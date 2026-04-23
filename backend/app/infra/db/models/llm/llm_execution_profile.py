# Modèle DB des profils d'exécution LLM.
"""Déclare les paramètres d'execution administrables des moteurs LLM."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import (
    UUID,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.domain.llm.runtime.execution_profiles_types import (
    OutputMode,
    ReasoningProfile,
    ToolMode,
    VerbosityProfile,
)
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_constraints import allowed_values_check
from app.infra.db.models.llm.llm_field_lengths import (
    FEATURE_LENGTH,
    MODEL_LENGTH,
    PLAN_LENGTH,
    PROVIDER_LENGTH,
    SHORT_STATUS_LENGTH,
    SUBFEATURE_LENGTH,
)
from app.infra.db.models.llm.llm_indexes import published_unique_index
from app.infra.db.models.llm.llm_prompt import PromptStatus


class LlmExecutionProfileModel(CreatedByMixin, CreatedAtMixin, PublishedAtMixin, Base):
    """Separe les choix moteur LLM du texte des prompts pour une cible donnee."""

    __tablename__ = "llm_execution_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(MODEL_LENGTH), nullable=False)  # Admin label

    provider: Mapped[str] = mapped_column(String(PROVIDER_LENGTH), nullable=False, default="openai")
    model: Mapped[str] = mapped_column(String(MODEL_LENGTH), nullable=False)

    # Internal stable profiles (Story 66.11 D4)
    reasoning_profile: Mapped[ReasoningProfile] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False, default="off"
    )
    verbosity_profile: Mapped[VerbosityProfile] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False, default="balanced"
    )
    output_mode: Mapped[OutputMode] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False, default="free_text"
    )
    tool_mode: Mapped[ToolMode] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False, default="none"
    )

    max_output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    fallback_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_execution_profiles.id"), nullable=True
    )

    # Target (waterfall resolution)
    feature: Mapped[Optional[str]] = mapped_column(String(FEATURE_LENGTH), nullable=True)
    subfeature: Mapped[Optional[str]] = mapped_column(String(SUBFEATURE_LENGTH), nullable=True)
    plan: Mapped[Optional[str]] = mapped_column(String(PLAN_LENGTH), nullable=True)

    status: Mapped[PromptStatus] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False, default=PromptStatus.DRAFT
    )

    @validates("model")
    def validate_model(self, key: str, value: str) -> str:
        """Garantit qu un profil publie ou brouillon cible un modele explicite."""
        if not str(value or "").strip():
            raise ValueError("model must not be empty.")
        return value

    @validates("timeout_seconds")
    def validate_timeout_seconds(self, key: str, value: int) -> int:
        """Garantit un timeout runtime strictement positif."""
        if int(value) <= 0:
            raise ValueError("timeout_seconds must be positive.")
        return value

    @validates("max_output_tokens")
    def validate_max_output_tokens(self, key: str, value: Optional[int]) -> Optional[int]:
        """Garantit que la limite de sortie optionnelle reste exploitable."""
        if value is not None and int(value) <= 0:
            raise ValueError("max_output_tokens must be positive when provided.")
        return value

    @validates("status")
    def validate_status_change(self, key: str, value: PromptStatus) -> PromptStatus:
        """Valide le support provider et la taxonomie avant publication."""
        if value == PromptStatus.PUBLISHED:
            from app.domain.llm.configuration.coherence import validate_execution_profile

            result = validate_execution_profile(self)
            if not result.is_valid:
                # We raise the first error message for simplicity in model validator
                # but we could also raise a more structured exception if needed.
                raise ValueError(result.errors[0].message)

        return value

    # Relationship for fallback
    fallback_profile = relationship("LlmExecutionProfileModel", remote_side=[id])

    __table_args__ = (
        published_unique_index(
            "ix_llm_execution_profile_active_unique",
            "feature",
            func.coalesce(subfeature, ""),
            func.coalesce(plan, ""),
            status_column=status,
        ),
        allowed_values_check(
            "ck_llm_execution_profiles_reasoning_profile",
            "reasoning_profile",
            ("off", "light", "medium", "deep"),
        ),
        allowed_values_check(
            "ck_llm_execution_profiles_verbosity_profile",
            "verbosity_profile",
            ("concise", "balanced", "detailed"),
        ),
        allowed_values_check(
            "ck_llm_execution_profiles_output_mode",
            "output_mode",
            ("free_text", "structured_json"),
        ),
        allowed_values_check(
            "ck_llm_execution_profiles_tool_mode",
            "tool_mode",
            ("none", "optional", "required"),
        ),
        allowed_values_check(
            "ck_llm_execution_profiles_provider",
            "provider",
            ("openai", "anthropic"),
        ),
        Index("ix_llm_execution_profiles_feature", "feature"),
        Index("ix_llm_execution_profiles_status", "status"),
    )
