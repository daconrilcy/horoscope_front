from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.ops.feature_flags import (
    FeatureFlagApiResponse,
    FeatureFlagListApiResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.api_feature_flags import (
    _enforce_limits,
    _ensure_ops_role,
    _error_response,
    _record_audit_event,
)
from app.services.ops.audit_service import AuditServiceError
from app.services.ops.feature_flag_service import (
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/ops/feature-flags", tags=["ops-feature-flags"])


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
