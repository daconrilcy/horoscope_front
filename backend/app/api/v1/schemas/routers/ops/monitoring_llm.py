"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from typing import Any
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_observability.monitoring_service import (
    LlmOpsMonitoringData,
    LlmOpsMonitoringService,
)

router = APIRouter(prefix="/v1/ops/monitoring/llm", tags=["ops-monitoring-llm"])


class ResponseMeta(BaseModel):
    request_id: str


class LlmOpsMonitoringApiResponse(BaseModel):
    data: LlmOpsMonitoringData
    meta: ResponseMeta
