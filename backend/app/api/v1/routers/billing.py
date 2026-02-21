from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService
from app.services.billing_service import (
    BillingService,
    BillingServiceError,
    CheckoutData,
    CheckoutPayload,
    PlanChangeData,
    PlanChangePayload,
    SubscriptionStatusData,
)
from app.services.pricing_experiment_service import (
    PricingExperimentService,
    PricingExperimentServiceError,
)
from app.services.quota_service import QuotaService, QuotaServiceError, QuotaStatusData


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class SubscriptionApiResponse(BaseModel):
    data: SubscriptionStatusData
    meta: ResponseMeta


class CheckoutApiResponse(BaseModel):
    data: CheckoutData
    meta: ResponseMeta


class PlanChangeApiResponse(BaseModel):
    data: PlanChangeData
    meta: ResponseMeta


class QuotaApiResponse(BaseModel):
    data: QuotaStatusData
    meta: ResponseMeta


class CheckoutRequest(BaseModel):
    plan_code: str = "basic-entry"
    payment_method_token: str = "pm_card_ok"
    idempotency_key: str | None = None


class PlanChangeRequest(BaseModel):
    target_plan_code: str
    idempotency_key: str | None = None


router = APIRouter(prefix="/v1/billing", tags=["billing"])
logger = logging.getLogger(__name__)


class AuditWriteError(Exception):
    pass


def _record_pricing_event_safely(
    *,
    db: Session,
    request_id: str,
    action: str,
    details: dict[str, object],
) -> None:
    try:
        event = None
        if action == "offer_exposure":
            event = PricingExperimentService.record_offer_exposure(
                user_id=int(details["user_id"]),
                user_role=str(details["user_role"]),
                plan_code=str(details["plan_code"]),
                request_id=request_id,
            )
        elif action == "offer_conversion":
            event = PricingExperimentService.record_offer_conversion(
                user_id=int(details["user_id"]),
                user_role=str(details["user_role"]),
                plan_code=str(details["plan_code"]),
                conversion_type=str(details["conversion_type"]),
                conversion_status=str(details["conversion_status"]),
                request_id=request_id,
            )
        elif action == "offer_revenue":
            event = PricingExperimentService.record_offer_revenue(
                user_id=int(details["user_id"]),
                user_role=str(details["user_role"]),
                plan_code=str(details["plan_code"]),
                revenue_cents=int(details["revenue_cents"]),
                request_id=request_id,
            )
        elif action == "offer_retention":
            event = PricingExperimentService.record_retention_usage(
                user_id=int(details["user_id"]),
                user_role=str(details["user_role"]),
                plan_code=str(details["plan_code"]),
                retention_event=str(details["retention_event"]),
                request_id=request_id,
            )

        if event is None:
            return

        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=int(details["user_id"]),
                actor_role=str(details["user_role"]),
                action="pricing_experiment_event",
                target_type="pricing_experiment",
                target_id=event.variant_id,
                status="success",
                details=event.model_dump(mode="json"),
            ),
        )
    except PricingExperimentServiceError as error:
        logger.warning(
            "pricing_experiment_event_rejected action=%s request_id=%s code=%s details=%s",
            action,
            request_id,
            error.code,
            error.details,
        )
    except Exception:
        logger.exception(
            "pricing_experiment_event_failed action=%s request_id=%s",
            action,
            request_id,
        )


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _ensure_user_role(current_user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if current_user.role != "user":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed for billing subscription",
            details={"required_role": "user", "actual_role": current_user.role},
        )
    return None


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: dict[str, object] | None = None,
) -> None:
    try:
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                action=action,
                target_type=target_type,
                target_id=target_id,
                status=status,
                details=details or {},
            ),
        )
    except Exception as error:
        logger.exception("audit_event_write_failed action=%s request_id=%s", action, request_id)
        raise AuditWriteError("audit event write failed") from error


def _audit_unavailable_response(*, request_id: str) -> JSONResponse:
    return _error_response(
        status_code=503,
        request_id=request_id,
        code="audit_unavailable",
        message="audit persistence is unavailable",
        details={},
    )


def _enforce_billing_limits(
    *,
    user_id: int,
    plan_code: str | None,
    operation: str,
    request_id: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"billing:global:{operation}", limit=300, window_seconds=60)
        check_rate_limit(key=f"billing:user:{user_id}:{operation}", limit=60, window_seconds=60)
        if plan_code is not None:
            check_rate_limit(
                key=f"billing:user_plan:{user_id}:{plan_code}:{operation}",
                limit=30,
                window_seconds=60,
            )
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


@router.get(
    "/subscription",
    response_model=SubscriptionApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def get_subscription_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_billing_limits(
        user_id=current_user.id,
        plan_code=None,
        operation="get_subscription",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    if subscription.plan is not None:
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_retention",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": subscription.plan.code,
                "retention_event": "subscription_status_view",
            },
        )
        db.commit()
    return {"data": subscription.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.get(
    "/quota",
    response_model=QuotaApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def get_quota_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    plan_code = subscription.plan.code if subscription.plan is not None else "no-plan"
    rate_error = _enforce_billing_limits(
        user_id=current_user.id,
        plan_code=plan_code,
        operation="get_quota",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        quota = QuotaService.get_quota_status(
            db,
            user_id=current_user.id,
            subscription=subscription,
        )
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_retention",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": plan_code,
                "retention_event": "quota_status_view",
            },
        )
        db.commit()
        return {"data": quota.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except QuotaServiceError as error:
        status_code = 403 if error.code == "no_active_subscription" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/checkout",
    response_model=CheckoutApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def create_checkout(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    try:
        parsed = CheckoutRequest.model_validate(payload)
        rate_error = _enforce_billing_limits(
            user_id=current_user.id,
            plan_code=parsed.plan_code,
            operation="checkout",
            request_id=request_id,
        )
        if rate_error is not None:
            return rate_error
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_exposure",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code,
            },
        )
        request_payload = CheckoutPayload(
            plan_code=parsed.plan_code,
            payment_method_token=parsed.payment_method_token,
            idempotency_key=parsed.idempotency_key or uuid4().hex,
        )
        result = BillingService.create_checkout(
            db,
            user_id=current_user.id,
            payload=request_payload,
            request_id=request_id,
        )
        conversion_status = "success" if result.payment_status == "succeeded" else "failed"
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code,
                "conversion_type": "checkout",
                "conversion_status": conversion_status,
            },
        )
        if conversion_status == "success" and result.subscription.plan is not None:
            _record_pricing_event_safely(
                db=db,
                request_id=request_id,
                action="offer_revenue",
                details={
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "plan_code": result.subscription.plan.code,
                    "revenue_cents": result.subscription.plan.monthly_price_cents,
                },
            )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="billing_checkout",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
            details={"plan_code": parsed.plan_code},
        )
        db.commit()
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_checkout",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": "invalid_checkout_request"},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_checkout_request",
            message="checkout request validation failed",
            details={"errors": error.errors()},
        )
    except BillingServiceError as error:
        db.rollback()
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code if "parsed" in locals() else "unknown",
                "conversion_type": "checkout",
                "conversion_status": "failed",
            },
        )
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_checkout",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        status_code = 409 if error.code == "subscription_already_active" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)


@router.post(
    "/retry",
    response_model=CheckoutApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def retry_checkout(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    try:
        parsed = CheckoutRequest.model_validate(payload)
        rate_error = _enforce_billing_limits(
            user_id=current_user.id,
            plan_code=parsed.plan_code,
            operation="retry",
            request_id=request_id,
        )
        if rate_error is not None:
            return rate_error
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_exposure",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code,
            },
        )
        request_payload = CheckoutPayload(
            plan_code=parsed.plan_code,
            payment_method_token=parsed.payment_method_token,
            idempotency_key=parsed.idempotency_key or uuid4().hex,
        )
        result = BillingService.retry_checkout(
            db,
            user_id=current_user.id,
            payload=request_payload,
            request_id=request_id,
        )
        conversion_status = "success" if result.payment_status == "succeeded" else "failed"
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code,
                "conversion_type": "retry",
                "conversion_status": conversion_status,
            },
        )
        if conversion_status == "success" and result.subscription.plan is not None:
            _record_pricing_event_safely(
                db=db,
                request_id=request_id,
                action="offer_revenue",
                details={
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "plan_code": result.subscription.plan.code,
                    "revenue_cents": result.subscription.plan.monthly_price_cents,
                },
            )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="billing_retry_checkout",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
            details={"plan_code": parsed.plan_code},
        )
        db.commit()
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_retry_checkout",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": "invalid_checkout_request"},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_checkout_request",
            message="checkout request validation failed",
            details={"errors": error.errors()},
        )
    except BillingServiceError as error:
        db.rollback()
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.plan_code if "parsed" in locals() else "unknown",
                "conversion_type": "retry",
                "conversion_status": "failed",
            },
        )
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_retry_checkout",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        status_code = 409 if error.code == "subscription_already_active" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)


@router.post(
    "/plan-change",
    response_model=PlanChangeApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def change_plan(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    try:
        parsed = PlanChangeRequest.model_validate(payload)
        rate_error = _enforce_billing_limits(
            user_id=current_user.id,
            plan_code=parsed.target_plan_code,
            operation="plan_change",
            request_id=request_id,
        )
        if rate_error is not None:
            return rate_error
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_exposure",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.target_plan_code,
            },
        )
        request_payload = PlanChangePayload(
            target_plan_code=parsed.target_plan_code,
            idempotency_key=parsed.idempotency_key or uuid4().hex,
        )
        result = BillingService.change_subscription_plan(
            db,
            user_id=current_user.id,
            payload=request_payload,
            request_id=request_id,
        )
        conversion_status = "success" if result.plan_change_status == "succeeded" else "failed"
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": result.target_plan_code,
                "conversion_type": "plan_change",
                "conversion_status": conversion_status,
            },
        )
        if conversion_status == "success" and result.subscription.plan is not None:
            _record_pricing_event_safely(
                db=db,
                request_id=request_id,
                action="offer_revenue",
                details={
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "plan_code": result.subscription.plan.code,
                    "revenue_cents": result.subscription.plan.monthly_price_cents,
                },
            )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="billing_plan_change",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
            details={"target_plan_code": parsed.target_plan_code},
        )
        db.commit()
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_plan_change",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": "invalid_plan_change_request"},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_plan_change_request",
            message="plan change request validation failed",
            details={"errors": error.errors()},
        )
    except BillingServiceError as error:
        db.rollback()
        _record_pricing_event_safely(
            db=db,
            request_id=request_id,
            action="offer_conversion",
            details={
                "user_id": current_user.id,
                "user_role": current_user.role,
                "plan_code": parsed.target_plan_code if "parsed" in locals() else "unknown",
                "conversion_type": "plan_change",
                "conversion_status": "failed",
            },
        )
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="billing_plan_change",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        status_code = (
            409 if error.code in {"duplicate_plan_change", "plan_change_not_allowed"} else 422
        )
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)



