"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
)
from app.api.v1.errors import api_error_response
from app.core.rate_limit import check_rate_limit
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _enforce_enterprise_limits(*, client: AuthenticatedEnterpriseClient, operation: str) -> None:
    check_rate_limit(key=f"b2b_billing:global:{operation}", limit=180, window_seconds=60)
    check_rate_limit(
        key=f"b2b_billing:account:{client.account_id}:{operation}",
        limit=90,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_billing:credential:{client.credential_id}:{operation}",
        limit=45,
        window_seconds=60,
    )


def _enforce_ops_limits(*, user: AuthenticatedUser, operation: str) -> None:
    check_rate_limit(key=f"b2b_billing_ops:global:{operation}", limit=120, window_seconds=60)
    check_rate_limit(
        key=f"b2b_billing_ops:role:{user.role}:{operation}", limit=60, window_seconds=60
    )
    check_rate_limit(key=f"b2b_billing_ops:user:{user.id}:{operation}", limit=30, window_seconds=60)


def _record_billing_audit(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            target_type="enterprise_billing_cycle",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _ensure_ops_role(*, user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in ["ops", "admin"]:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None
