"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.reference_data_service import ReferenceDataServiceError


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


def _record_reference_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    target_id: str | None,
    status_value: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="ops",
            action=action,
            target_type="reference_version",
            target_id=target_id,
            status=status_value,
            details=details,
        ),
    )


def _can_use_seed_token() -> bool:
    return settings.app_env in {
        "development",
        "dev",
        "local",
        "test",
        "testing",
    }


def _validate_seed_access(
    x_admin_token: str | None,
    current_user: AuthenticatedUser | None,
) -> ReferenceDataServiceError | None:
    if current_user is not None and current_user.role in {"ops", "admin"}:
        return None
    if current_user is not None and current_user.role not in {"ops", "admin"}:
        return ReferenceDataServiceError(
            code="insufficient_role",
            message="role is not allowed",
            details={"required_role": "ops, admin", "actual_role": current_user.role},
        )
    if _can_use_seed_token() and x_admin_token == settings.reference_seed_admin_token:
        return None
    return ReferenceDataServiceError(
        code="unauthorized_seed_access",
        message="invalid admin token",
        details={},
    )
