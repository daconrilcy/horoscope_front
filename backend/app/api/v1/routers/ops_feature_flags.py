from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagListData,
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/ops/feature-flags", tags=["ops-feature-flags"])


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class FeatureFlagListApiResponse(BaseModel):
    data: FeatureFlagListData
    meta: ResponseMeta


class FeatureFlagApiResponse(BaseModel):
    data: FeatureFlagData
    meta: ResponseMeta


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
    if user.role != "ops":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops", "actual_role": user.role},
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


@router.get(
    "",
    response_model=FeatureFlagListApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def list_feature_flags(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="list")
    if limit_error is not None:
        return limit_error
    data = FeatureFlagService.list_flags(db)
    return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.put(
    "/{flag_key}",
    response_model=FeatureFlagApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def update_feature_flag(
    flag_key: str,
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="update")
    if limit_error is not None:
        return limit_error
    try:
        parsed = FeatureFlagUpdatePayload.model_validate(payload)
        data = FeatureFlagService.update_flag(
            db,
            key=flag_key,
            payload=parsed,
            updated_by_user_id=current_user.id,
        )
        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="ops_feature_flag_update",
            target_id=data.key,
            status="success",
            details={
                "enabled": data.enabled,
                "target_roles": data.target_roles,
                "target_user_ids": data.target_user_ids,
            },
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_feature_flag_request",
            message="feature flag request validation failed",
            details={"errors": error.errors()},
        )
    except FeatureFlagServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor=current_user,
                action="ops_feature_flag_update",
                target_id=flag_key,
                status="failed",
                details={"error_code": error.code},
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            return _error_response(
                status_code=503,
                request_id=request_id,
                code="audit_unavailable",
                message="audit service is unavailable",
                details={},
            )
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
