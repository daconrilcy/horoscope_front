"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.services.llm_observability.consumption_service import (
    Granularity,
)

ConsumptionView = str


class CanonicalConsumptionViewRow(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: list[CanonicalConsumptionViewRow]
    meta: dict[str, Any]


class CanonicalConsumptionDrilldownRow(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str
    timestamp: datetime
    feature: str | None = None
    subfeature: str | None = None
    provider: str | None = None
    active_snapshot_version: str | None = None
    manifest_entry_id: str | None = None
    validation_status: str


class CanonicalConsumptionDrilldownResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[CanonicalConsumptionDrilldownRow]
    meta: dict[str, Any]
