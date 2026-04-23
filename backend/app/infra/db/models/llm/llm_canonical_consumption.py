# Modèle DB d'agrégation de consommation canonique LLM.
"""Déclare le read model utilisé pour piloter les coûts et volumes LLM canoniques."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_constraints import allowed_values_check


class LlmCanonicalConsumptionAggregateModel(Base):
    """Historise les métriques agrégées de consommation LLM par période et dimensions."""

    __tablename__ = "llm_canonical_consumption_aggregates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    granularity: Mapped[str] = mapped_column(String(16), nullable=False)  # day | month
    period_start_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subscription_plan: Mapped[str] = mapped_column(String(64), nullable=False)
    feature: Mapped[str] = mapped_column(String(64), nullable=False)
    subfeature: Mapped[str | None] = mapped_column(String(64), nullable=True)
    locale: Mapped[str] = mapped_column(String(32), nullable=False)
    executed_provider: Mapped[str] = mapped_column(String(32), nullable=False)
    active_snapshot_version: Mapped[str] = mapped_column(String(64), nullable=False)
    is_legacy_residual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd_estimated_microusd: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_p50_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_p95_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_rate_bps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    refreshed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime_provider.utcnow(),
    )

    __table_args__ = (
        UniqueConstraint(
            "granularity",
            "period_start_utc",
            "user_id",
            "subscription_plan",
            "feature",
            "subfeature",
            "locale",
            "executed_provider",
            "active_snapshot_version",
            "is_legacy_residual",
            name="uq_llm_canonical_consumption_dims",
        ),
        allowed_values_check(
            "ck_llm_canonical_consumption_granularity",
            "granularity",
            ("day", "month"),
        ),
        Index("ix_llm_canonical_consumption_period", "granularity", "period_start_utc"),
        Index("ix_llm_canonical_consumption_feature", "feature", "subfeature"),
    )
