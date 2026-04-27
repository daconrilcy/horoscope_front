"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.services.billing.pricing_experiment_service import (
    PricingExperimentService,
    PricingExperimentServiceError,
)
from app.services.billing.stripe_customer_portal_service import (
    StripeCustomerPortalServiceError,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)


class AuditWriteError(Exception):
    """Signale une indisponibilite de l'audit technique."""


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


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _ensure_user_role(current_user: AuthenticatedUser, request_id: str) -> Any | None:
    if current_user.role not in {"user", "admin"}:
        return _raise_error(
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


def _audit_unavailable_response(*, request_id: str) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code="audit_unavailable",
        message="audit persistence is unavailable",
        details={},
    )


def _create_stripe_subscription_flow_session_response(
    *,
    request_id: str,
    current_user: AuthenticatedUser,
    db: Session,
    operation: str,
    success_action: str,
    failure_action: str,
    session_factory: Any,
) -> Any:
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
        return _raise_error(
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
) -> Any | None:
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
        return _raise_error(
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
