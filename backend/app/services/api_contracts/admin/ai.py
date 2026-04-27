"""Schemas Pydantic des endpoints admin AI."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminAiTrendPoint(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    date: str
    call_count: int
    error_count: int


class AdminAiFailedCall(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: str
    timestamp: datetime
    error_code: str
    request_id_masked: str | None


class AdminAiUseCaseMetrics(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    use_case: str
    display_name: str
    call_count: int
    total_tokens: int
    estimated_cost_usd: float
    avg_latency_ms: int
    p50_latency_ms: int | None = None
    p95_latency_ms: int | None = None
    error_rate: float
    retry_rate: float = 0  # retry_count not in current schema?
    # top_persona: str | None = None
    # top_prompt_version: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminAiMetricsResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminAiUseCaseMetrics]
    period: str


class AdminAiUseCaseDetailResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    use_case: str
    metrics: AdminAiUseCaseMetrics
    trend_data: list[AdminAiTrendPoint]
    recent_failed_calls: list[AdminAiFailedCall]
