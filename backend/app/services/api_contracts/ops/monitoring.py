"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel

from app.domain.llm.runtime.contracts import PerformanceQualificationReport
from app.services.ops.monitoring_service import (
    OpsMonitoringKpisData,
    OpsMonitoringOperationalSummaryData,
    OpsMonitoringPersonaKpisData,
    OpsMonitoringPricingKpisData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class OpsMonitoringApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringKpisData
    meta: ResponseMeta


class OpsMonitoringOperationalSummaryApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringOperationalSummaryData
    meta: ResponseMeta


class OpsMonitoringPersonaKpisApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringPersonaKpisData
    meta: ResponseMeta


class OpsMonitoringPricingKpisApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringPricingKpisData
    meta: ResponseMeta


class PerformanceQualificationRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: PerformanceQualificationReport
    meta: ResponseMeta
