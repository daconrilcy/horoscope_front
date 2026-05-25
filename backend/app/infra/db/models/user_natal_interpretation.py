# Commentaire global: ce modele conserve les interpretations natales et leur audit narratif.
"""Déclare le stockage canonique des réponses narratives et de leur audit."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import ClassVar

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_field_lengths import (
    INPUT_HASH_HEX_LENGTH,
    MODEL_LENGTH,
    PLAN_LENGTH,
    PROVIDER_LENGTH,
    VERSION_LENGTH,
)

ANSWER_ID_LENGTH = 96
ANSWER_TYPE_LENGTH = 16
GROUNDING_STATUS_LENGTH = 16
PROMPT_REF_LENGTH = 255
PROMPT_SNAPSHOT_REF_LENGTH = 255
PROJECTION_HASH_LENGTH = 64

ALLOWED_NARRATIVE_ANSWER_TYPES = ("basic", "premium", "long", "sensitive", "free_short")
ALLOWED_NARRATIVE_GROUNDING_STATUSES = (
    "grounded",
    "partial",
    "ungrounded",
    "rejected",
    "not_checked",
)


class InterpretationLevel(str, Enum):
    """Liste les granularites historiques des interpretations natales."""

    SHORT = "short"
    COMPLETE = "complete"


class UserNatalInterpretationModel(Base):
    """Stocke une reponse narrative utilisateur avec son audit CS-259."""

    __tablename__ = "user_natal_interpretations"
    allowed_answer_types: ClassVar[tuple[str, ...]] = ALLOWED_NARRATIVE_ANSWER_TYPES
    allowed_grounding_statuses: ClassVar[tuple[str, ...]] = ALLOWED_NARRATIVE_GROUNDING_STATUSES
    __table_args__ = (
        CheckConstraint(
            f"answer_type IN {ALLOWED_NARRATIVE_ANSWER_TYPES}",
            name="ck_user_natal_interpretations_answer_type",
        ),
        CheckConstraint(
            f"grounding_status IN {ALLOWED_NARRATIVE_GROUNDING_STATUSES}",
            name="ck_user_natal_interpretations_grounding_status",
        ),
        Index(
            "uq_user_natal_interpretations_null_persona",
            "user_id",
            "chart_id",
            "level",
            "variant_code",
            unique=True,
            postgresql_where=text("persona_id IS NULL"),
            sqlite_where=text("persona_id IS NULL"),
        ),
        Index(
            "uq_user_natal_interpretations_with_persona",
            "user_id",
            "chart_id",
            "level",
            "persona_id",
            "variant_code",
            unique=True,
            postgresql_where=text("persona_id IS NOT NULL"),
            sqlite_where=text("persona_id IS NOT NULL"),
        ),
        Index(
            "idx_user_natal_interpretations_listing",
            "user_id",
            "chart_id",
            "level",
            "created_at",
        ),
        Index("ix_user_natal_interpretations_answer_id", "answer_id"),
        Index(
            "ix_user_natal_interpretations_audit_lookup",
            "user_id",
            "chart_id",
            "answer_type",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    chart_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    level: Mapped[InterpretationLevel] = mapped_column(
        SqlEnum(InterpretationLevel), nullable=False, index=True
    )

    use_case: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    persona_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    persona_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    answer_id: Mapped[str] = mapped_column(
        String(ANSWER_ID_LENGTH),
        default=lambda: f"answer-{uuid.uuid4()}",
        nullable=False,
    )
    answer_type: Mapped[str] = mapped_column(
        String(ANSWER_TYPE_LENGTH), nullable=False, default="basic"
    )
    plan: Mapped[str] = mapped_column(String(PLAN_LENGTH), nullable=False, default="unknown")
    projection_version: Mapped[str] = mapped_column(
        String(VERSION_LENGTH),
        nullable=False,
        default="legacy_unavailable",
    )
    projection_hash: Mapped[str] = mapped_column(
        String(PROJECTION_HASH_LENGTH),
        nullable=False,
        default="0" * PROJECTION_HASH_LENGTH,
    )
    llm_input_version: Mapped[str] = mapped_column(
        String(VERSION_LENGTH),
        nullable=False,
        default="legacy_unavailable",
    )
    llm_input_hash: Mapped[str] = mapped_column(
        String(INPUT_HASH_HEX_LENGTH),
        nullable=False,
        default="0" * INPUT_HASH_HEX_LENGTH,
    )
    prompt_version: Mapped[str] = mapped_column(
        String(VERSION_LENGTH),
        nullable=False,
        default="legacy_unavailable",
    )
    prompt_ref: Mapped[str | None] = mapped_column(String(PROMPT_REF_LENGTH), nullable=True)
    prompt_snapshot_ref: Mapped[str | None] = mapped_column(
        String(PROMPT_SNAPSHOT_REF_LENGTH),
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(
        String(PROVIDER_LENGTH), nullable=False, default="unknown"
    )
    model: Mapped[str] = mapped_column(String(MODEL_LENGTH), nullable=False, default="unknown")
    grounding_status: Mapped[str] = mapped_column(
        String(GROUNDING_STATUS_LENGTH),
        nullable=False,
        default="not_checked",
    )
    evidence_refs: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list, nullable=False
    )

    interpretation_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    was_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    degraded_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )

    user = relationship("UserModel")
