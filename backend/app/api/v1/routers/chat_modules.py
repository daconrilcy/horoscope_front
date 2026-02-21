from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.feature_flag_service import (
    FeatureFlagService,
    FeatureFlagServiceError,
    ModuleAvailabilityListData,
    ModuleExecutionData,
    ModuleExecutionPayload,
)
from app.services.quota_service import QuotaService, QuotaServiceError

router = APIRouter(prefix="/v1/chat/modules", tags=["chat-modules"])


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class ModuleAvailabilityApiResponse(BaseModel):
    data: ModuleAvailabilityListData
    meta: ResponseMeta


class ModuleExecutionApiResponse(BaseModel):
    data: ModuleExecutionData
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


def _ensure_user_role(current_user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if current_user.role != "user":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "user", "actual_role": current_user.role},
        )
    return None


@router.get(
    "/availability",
    response_model=ModuleAvailabilityApiResponse,
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def get_module_availability(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    data = FeatureFlagService.list_modules_availability(
        db,
        user_id=current_user.id,
        user_role=current_user.role,
    )
    return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}


@router.post(
    "/{module_key}/execute",
    response_model=ModuleExecutionApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def execute_module(
    module_key: str,
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    try:
        parsed = ModuleExecutionPayload.model_validate(payload)
        availability = FeatureFlagService.get_module_availability(
            db,
            module=module_key,
            user_id=current_user.id,
            user_role=current_user.role,
        )
        if not availability.available:
            increment_counter(
                f"module_errors_total|module={module_key.strip().lower()}|code=module_locked",
                1.0,
            )
            return _error_response(
                status_code=403,
                request_id=request_id,
                code="module_locked",
                message="module is not available for this user",
                details={"module": module_key.strip().lower(), "reason": availability.reason},
            )
        QuotaService.consume_quota_or_raise(
            db,
            user_id=current_user.id,
            request_id=request_id,
        )
        data = FeatureFlagService.execute_module(
            db,
            module=module_key,
            user_id=current_user.id,
            user_role=current_user.role,
            payload=parsed,
            skip_availability_check=True,
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_module_request",
            message="module request validation failed",
            details={"errors": error.errors()},
        )
    except QuotaServiceError as error:
        db.rollback()
        status_code = 429 if error.code == "quota_exceeded" else 403
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except FeatureFlagServiceError as error:
        db.rollback()
        if error.code in {
            "module_not_supported",
            "conversation_not_found",
            "feature_flag_not_found",
        }:
            status_code = 404
        elif error.code in {"module_locked", "conversation_forbidden"}:
            status_code = 403
        else:
            status_code = 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
