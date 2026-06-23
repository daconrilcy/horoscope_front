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
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.ops.monitoring import (
    OpsMonitoringOperationalSummaryApiResponse,
    OpsMonitoringPricingKpisApiResponse,
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
