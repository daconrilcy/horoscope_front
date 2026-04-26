"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

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

router = APIRouter(prefix="/v1/ops/monitoring", tags=["ops-monitoring"])


class ResponseMeta(BaseModel):
    request_id: str


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
