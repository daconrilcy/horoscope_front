from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.config import settings
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService
from app.services.billing_service import (
    BillingPlanData,
    BillingService,
    SubscriptionStatusData,
    TokenUsageData,
)
from app.services.pricing_experiment_service import (
    PricingExperimentService,
    PricingExperimentServiceError,
)
from app.services.stripe_checkout_service import (
    StripeCheckoutService,
    StripeCheckoutServiceError,
)
from app.services.stripe_customer_portal_service import (
    StripeCustomerPortalService,
    StripeCustomerPortalServiceError,
)
from app.services.stripe_webhook_service import (
    StripeWebhookService,
    StripeWebhookServiceError,
)


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


class BillingPlansApiResponse(BaseModel):
    data: list[BillingPlanData]
    meta: ResponseMeta


class StripeCheckoutRequest(BaseModel):
    plan: Literal["basic", "premium"]


class StripeSubscriptionUpgradeRequest(BaseModel):
    plan: Literal["basic", "premium"]


class StripeCheckoutResponse(BaseModel):
    checkout_url: str


class StripeCheckoutApiResponse(BaseModel):
    data: StripeCheckoutResponse
    meta: ResponseMeta


class StripePortalResponse(BaseModel):
    url: str


class StripePortalApiResponse(BaseModel):
    data: StripePortalResponse
    meta: ResponseMeta


class StripeSubscriptionStatusApiResponse(BaseModel):
    data: SubscriptionStatusData
    meta: ResponseMeta


class StripeSubscriptionUpgradeResponse(BaseModel):
    checkout_url: str | None
    invoice_status: str | None
    amount_due_cents: int
    currency: str | None


class StripeSubscriptionUpgradeApiResponse(BaseModel):
    data: StripeSubscriptionUpgradeResponse
    meta: ResponseMeta


class TokenUsageApiResponse(BaseModel):
    data: TokenUsageData
    meta: ResponseMeta


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
    if current_user.role not in {"user", "admin"}:
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


def _resolve_portal_service_status_code(error_code: str) -> int:
    return {
        "stripe_billing_profile_not_found": 404,
        "stripe_subscription_not_found": 404,
        "stripe_unavailable": 503,
        "stripe_portal_configuration_missing": 503,
        "stripe_portal_subscription_update_not_allowed_for_trial": 422,
        "stripe_portal_subscription_update_disabled": 422,
        "stripe_portal_subscription_update_no_change_options": 422,
        "stripe_portal_subscription_cancel_disabled": 422,
        "stripe_portal_subscription_cancel_already_scheduled": 422,
        "stripe_subscription_reactivation_not_needed": 422,
        "stripe_subscription_upgrade_not_allowed": 422,
        "stripe_subscription_upgrade_invalid_proration_preview": 502,
        "stripe_subscription_upgrade_payment_not_completed": 422,
        "stripe_subscription_upgrade_checkout_metadata_missing": 502,
        "stripe_subscription_upgrade_checkout_customer_mismatch": 502,
        "plan_price_not_configured": 503,
        "stripe_api_error": 502,
    }.get(error_code, 500)


def _create_stripe_subscription_flow_session_response(
    *,
    request: Request,
    current_user: AuthenticatedUser,
    db: Session,
    operation: str,
    success_action: str,
    failure_action: str,
    session_factory: Any,
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error

    rate_error = _enforce_billing_limits(
        user_id=current_user.id,
        plan_code=None,
        operation=operation,
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    try:
        portal_url = session_factory()
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=success_action,
            target_type="user",
            target_id=str(current_user.id),
            status="success",
        )
        db.commit()
        return {"data": {"url": portal_url}, "meta": {"request_id": request_id}}

    except StripeCustomerPortalServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action=failure_action,
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=_resolve_portal_service_status_code(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)


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
    "/plans",
    response_model=BillingPlansApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def list_billing_plans(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error

    plans = db.scalars(
        select(BillingPlanModel).where(
            BillingPlanModel.is_active,
            BillingPlanModel.is_visible_to_users,
        )
    ).all()

    return {
        "data": [BillingService._to_plan_data(p).model_dump(mode="json") for p in plans],
        "meta": {"request_id": request_id},
    }


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
    "/token-usage",
    response_model=TokenUsageApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def get_token_usage(
    request: Request,
    period: str = "current_month",
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
        operation="get_token_usage",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    usage = BillingService.get_token_usage(db, user_id=current_user.id, period=period)
    return {"data": usage.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.post(
    "/stripe-checkout-session",
    response_model=StripeCheckoutApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def create_stripe_checkout_session(
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
        parsed = StripeCheckoutRequest.model_validate(payload)
        rate_error = _enforce_billing_limits(
            user_id=current_user.id,
            plan_code=parsed.plan,
            operation="stripe_checkout",
            request_id=request_id,
        )
        if rate_error is not None:
            return rate_error

        checkout_url = StripeCheckoutService.create_checkout_session(
            db,
            user_id=current_user.id,
            user_email=current_user.email,
            plan=parsed.plan,
            success_url=settings.stripe_checkout_success_url,
            cancel_url=settings.stripe_checkout_cancel_url,
            billing_address_collection=settings.stripe_checkout_billing_address_collection,
            automatic_tax_enabled=settings.stripe_tax_enabled,
            tax_id_collection_enabled=settings.stripe_tax_id_collection_enabled,
            trial_enabled=settings.stripe_trial_enabled,
            trial_period_days=settings.stripe_trial_period_days,
            payment_method_collection=settings.stripe_payment_method_collection,
            missing_payment_method_behavior=settings.stripe_trial_missing_payment_method_behavior,
        )

        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="stripe_checkout_session_created",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
            details={
                "plan": parsed.plan,
                "automatic_tax_enabled": settings.stripe_tax_enabled,
                "tax_id_collection_enabled": settings.stripe_tax_id_collection_enabled,
                "trial_enabled": settings.stripe_trial_enabled,
                "trial_period_days": settings.stripe_trial_period_days,
                "payment_method_collection": settings.stripe_payment_method_collection,
                "missing_payment_method_behavior": (
                    settings.stripe_trial_missing_payment_method_behavior
                ),
            },
        )
        db.commit()
        return {
            "data": {"checkout_url": checkout_url},
            "meta": {"request_id": request_id},
        }

    except ValidationError as error:
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="stripe_checkout_session_failed",
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
            message="request validation failed",
            details={"errors": error.errors()},
        )
    except StripeCheckoutServiceError as error:
        db.rollback()
        status_code = 422
        if error.code == "stripe_unavailable":
            status_code = 503
        elif error.code == "stripe_api_error":
            status_code = 502
        elif error.code in {"plan_price_not_configured", "invalid_checkout_request"}:
            status_code = 422

        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="stripe_checkout_session_failed",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)

        db.commit()
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
    "/stripe-customer-portal-session",
    response_model=StripePortalApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def create_stripe_customer_portal_session(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error

    try:
        rate_error = _enforce_billing_limits(
            user_id=current_user.id,
            plan_code=None,
            operation="stripe_portal_session",
            request_id=request_id,
        )
        if rate_error is not None:
            return rate_error

        portal_url = StripeCustomerPortalService.create_portal_session(
            db,
            user_id=current_user.id,
            return_url=settings.stripe_portal_return_url,
            configuration_id=settings.stripe_portal_configuration_id,
        )

        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="stripe_portal_session_created",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
        )
        db.commit()
        return {
            "data": {"url": portal_url},
            "meta": {"request_id": request_id},
        }

    except StripeCustomerPortalServiceError as error:
        db.rollback()
        status_code = _resolve_portal_service_status_code(error.code)

        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="stripe_portal_session_failed",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)

        db.commit()
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
    "/stripe-customer-portal-subscription-update-session",
    response_model=StripePortalApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def create_stripe_portal_subscription_update_session(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    return _create_stripe_subscription_flow_session_response(
        request=request,
        current_user=current_user,
        db=db,
        operation="stripe_portal_subscription_update_session",
        success_action="stripe_portal_subscription_update_session_created",
        failure_action="stripe_portal_subscription_update_session_failed",
        session_factory=lambda: StripeCustomerPortalService.create_subscription_update_session(
            db,
            user_id=current_user.id,
            return_url=settings.stripe_portal_return_url,
            configuration_id=settings.stripe_portal_configuration_id,
        ),
    )


@router.post(
    "/stripe-customer-portal-subscription-cancel-session",
    response_model=StripePortalApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def create_stripe_portal_subscription_cancel_session(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    return _create_stripe_subscription_flow_session_response(
        request=request,
        current_user=current_user,
        db=db,
        operation="stripe_portal_subscription_cancel_session",
        success_action="stripe_portal_subscription_cancel_session_created",
        failure_action="stripe_portal_subscription_cancel_session_failed",
        session_factory=lambda: StripeCustomerPortalService.create_subscription_cancel_session(
            db,
            user_id=current_user.id,
            return_url=settings.stripe_portal_return_url,
            configuration_id=settings.stripe_portal_configuration_id,
        ),
    )


@router.post(
    "/stripe-subscription-reactivate",
    response_model=StripeSubscriptionStatusApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def reactivate_stripe_subscription(
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
        operation="stripe_subscription_reactivate",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    try:
        profile = StripeCustomerPortalService.reactivate_subscription(
            db,
            user_id=current_user.id,
        )
        subscription = BillingService._to_stripe_subscription_data(db, profile=profile)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="stripe_subscription_reactivated",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
        )
        db.commit()
        return {"data": subscription.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except StripeCustomerPortalServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="stripe_subscription_reactivation_failed",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=_resolve_portal_service_status_code(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)


@router.post(
    "/stripe-subscription-upgrade",
    response_model=StripeSubscriptionUpgradeApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
    },
)
def create_stripe_subscription_upgrade_payment(
    request: Request,
    payload: StripeSubscriptionUpgradeRequest = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error

    rate_error = _enforce_billing_limits(
        user_id=current_user.id,
        plan_code=payload.plan,
        operation="stripe_subscription_upgrade",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error

    try:
        upgrade_result = StripeCustomerPortalService.create_subscription_upgrade_payment(
            db,
            user_id=current_user.id,
            target_plan=payload.plan,
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="stripe_subscription_upgrade_payment_created",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
            details={
                "target_plan": payload.plan,
                "amount_due_cents": upgrade_result.amount_due_cents,
                "invoice_status": upgrade_result.invoice_status,
            },
        )
        db.commit()
        return {
            "data": {
                "checkout_url": upgrade_result.checkout_url,
                "invoice_status": upgrade_result.invoice_status,
                "amount_due_cents": upgrade_result.amount_due_cents,
                "currency": upgrade_result.currency,
            },
            "meta": {"request_id": request_id},
        }
    except StripeCustomerPortalServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=int(current_user.id),
                actor_role=str(current_user.role),
                action="stripe_subscription_upgrade_payment_failed",
                target_type="user",
                target_id=str(current_user.id),
                status="failed",
                details={"error_code": error.code, "target_plan": payload.plan},
            )
        except AuditWriteError:
            db.rollback()
            return _audit_unavailable_response(request_id=request_id)
        db.commit()
        return _error_response(
            status_code=_resolve_portal_service_status_code(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _audit_unavailable_response(request_id=request_id)


@router.post(
    "/stripe-webhook",
    responses={
        400: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Endpoint de réception des webhooks Stripe.
    Vérifie la signature et délègue le traitement au service.
    """
    request_id = resolve_request_id(request)
    payload_bytes = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        logger.error("stripe_webhook: STRIPE_WEBHOOK_SECRET is not configured")
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="webhook_secret_not_configured",
            message="Stripe webhook secret is not configured on server",
            details={},
        )

    try:
        event = StripeWebhookService.verify_and_parse(
            payload_bytes, sig_header, settings.stripe_webhook_secret
        )

        # 1. Traitement métier (prioritaire)
        status = StripeWebhookService.handle_event(db, event)
        db.commit()

        # 2. Audit (best-effort, ne doit pas bloquer le retour 200 à Stripe)
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=None,
                actor_role="system",
                action="stripe_webhook_processed",
                target_type="stripe_event",
                target_id=event.id,
                status="success",
                details={
                    "type": event.type,
                    "event_id": event.id,
                    "outcome": status,
                },
            )
            db.commit()
        except Exception:
            logger.exception("stripe_webhook: best-effort audit failed (non-blocking)")
            db.rollback()

        return {"status": status}

    except StripeWebhookServiceError as error:
        db.rollback()
        if error.code == "invalid_signature":
            return _error_response(
                status_code=400,
                request_id=request_id,
                code="invalid_signature",
                message=error.message,
                details={},
            )
        # Autres erreurs de service (ex: parsing) -> 200 pour éviter retry inutile
        logger.warning("stripe_webhook: non-fatal service error: %s", error.message)
        return {"status": "error_non_fatal", "code": error.code}

    except Exception:
        db.rollback()
        logger.exception("stripe_webhook: unexpected internal error")
        # On retourne 200 même ici selon AC3 pour éviter les retries Stripe
        # sur des erreurs applicatives après signature valide.
        return {"status": "failed_internal"}
