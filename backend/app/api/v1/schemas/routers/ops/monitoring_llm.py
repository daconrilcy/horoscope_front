"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_observability.monitoring_service import (
    LlmOpsMonitoringData,
)

router = APIRouter(prefix="/v1/ops/monitoring/llm", tags=["ops-monitoring-llm"])


class ResponseMeta(BaseModel):
    request_id: str


class LlmOpsMonitoringApiResponse(BaseModel):
    data: LlmOpsMonitoringData
    meta: ResponseMeta
