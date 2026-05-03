"""Routeur public de facturation exposant les contrats HTTP billing."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import resolve_application_error_status
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.billing import (
    BillingPlansApiResponse,
    StripeCheckoutApiResponse,
    StripeCheckoutRequest,
    StripePortalApiResponse,
    StripeSubscriptionStatusApiResponse,
    StripeSubscriptionUpgradeApiResponse,
    StripeSubscriptionUpgradeRequest,
    SubscriptionApiResponse,
    TokenUsageApiResponse,
)
from app.services.billing.public_billing import (
    AuditWriteError,
    _audit_unavailable_response,
    _create_stripe_subscription_flow_session_response,
    _enforce_billing_limits,
    _ensure_user_role,
    _raise_error,
    _record_audit_event,
    _record_pricing_event_safely,
)
from app.services.billing.service import (
    BillingService,
)
from app.services.billing.stripe_checkout_service import (
    StripeCheckoutService,
    StripeCheckoutServiceError,
)
from app.services.billing.stripe_customer_portal_service import (
    StripeCustomerPortalService,
    StripeCustomerPortalServiceError,
)
from app.services.billing.stripe_webhook_service import (
    StripeWebhookService,
    StripeWebhookServiceError,
)

router = APIRouter(prefix="/v1/billing", tags=["billing"])
logger = logging.getLogger(__name__)


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
        return _raise_error(
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
        return _raise_error(
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
        status_code = resolve_application_error_status(error.code)

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
        return _raise_error(
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
    request_id = resolve_request_id(request)
    return _create_stripe_subscription_flow_session_response(
        request_id=request_id,
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
    request_id = resolve_request_id(request)
    return _create_stripe_subscription_flow_session_response(
        request_id=request_id,
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
        return _raise_error(
            status_code=resolve_application_error_status(error.code),
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
        return _raise_error(
            status_code=resolve_application_error_status(error.code),
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
        500: {"model": ErrorEnvelope},
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
        return _raise_error(
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
        if status == "failed_internal":
            logger.warning(
                "stripe_webhook: signed processing failed event_id=%s type=%s outcome=%s",
                event.id,
                event.type,
                status,
            )
            return _raise_error(
                status_code=500,
                request_id=request_id,
                code="stripe_webhook_processing_failed",
                message="Stripe webhook processing failed; delivery should be retried",
                details={"event_id": event.id, "event_type": event.type},
            )

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

    except ApplicationError:
        raise

    except StripeWebhookServiceError as error:
        db.rollback()
        if error.code == "invalid_signature":
            return _raise_error(
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
        return _raise_error(
            status_code=500,
            request_id=request_id,
            code="stripe_webhook_processing_failed",
            message="Stripe webhook processing failed; delivery should be retried",
            details={},
        )
