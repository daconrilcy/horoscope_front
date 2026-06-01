# Commentaire global: modele de slot public accepte pour les lectures natales theme natal.
"""Declare le cycle de vie public des slots de lecture natale separe des runs LLM."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import (
    JSON,
    UUID,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base

THEME_NATAL_SLOT_STATUS_EMPTY = "empty"
THEME_NATAL_SLOT_STATUS_GENERATING = "generating"
THEME_NATAL_SLOT_STATUS_ACCEPTED = "accepted"
THEME_NATAL_SLOT_STATUS_REJECTED = "rejected"
THEME_NATAL_SLOT_STATUS_FAILED_RETRIABLE = "failed_retriable"
THEME_NATAL_SLOT_STATUS_SUPERSEDED = "superseded"

THEME_NATAL_READING_SLOT_STATUSES = (
    THEME_NATAL_SLOT_STATUS_EMPTY,
    THEME_NATAL_SLOT_STATUS_GENERATING,
    THEME_NATAL_SLOT_STATUS_ACCEPTED,
    THEME_NATAL_SLOT_STATUS_REJECTED,
    THEME_NATAL_SLOT_STATUS_FAILED_RETRIABLE,
    THEME_NATAL_SLOT_STATUS_SUPERSEDED,
)


class ThemeNatalReadingSlotModel(Base):
    """Stocke l'etat public d'un slot de lecture natale accepte."""

    __tablename__ = "theme_natal_reading_slots"
    allowed_statuses: ClassVar[tuple[str, ...]] = THEME_NATAL_READING_SLOT_STATUSES

    __table_args__ = (
        CheckConstraint(
            f"status IN {THEME_NATAL_READING_SLOT_STATUSES}",
            name="ck_theme_natal_reading_slots_status",
        ),
        Index(
            "uq_theme_natal_reading_slots_null_persona",
            "user_id",
            "chart_id",
            "feature",
            "reading_kind",
            "product_plan",
            "output_variant",
            "contract_version",
            unique=True,
            postgresql_where=text("persona_profile_id IS NULL"),
            sqlite_where=text("persona_profile_id IS NULL"),
        ),
        Index(
            "uq_theme_natal_reading_slots_with_persona",
            "user_id",
            "chart_id",
            "feature",
            "reading_kind",
            "product_plan",
            "output_variant",
            "persona_profile_id",
            "contract_version",
            unique=True,
            postgresql_where=text("persona_profile_id IS NOT NULL"),
            sqlite_where=text("persona_profile_id IS NOT NULL"),
        ),
        Index(
            "ix_theme_natal_reading_slots_public_lookup",
            "user_id",
            "chart_id",
            "status",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    chart_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    feature: Mapped[str] = mapped_column(String(64), nullable=False)
    reading_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    product_plan: Mapped[str] = mapped_column(String(32), nullable=False)
    output_variant: Mapped[str] = mapped_column(String(64), nullable=False)
    persona_profile_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    contract_version: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=THEME_NATAL_SLOT_STATUS_EMPTY,
    )
    public_payload: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_generation_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )

    generation_runs = relationship(
        "LlmGenerationRunModel",
        back_populates="slot",
        foreign_keys="LlmGenerationRunModel.slot_id",
    )
