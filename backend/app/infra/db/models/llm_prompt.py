from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromptStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LlmUseCaseConfigModel(Base):
    __tablename__ = "llm_use_case_configs"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    input_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_schema_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    persona_strategy: Mapped[str] = mapped_column(
        String(16),
        default="optional",  # optional, required, forbidden
    )
    interaction_mode: Mapped[str] = mapped_column(
        String(16),
        default="structured",  # structured, chat
    )
    user_question_policy: Mapped[str] = mapped_column(
        String(16),
        default="none",  # none, optional, required
    )
    safety_profile: Mapped[str] = mapped_column(
        String(32),
        default="astrology",  # astrology, support, transactional
    )
    required_prompt_placeholders: Mapped[list[str]] = mapped_column(JSON, default=list)
    fallback_use_case_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    allowed_persona_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    eval_fixtures_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    eval_failure_threshold: Mapped[float] = mapped_column(Float, default=0.20)
    golden_set_path: Mapped[str | None] = mapped_column(String(255), nullable=True)


class LlmPromptVersionModel(Base):
    __tablename__ = "llm_prompt_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case_key: Mapped[str] = mapped_column(
        ForeignKey("llm_use_case_configs.key", ondelete="CASCADE"), index=True
    )
    status: Mapped[PromptStatus] = mapped_column(String(16), index=True, default=PromptStatus.DRAFT)
    developer_prompt: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64))
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    fallback_use_case_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reasoning_effort: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
    )
    verbosity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
    )
    created_by: Mapped[str] = mapped_column(String(255))  # user_id
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            "ix_llm_prompt_version_active_unique",
            "use_case_key",
            unique=True,
            postgresql_where=(status == PromptStatus.PUBLISHED),
            sqlite_where=(status == PromptStatus.PUBLISHED),
        ),
    )
