"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.llm_observability.monitoring_service import (
    LlmOpsMonitoringData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class LlmOpsMonitoringApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: LlmOpsMonitoringData
    meta: ResponseMeta
