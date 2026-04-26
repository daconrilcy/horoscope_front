"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/ops/feature-flags", tags=["ops-feature-flags"])
from app.api.v1.schemas.routers.ops.feature_flags import *


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


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in ["ops", "admin"]:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"ops_feature_flags:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"ops_feature_flags:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(
            key=f"ops_feature_flags:user:{user.id}:{operation}", limit=30, window_seconds=60
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


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_type="feature_flag",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )
