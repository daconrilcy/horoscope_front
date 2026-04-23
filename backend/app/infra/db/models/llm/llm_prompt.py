# Modèles DB des prompts et contrats de use case LLM.
"""Déclare les use cases LLM et leurs versions de prompts publiables."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import ClassVar

from sqlalchemy import (
    JSON,
    UUID,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_indexes import published_unique_index


class PromptStatus(str, Enum):
    """Liste les statuts de cycle de vie d'un prompt LLM."""

    DRAFT = "draft"
    PUBLISHED = "published"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

    @classmethod
    def normalize(cls, value: "PromptStatus | str") -> "PromptStatus":
        """Normalise les anciens statuts vers les statuts actifs."""
        if value == cls.ARCHIVED or value == cls.ARCHIVED.value:
            return cls.INACTIVE
        if isinstance(value, cls):
            return value
        return cls(str(value))

    @classmethod
    def inactive_values(cls) -> tuple[str, str]:
        """Retourne les statuts considérés inactifs, y compris l'ancien statut archivé."""
        return (cls.INACTIVE.value, cls.ARCHIVED.value)


class LlmUseCaseConfigModel(Base):
    """Décrit le contrat fonctionnel et technique d'un use case LLM."""

    __tablename__ = "llm_use_case_configs"
    legacy_identity_field: ClassVar[str] = "key"
    canonical_scope_fields: ClassVar[frozenset[str]] = frozenset(
        {"feature", "subfeature", "plan", "locale"}
    )
    legacy_compatibility_fields: ClassVar[frozenset[str]] = frozenset(
        {"fallback_use_case_key", "allowed_persona_ids"}
    )

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

    prompt_versions: Mapped[list["LlmPromptVersionModel"]] = relationship(
        "LlmPromptVersionModel", back_populates="use_case", cascade="all, delete-orphan"
    )


class LlmPromptVersionModel(CreatedByMixin, CreatedAtMixin, PublishedAtMixin, Base):
    """Représente une version de prompt LLM liée à un use case."""

    __tablename__ = "llm_prompt_versions"
    legacy_use_case_link_field: ClassVar[str] = "use_case_key"
    legacy_execution_compatibility_fields: ClassVar[frozenset[str]] = frozenset(
        {"model", "temperature", "max_output_tokens", "reasoning_effort", "verbosity"}
    )
    canonical_text_fields: ClassVar[frozenset[str]] = frozenset({"developer_prompt"})

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case_key: Mapped[str] = mapped_column(
        ForeignKey("llm_use_case_configs.key", ondelete="CASCADE"), index=True
    )
    status: Mapped[PromptStatus] = mapped_column(String(16), index=True, default=PromptStatus.DRAFT)
    developer_prompt: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64))
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=2048)
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

    use_case: Mapped[LlmUseCaseConfigModel] = relationship(
        "LlmUseCaseConfigModel", back_populates="prompt_versions"
    )

    __table_args__ = (
        published_unique_index(
            "ix_llm_prompt_version_active_unique",
            "use_case_key",
            status_column=status,
        ),
    )
