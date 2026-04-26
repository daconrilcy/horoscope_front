"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

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
) -> Any:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _enforce_limits(*, client: AuthenticatedEnterpriseClient, operation: str) -> None:
    check_rate_limit(key=f"b2b_usage:global:{operation}", limit=240, window_seconds=60)
    check_rate_limit(
        key=f"b2b_usage:account:{client.account_id}:{operation}",
        limit=120,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_usage:credential:{client.credential_id}:{operation}",
        limit=60,
        window_seconds=60,
    )


def _record_usage_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    status: str,
    account_id: int,
    credential_id: int,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action=action,
            target_type="enterprise_usage",
            target_id=str(credential_id),
            status=status,
            details={"account_id": account_id, **details},
        ),
    )
