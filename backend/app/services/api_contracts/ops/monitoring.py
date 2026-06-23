"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.ops.monitoring_service import (
    OpsMonitoringOperationalSummaryData,
    OpsMonitoringPricingKpisData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class OpsMonitoringOperationalSummaryApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringOperationalSummaryData
    meta: ResponseMeta


class OpsMonitoringPricingKpisApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: OpsMonitoringPricingKpisData
    meta: ResponseMeta
