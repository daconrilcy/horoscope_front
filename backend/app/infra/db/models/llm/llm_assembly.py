# Modèle DB de configuration d'assemblage LLM.
"""Declare la table qui assemble prompts, personas et profils d execution LLM."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    UUID,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_field_lengths import (
    FEATURE_LENGTH,
    LOCALE_LENGTH,
    PLAN_LENGTH,
    SUBFEATURE_LENGTH,
)
from app.infra.db.models.llm.llm_indexes import published_unique_index
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, PromptStatus


class AssemblyComponentResolutionState(str, Enum):
    """Liste les états explicites de resolution d'un composant optionnel."""

    ABSENT = "absent"
    INHERITED = "inherited"
    ENABLED = "enabled"
    DISABLED = "disabled"


class PromptAssemblyConfigModel(CreatedByMixin, CreatedAtMixin, PublishedAtMixin, Base):
    """Represente une configuration d assemblage publiee ou brouillon pour une cible LLM."""

    __tablename__ = "llm_assembly_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature: Mapped[str] = mapped_column(String(FEATURE_LENGTH), index=True)
    subfeature: Mapped[Optional[str]] = mapped_column(
        String(SUBFEATURE_LENGTH), nullable=True, index=True
    )
    plan: Mapped[Optional[str]] = mapped_column(String(PLAN_LENGTH), nullable=True, index=True)
    locale: Mapped[str] = mapped_column(String(LOCALE_LENGTH), index=True, default="fr-FR")

    feature_template_ref: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_prompt_versions.id", ondelete="RESTRICT")
    )
    subfeature_template_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_prompt_versions.id", ondelete="SET NULL"), nullable=True
    )
    persona_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_personas.id", ondelete="SET NULL"), nullable=True
    )
    execution_profile_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_execution_profiles.id", ondelete="SET NULL"), nullable=True
    )
    output_schema_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_output_schemas.id", ondelete="SET NULL"), nullable=True
    )
    plan_rules_ref: Mapped[Optional[str]] = mapped_column(String(PLAN_LENGTH), nullable=True)
    length_budget: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    feature_template_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(32),
        nullable=False,
        default=AssemblyComponentResolutionState.ENABLED.value,
    )
    subfeature_template_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(32),
        nullable=False,
        default=AssemblyComponentResolutionState.ABSENT.value,
    )
    persona_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(32),
        nullable=False,
        default=AssemblyComponentResolutionState.INHERITED.value,
    )
    plan_rules_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(32),
        nullable=False,
        default=AssemblyComponentResolutionState.ABSENT.value,
    )

    status: Mapped[PromptStatus] = mapped_column(
        String(32), index=True, default=PromptStatus.DRAFT
    )

    @validates("plan_rules_ref")
    def validate_optional_reference(self, key: str, value: Optional[str]) -> Optional[str]:
        """Bloque les references vides qui masquent une configuration incomplete."""
        if value is not None and not value.strip():
            raise ValueError(f"{key} must not be empty when provided.")
        return value

    @validates("status")
    def validate_status_change(self, key: str, value: PromptStatus) -> PromptStatus:
        """Bloque la publication si la configuration référence une taxonomie legacy."""
        if value == PromptStatus.PUBLISHED:
            from app.domain.llm.governance.feature_taxonomy import (
                NATAL_CANONICAL_FEATURE,
                assert_nominal_feature_allowed,
                is_natal_subfeature_canonical,
            )

            # AC2, AC5: Validate feature taxonomy
            if self.feature:
                assert_nominal_feature_allowed(self.feature)

                # AC6: Ensure subfeature is canonical if feature is natal
                if self.feature == NATAL_CANONICAL_FEATURE and self.subfeature:
                    if not is_natal_subfeature_canonical(self.subfeature):
                        raise ValueError(
                            f"Subfeature '{self.subfeature}' is not canonical "
                            f"for feature '{self.feature}'."
                        )
        return value

    # Relationships
    feature_template: Mapped[LlmPromptVersionModel] = relationship(
        "LlmPromptVersionModel", foreign_keys=[feature_template_ref]
    )
    subfeature_template: Mapped[Optional[LlmPromptVersionModel]] = relationship(
        "LlmPromptVersionModel", foreign_keys=[subfeature_template_ref]
    )
    persona: Mapped[Optional[LlmPersonaModel]] = relationship(
        "LlmPersonaModel", foreign_keys=[persona_ref]
    )
    execution_profile: Mapped[Optional[LlmExecutionProfileModel]] = relationship(
        "LlmExecutionProfileModel", foreign_keys=[execution_profile_ref]
    )
    output_schema: Mapped[Optional[LlmOutputSchemaModel]] = relationship(
        "LlmOutputSchemaModel", foreign_keys=[output_schema_id], back_populates="assemblies"
    )

    def component_resolution_states(self) -> dict[str, AssemblyComponentResolutionState]:
        """Expose la semantique des composants optionnels sans ambiguite booleenne."""
        return {
            "feature_template": AssemblyComponentResolutionState(
                self.feature_template_state
                or self.infer_component_state(
                    has_reference=self.feature_template_ref is not None,
                    is_enabled=True,
                    can_inherit=False,
                ).value
            ),
            "subfeature_template": AssemblyComponentResolutionState(
                self.subfeature_template_state
                or self.infer_component_state(
                    has_reference=self.subfeature_template_ref is not None,
                    is_enabled=True,
                    can_inherit=self.subfeature is not None,
                ).value
            ),
            "persona": AssemblyComponentResolutionState(
                self.persona_state
                or self.infer_component_state(
                    has_reference=self.persona_ref is not None,
                    is_enabled=True,
                    can_inherit=True,
                ).value
            ),
            "plan_rules": AssemblyComponentResolutionState(
                self.plan_rules_state
                or self.infer_component_state(
                    has_reference=self.plan_rules_ref is not None,
                    is_enabled=True,
                    can_inherit=self.plan is not None,
                ).value
            ),
        }

    @staticmethod
    def infer_component_state(
        *,
        has_reference: bool,
        is_enabled: bool,
        can_inherit: bool,
    ) -> AssemblyComponentResolutionState:
        """Traduit reference, héritage possible et flag enabled en état explicite."""
        if not is_enabled:
            return AssemblyComponentResolutionState.DISABLED
        if has_reference:
            return AssemblyComponentResolutionState.ENABLED
        if can_inherit:
            return AssemblyComponentResolutionState.INHERITED
        return AssemblyComponentResolutionState.ABSENT

    def is_feature_template_enabled(self) -> bool:
        """Indique si le bloc feature participe au rendu nominal."""
        return self.component_resolution_states()["feature_template"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    def is_subfeature_template_enabled(self) -> bool:
        """Indique si le bloc subfeature participe au rendu nominal."""
        return self.component_resolution_states()["subfeature_template"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    def is_persona_enabled(self) -> bool:
        """Indique si le persona participe au rendu nominal."""
        return self.component_resolution_states()["persona"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    def is_plan_rules_enabled(self) -> bool:
        """Indique si les regles de plan participent au rendu nominal."""
        return self.component_resolution_states()["plan_rules"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    __table_args__ = (
        published_unique_index(
            "ix_llm_assembly_config_active_unique",
            "feature",
            func.coalesce(subfeature, ""),
            func.coalesce(plan, ""),
            "locale",
            status_column=status,
        ),
        Index("ix_llm_assembly_configs_created_at", "created_at"),
    )
