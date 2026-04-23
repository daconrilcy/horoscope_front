from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class PersonaTone(str, Enum):
    WARM = "warm"
    DIRECT = "direct"
    MYSTICAL = "mystical"
    RATIONAL = "rational"


class PersonaVerbosity(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class LlmPersonaModel(Base):
    __tablename__ = "llm_personas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    tone: Mapped[PersonaTone] = mapped_column(String(32), default=PersonaTone.DIRECT)
    verbosity: Mapped[PersonaVerbosity] = mapped_column(String(32), default=PersonaVerbosity.MEDIUM)

    # JSON list of strings
    style_markers: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    boundaries: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    allowed_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    # JSON list of strings
    disallowed_topics: Mapped[list[str]] = mapped_column(JSON, default=list)

    # JSON : sections bool, bullets bool, emojis bool
    formatting: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"sections": True, "bullets": False, "emojis": False}
    )

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
