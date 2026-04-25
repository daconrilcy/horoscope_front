from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.domain.llm.runtime.contracts import PerformanceQualificationReport
from app.infra.db.session import get_db_session
from app.ops.llm.performance_qualification import PerformanceQualificationService
from app.services.ops.monitoring_service import (
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


class PerformanceQualificationRequest(BaseModel):
    family: str
    profile: str
    total_requests: int
    success_count: int
    protection_count: int
    error_count: int
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rps: float
    active_snapshot_id: Optional[uuid.UUID] = None
    active_snapshot_version: Optional[str] = None
    manifest_entry_id: Optional[str] = None
    environment: str = "local"


class PerformanceQualificationApiResponse(BaseModel):
    data: PerformanceQualificationReport
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
) -> Any:
    request_id = resolve_request_id(request)
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
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
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


@router.post(
    "/performance-qualification",
    response_model=PerformanceQualificationApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
async def evaluate_performance_qualification(
    request: Request,
    body: PerformanceQualificationRequest,
    current_user: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="performance_qualification"
    )
    if limit_error is not None:
        return limit_error

    try:
        report = await PerformanceQualificationService.evaluate_run_async(
            family=body.family,
            profile=body.profile,
            total_requests=body.total_requests,
            success_count=body.success_count,
            protection_count=body.protection_count,
            error_count=body.error_count,
            latency_p50_ms=body.latency_p50_ms,
            latency_p95_ms=body.latency_p95_ms,
            latency_p99_ms=body.latency_p99_ms,
            throughput_rps=body.throughput_rps,
            db=db,
            active_snapshot_id=body.active_snapshot_id,
            active_snapshot_version=body.active_snapshot_version,
            manifest_entry_id=body.manifest_entry_id,
            environment=body.environment,
        )
        return {"data": report.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValueError as err:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_qualification_context",
            message=str(err),
            details={},
        )
