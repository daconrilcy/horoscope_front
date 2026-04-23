from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, UUID, Boolean, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class InterpretationLevel(str, Enum):
    SHORT = "short"
    COMPLETE = "complete"


class UserNatalInterpretationModel(Base):
    """
    Stores persisted natal interpretations for users.
    Allows avoiding re-generating the free (short) interpretation every time.
    """

    __tablename__ = "user_natal_interpretations"
    __table_args__ = (
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

    # The actual structured AstroResponseV1 content
    interpretation_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    # Metadata for UI
    was_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    degraded_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )

    # Relationships
    user = relationship("UserModel")
