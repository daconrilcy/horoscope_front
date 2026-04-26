"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigData,
    PersonaConfigServiceError,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/ops/persona", tags=["ops-persona"])
from app.api.v1.schemas.routers.ops.persona import *


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


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"ops_persona:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"ops_persona:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(key=f"ops_persona:user:{user.id}:{operation}", limit=30, window_seconds=60)
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
            target_type="persona_config",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _audit_failure_or_503(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    error_code: str,
) -> JSONResponse | None:
    try:
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_id=None,
            status="failed",
            details={"error_code": error_code},
        )
        db.commit()
    except Exception:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
    return None


def _persona_profile_mutation(
    *,
    request: Request,
    profile_id: int,
    operation: str,
    action: str,
    service_call: Callable[..., PersonaConfigData],
    current_user: AuthenticatedUser,
    db: Session,
) -> Any:
    request_id = resolve_request_id(request)
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation=operation)
    if limit_error is not None:
        return limit_error
    try:
        response = service_call(db=db, user_id=current_user.id, profile_id=profile_id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=action,
            target_id=str(response.id) if response.id is not None else None,
            status="success",
            details={"version": response.version, "profile_code": response.profile_code},
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PersonaConfigServiceError as error:
        db.rollback()
        audit_error = _audit_failure_or_503(
            db,
            request_id=request_id,
            actor=current_user,
            action=action,
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
