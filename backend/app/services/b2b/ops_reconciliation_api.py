"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.core.rate_limit import check_rate_limit
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService


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


def _ensure_ops_role(*, user: AuthenticatedUser, request_id: str) -> Any | None:
    if user.role not in ["ops", "admin"]:
        return _raise_error(
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(*, user: AuthenticatedUser, operation: str) -> None:
    check_rate_limit(key=f"b2b_reconciliation:global:{operation}", limit=120, window_seconds=60)
    check_rate_limit(
        key=f"b2b_reconciliation:role:{user.role}:{operation}",
        limit=60,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_reconciliation:user:{user.id}:{operation}",
        limit=30,
        window_seconds=60,
    )


def _record_reconciliation_audit(
    db: Session,
    *,
    request_id: str,
    user: AuthenticatedUser,
    action: str,
    status: str,
    target_id: str | None,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=user.id,
            actor_role=user.role,
            action=action,
            target_type="enterprise_billing_reconciliation",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )
