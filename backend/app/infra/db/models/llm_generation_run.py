# Commentaire global: modele des tentatives techniques LLM liees aux slots publics.
"""Declare les runs LLM techniques sans leur donner de visibilite publique directe."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base

LLM_GENERATION_RUN_STATUS_GENERATING = "generating"
LLM_GENERATION_RUN_STATUS_ACCEPTED = "accepted"
LLM_GENERATION_RUN_STATUS_REJECTED = "rejected"
LLM_GENERATION_RUN_STATUS_FAILED_RETRIABLE = "failed_retriable"
LLM_GENERATION_RUN_STATUS_SUPERSEDED = "superseded"

LLM_GENERATION_RUN_STATUSES = (
    LLM_GENERATION_RUN_STATUS_GENERATING,
    LLM_GENERATION_RUN_STATUS_ACCEPTED,
    LLM_GENERATION_RUN_STATUS_REJECTED,
    LLM_GENERATION_RUN_STATUS_FAILED_RETRIABLE,
    LLM_GENERATION_RUN_STATUS_SUPERSEDED,
)


class LlmGenerationRunModel(Base):
    """Stocke une tentative LLM technique rattachee a un slot public."""

    __tablename__ = "llm_generation_runs"
    allowed_statuses: ClassVar[tuple[str, ...]] = LLM_GENERATION_RUN_STATUSES

    __table_args__ = (
        CheckConstraint(
            f"status IN {LLM_GENERATION_RUN_STATUSES}",
            name="ck_llm_generation_runs_status",
        ),
        Index(
            "uq_llm_generation_runs_slot_client_request",
            "slot_id",
            "client_request_id",
            unique=True,
        ),
        Index("ix_llm_generation_runs_slot_status", "slot_id", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("theme_natal_reading_slots.id"),
        nullable=False,
        index=True,
    )
    client_request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=LLM_GENERATION_RUN_STATUS_GENERATING,
    )
    raw_provider_response: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    parsed_raw_response: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    validation_errors: Mapped[list[dict[str, object]] | None] = mapped_column(JSON, nullable=True)
    rejection_reason: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    generation_contract_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    generation_contract_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    generation_contract_snapshot_id: Mapped[str | None] = mapped_column(String(220), nullable=True)
    provider_mode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    data_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    engine_profile_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    output_schema_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    slot = relationship(
        "ThemeNatalReadingSlotModel",
        back_populates="generation_runs",
        foreign_keys=[slot_id],
    )
