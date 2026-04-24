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
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_field_lengths import (
    ARTIFACT_PATH_LENGTH,
    FEATURE_LENGTH,
    SHORT_STATUS_LENGTH,
    USE_CASE_DISPLAY_NAME_LENGTH,
)
from app.infra.db.models.llm.llm_indexes import published_unique_index


class PromptStatus(str, Enum):
    """Liste les statuts de cycle de vie d'un prompt LLM."""

    DRAFT = "draft"
    PUBLISHED = "published"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

    @classmethod
    def inactive_values(cls) -> tuple[str, str]:
        """Retourne les statuts non publies reutilisables dans les parcours d historique."""
        return (cls.INACTIVE.value, cls.ARCHIVED.value)


class LlmUseCaseConfigModel(Base):
    """Porte le read model historique/admin des use cases LLM hors runtime nominal."""

    __tablename__ = "llm_use_case_configs"
    historical_identity_field: ClassVar[str] = "key"
    canonical_scope_fields: ClassVar[frozenset[str]] = frozenset(
        {"feature", "subfeature", "plan", "locale"}
    )
    runtime_surface: ClassVar[str] = "historical_admin_only"

    key: Mapped[str] = mapped_column(String(FEATURE_LENGTH), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(USE_CASE_DISPLAY_NAME_LENGTH))
    description: Mapped[str] = mapped_column(Text)
    required_prompt_placeholders: Mapped[list[str]] = mapped_column(JSON, default=list)
    eval_fixtures_path: Mapped[str | None] = mapped_column(
        String(ARTIFACT_PATH_LENGTH), nullable=True
    )
    eval_failure_threshold: Mapped[float] = mapped_column(Float, default=0.20)
    golden_set_path: Mapped[str | None] = mapped_column(String(ARTIFACT_PATH_LENGTH), nullable=True)

    prompt_versions: Mapped[list["LlmPromptVersionModel"]] = relationship(
        "LlmPromptVersionModel", back_populates="use_case", cascade="all, delete-orphan"
    )


class LlmPromptVersionModel(CreatedByMixin, CreatedAtMixin, PublishedAtMixin, Base):
    """Représente une version de prompt LLM liée à un use case."""

    __tablename__ = "llm_prompt_versions"
    historical_use_case_link_field: ClassVar[str] = "use_case_key"
    canonical_text_fields: ClassVar[frozenset[str]] = frozenset({"developer_prompt"})

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case_key: Mapped[str] = mapped_column(
        ForeignKey("llm_use_case_configs.key", ondelete="CASCADE"), index=True
    )
    status: Mapped[PromptStatus] = mapped_column(
        String(SHORT_STATUS_LENGTH), index=True, default=PromptStatus.DRAFT
    )
    developer_prompt: Mapped[str] = mapped_column(Text)

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
