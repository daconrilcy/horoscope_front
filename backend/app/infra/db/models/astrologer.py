from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.llm_persona import LlmPersonaModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AstrologerGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"


class AstrologerProfileModel(Base):
    __tablename__ = "astrologer_profiles"

    # Linked 1:1 to LlmPersonaModel. We use persona_id as PK for simplicity and performance.
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_personas.id", ondelete="CASCADE"), primary_key=True
    )

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(200))
    gender: Mapped[AstrologerGender] = mapped_column(String(32))
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    # "Mystique", "Analytique", etc.
    public_style_label: Mapped[str] = mapped_column(String(100))
    
    bio_short: Mapped[str] = mapped_column(String(500))
    bio_long: Mapped[str] = mapped_column(Text)
    
    # Internal category: "standard", "mystical", etc.
    admin_category: Mapped[str] = mapped_column(String(64), index=True)
    
    # JSON list of strings: ["Amour", "Carrière", etc.]
    specialties: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    # Relationships
    persona: Mapped[LlmPersonaModel] = relationship(
        "LlmPersonaModel", backref="astrologer_profile"
    )


class AstrologerPromptProfileModel(Base):
    """
    Dedicated table for astrologer prompt configuration.
    Allows versioning and precise control over the prompt injected for this specific persona.
    """
    __tablename__ = "astrologer_prompt_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_personas.id", ondelete="CASCADE"), index=True
    )
    
    # Content to be injected into the system prompt for this persona
    # Usually contains: instructions, tone details, style markers, etc.
    prompt_content: Mapped[str] = mapped_column(Text)
    
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    persona: Mapped[LlmPersonaModel] = relationship(
        "LlmPersonaModel", backref="prompt_profiles"
    )
