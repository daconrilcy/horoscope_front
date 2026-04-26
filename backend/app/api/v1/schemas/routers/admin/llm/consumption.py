"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.llm_observability.consumption_service import (
    CanonicalConsumptionAggregate,
    CanonicalConsumptionFilters,
    Granularity,
    LlmCanonicalConsumptionService,
    Scope,
)

router = APIRouter(prefix="/v1/admin/llm/consumption", tags=["admin-llm-consumption"])
ConsumptionView = str
VALID_VIEWS = {"user", "subscription", "feature"}
MAX_PAGE_SIZE = 100
DEFAULT_DRILLDOWN_LIMIT = 50


class CanonicalConsumptionViewRow(BaseModel):
    period_start_utc: datetime
    granularity: Granularity
    user_id: int | None = None
    user_email: str | None = None
    subscription_plan: str | None = None
    feature: str | None = None
    subfeature: str | None = None
    locale: str | None = None
    executed_provider: str | None = None
    active_snapshot_version: str | None = None
    request_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    avg_latency_ms: float
    error_rate: float


class CanonicalConsumptionResponse(BaseModel):
    data: list[CanonicalConsumptionViewRow]
    meta: dict[str, Any]


class CanonicalConsumptionDrilldownRow(BaseModel):
    request_id: str
    timestamp: datetime
    feature: str | None = None
    subfeature: str | None = None
    provider: str | None = None
    active_snapshot_version: str | None = None
    manifest_entry_id: str | None = None
    validation_status: str


class CanonicalConsumptionDrilldownResponse(BaseModel):
    data: list[CanonicalConsumptionDrilldownRow]
    meta: dict[str, Any]
