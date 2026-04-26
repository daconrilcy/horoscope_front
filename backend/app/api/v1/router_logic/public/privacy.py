"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/privacy", tags=["privacy"])
logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.public.privacy import *


class AuditWriteError(Exception):
    """Signale une indisponibilite de l'audit technique."""


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
            message="role is not allowed for privacy requests",
            details={"required_role": "user, admin", "actual_role": current_user.role},
        )
    return None


def _ensure_support_or_ops_role(
    current_user: AuthenticatedUser, request_id: str
) -> JSONResponse | None:
    if current_user.role not in {"support", "ops", "admin"}:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed for privacy evidence",
            details={"required_roles": "support,ops,admin", "actual_role": current_user.role},
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


def _record_failed_audit_or_503(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    error_code: str,
) -> JSONResponse | None:
    try:
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            status="failed",
            details={"error_code": error_code},
        )
        db.commit()
    except AuditWriteError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit persistence is unavailable",
            details={},
        )
    return None


def _enforce_privacy_limits(
    *,
    user_id: int,
    plan_code: str | None,
    operation: str,
    request_id: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"privacy:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(key=f"privacy:user:{user_id}:{operation}", limit=20, window_seconds=60)
        if plan_code is not None:
            check_rate_limit(
                key=f"privacy:user_plan:{user_id}:{plan_code}:{operation}",
                limit=10,
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
