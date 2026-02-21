from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops_monitoring_service import (
    OpsMonitoringKpisData,
    OpsMonitoringOperationalSummaryData,
    OpsMonitoringPersonaKpisData,
    OpsMonitoringPricingKpisData,
    OpsMonitoringService,
    OpsMonitoringServiceError,
)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class OpsMonitoringApiResponse(BaseModel):
    data: OpsMonitoringKpisData
    meta: ResponseMeta


class OpsMonitoringOperationalSummaryApiResponse(BaseModel):
    data: OpsMonitoringOperationalSummaryData
    meta: ResponseMeta


class OpsMonitoringPersonaKpisApiResponse(BaseModel):
    data: OpsMonitoringPersonaKpisData
    meta: ResponseMeta


class OpsMonitoringPricingKpisApiResponse(BaseModel):
    data: OpsMonitoringPricingKpisData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/ops/monitoring", tags=["ops-monitoring"])


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
        check_rate_limit(key=f"ops_monitoring:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"ops_monitoring:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(
            key=f"ops_monitoring:user:{user.id}:{operation}", limit=30, window_seconds=60
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


@router.get(
    "/conversation-kpis",
    response_model=OpsMonitoringApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_conversation_kpis(
    request: Request,
    window: str = Query(default="24h"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="conversation_kpis"
    )
    if limit_error is not None:
        return limit_error
    try:
        data = OpsMonitoringService.get_conversation_kpis(window=window)
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except OpsMonitoringServiceError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/operational-summary",
    response_model=OpsMonitoringOperationalSummaryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_operational_summary(
    request: Request,
    window: str = Query(default="24h"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="operational_summary"
    )
    if limit_error is not None:
        return limit_error
    try:
        data = OpsMonitoringService.get_operational_summary(window=window)
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except OpsMonitoringServiceError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/persona-kpis",
    response_model=OpsMonitoringPersonaKpisApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_persona_kpis(
    request: Request,
    window: str = Query(default="24h"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="persona_kpis"
    )
    if limit_error is not None:
        return limit_error
    try:
        data = OpsMonitoringService.get_persona_kpis(window=window)
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except OpsMonitoringServiceError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/pricing-experiments-kpis",
    response_model=OpsMonitoringPricingKpisApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_pricing_experiment_kpis(
    request: Request,
    window: str = Query(default="24h"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="pricing_experiment_kpis"
    )
    if limit_error is not None:
        return limit_error
    try:
        data = OpsMonitoringService.get_pricing_experiment_kpis(window=window, db=db)
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except OpsMonitoringServiceError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
