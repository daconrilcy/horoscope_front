"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationError
from app.core.rbac import is_valid_role
from app.core.security import SecurityError, decode_token
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)


class AuditWriteError(Exception):
    """Signale une indisponibilite de l'audit technique."""


def _audit_unavailable_response(request_id: str) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code="audit_unavailable",
        message="audit persistence is unavailable",
        details={},
    )


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


def _resolve_refresh_actor(refresh_token: str) -> tuple[int | None, str]:
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except SecurityError:
        return None, "anonymous"
    subject = payload.get("sub")
    role = payload.get("role")
    actor_user_id = int(subject) if isinstance(subject, str) and subject.isdigit() else None
    actor_role = role if isinstance(role, str) and is_valid_role(role) else "anonymous"
    return actor_user_id, actor_role
