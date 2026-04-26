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

router = APIRouter(prefix="/v1/b2b/credentials", tags=["b2b-credentials"])
from app.api.v1.schemas.routers.public.enterprise_credentials import *


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


def _ensure_enterprise_admin_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in {"enterprise_admin", "admin"}:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "enterprise_admin, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_credentials:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"b2b_credentials:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(
            key=f"b2b_credentials:user:{user.id}:{operation}", limit=30, window_seconds=60
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
    actor_user_id: int,
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
            target_type="enterprise_api_credential",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )
