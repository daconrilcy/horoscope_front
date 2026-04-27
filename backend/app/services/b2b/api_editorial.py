"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedEnterpriseClient
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


def _enforce_limits(*, client: AuthenticatedEnterpriseClient, operation: str) -> None:
    check_rate_limit(key=f"b2b_editorial:global:{operation}", limit=180, window_seconds=60)
    check_rate_limit(
        key=f"b2b_editorial:account:{client.account_id}:{operation}",
        limit=90,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_editorial:credential:{client.credential_id}:{operation}",
        limit=45,
        window_seconds=60,
    )


def _record_editorial_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action=action,
            target_type="enterprise_editorial_config",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _sanitize_validation_errors(error: ValidationError) -> list[dict[str, object]]:
    sanitized: list[dict[str, object]] = []
    for item in error.errors():
        sanitized.append(
            {
                "loc": [str(part) for part in item.get("loc", ())],
                "msg": str(item.get("msg", "")),
                "type": str(item.get("type", "")),
            }
        )
    return sanitized
