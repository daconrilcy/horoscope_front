from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.ops.llm.performance_qualification import PerformanceQualificationService
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.ops.monitoring import (
    OpsMonitoringApiResponse,
    OpsMonitoringOperationalSummaryApiResponse,
    OpsMonitoringPersonaKpisApiResponse,
    OpsMonitoringPricingKpisApiResponse,
    PerformanceQualificationApiResponse,
    PerformanceQualificationRequest,
)
from app.services.ops.api_monitoring import (
    _enforce_limits,
    _raise_error,
)
from app.services.ops.monitoring_service import (
    OpsMonitoringService,
    OpsMonitoringServiceError,
)

router = APIRouter(prefix="/v1/ops/monitoring", tags=["ops-monitoring"])


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
        return _raise_error(
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
        return _raise_error(
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
        return _raise_error(
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
        return _raise_error(
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
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code="invalid_qualification_context",
            message=str(err),
            details={},
        )
