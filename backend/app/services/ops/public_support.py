"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.infra.db.models.audit_event import AuditEventModel
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.public.support import SupportAuditEventSummary


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


def _ensure_support_role(user: AuthenticatedUser, request_id: str) -> Any | None:
    if user.role not in {"support", "ops", "admin"}:
        return _raise_error(
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "support,ops,admin", "actual_role": user.role},
        )
    return None


def _enforce_support_limits(
    *,
    role: str,
    user_id: int,
    operation: str,
    request_id: str,
) -> Any | None:
    try:
        check_rate_limit(key=f"support:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(key=f"support:role:{role}:{operation}", limit=60, window_seconds=60)
        check_rate_limit(key=f"support:user:{user_id}:{operation}", limit=30, window_seconds=60)
    except RateLimitError as error:
        return _raise_error(
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    try:
        transaction = db.begin_nested() if db.in_transaction() else db.begin()
        with transaction:
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
                    details=details,
                ),
            )
    except Exception:
        logger.exception(
            "audit_event_write_failed action=%s request_id=%s target_type=%s target_id=%s",
            action,
            request_id,
            target_type,
            target_id or "",
        )


def _recent_audit_events_for_user(
    db: Session, *, user_id: int, incident_ids: list[int]
) -> list[SupportAuditEventSummary]:
    user_rows = db.scalars(
        select(AuditEventModel).where(
            (AuditEventModel.target_type == "user") & (AuditEventModel.target_id == str(user_id))
        )
    ).all()
    incident_rows: list[AuditEventModel] = []
    if incident_ids:
        incident_rows = db.scalars(
            select(AuditEventModel).where(
                (AuditEventModel.target_type == "incident")
                & (AuditEventModel.target_id.in_([str(item) for item in incident_ids]))
            )
        ).all()
    rows = sorted(
        [*user_rows, *incident_rows],
        key=lambda item: (item.created_at, item.id),
        reverse=True,
    )[:20]
    return [
        SupportAuditEventSummary(
            event_id=row.id,
            action=row.action,
            status=row.status,
            target_type=row.target_type,
            target_id=row.target_id,
            created_at=row.created_at,
        )
        for row in rows
    ]
