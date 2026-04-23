# Modèle DB de configuration d'assemblage LLM.
"""Déclare la table qui assemble prompts, personas et profils d'exécution LLM."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, ClassVar, Optional

from sqlalchemy import (
    JSON,
    UUID,
    ForeignKey,
    Index,
    String,
    cast,
    func,
)
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship, validates

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import CreatedAtMixin, CreatedByMixin, PublishedAtMixin
from app.infra.db.models.llm.llm_constraints import allowed_values_check
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
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
    """Représente une configuration d'assemblage publiée ou brouillon pour une cible LLM."""

    __tablename__ = "llm_assembly_configs"
    legacy_runtime_compatibility_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "execution_config",
            "interaction_mode",
            "user_question_policy",
            "input_schema",
            "output_contract_ref",
            "fallback_use_case",
        }
    )
    profile_controlled_execution_config_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "model",
            "provider",
            "temperature",
            "timeout_seconds",
            "max_output_tokens",
            "reasoning_effort",
            "verbosity",
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature: Mapped[str] = mapped_column(String(64), index=True)
    subfeature: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    plan: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    locale: Mapped[str] = mapped_column(String(32), index=True, default="fr-FR")

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
    plan_rules_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    execution_config: Mapped[dict] = mapped_column(JSON)
    output_contract_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    length_budget: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    interaction_mode: Mapped[str] = mapped_column(String(16), default="structured")
    user_question_policy: Mapped[str] = mapped_column(String(16), default="none")
    fallback_use_case: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    feature_template_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(16), nullable=False, default=AssemblyComponentResolutionState.ENABLED.value
    )
    subfeature_template_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(16), nullable=False, default=AssemblyComponentResolutionState.ABSENT.value
    )
    persona_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(16), nullable=False, default=AssemblyComponentResolutionState.INHERITED.value
    )
    plan_rules_state: Mapped[AssemblyComponentResolutionState] = mapped_column(
        String(16), nullable=False, default=AssemblyComponentResolutionState.ABSENT.value
    )

    status: Mapped[PromptStatus] = mapped_column(String(16), index=True, default=PromptStatus.DRAFT)

    @validates("plan_rules_ref", "output_contract_ref")
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
        "LlmOutputSchemaModel",
        primaryjoin=lambda: (
            func.replace(foreign(PromptAssemblyConfigModel.output_contract_ref), "-", "")
            == cast(LlmOutputSchemaModel.id, String)
        ),
        viewonly=True,
        uselist=False,
    )

    def component_resolution_states(self) -> dict[str, AssemblyComponentResolutionState]:
        """Expose la semantique des composants optionnels sans ambiguité booléenne."""
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

    def __init__(self, **kwargs: Any) -> None:
        """Absorbe temporairement les anciens flags `*_enabled` a l'initialisation."""
        legacy_enabled_flags = {
            "feature_enabled": kwargs.pop("feature_enabled", None),
            "subfeature_enabled": kwargs.pop("subfeature_enabled", None),
            "persona_enabled": kwargs.pop("persona_enabled", None),
            "plan_rules_enabled": kwargs.pop("plan_rules_enabled", None),
        }
        super().__init__(**kwargs)
        if self.feature_template_state is None:
            self.feature_template_state = self.infer_component_state(
                has_reference=self.feature_template_ref is not None,
                is_enabled=True,
                can_inherit=False,
            ).value
        if self.subfeature_template_state is None:
            self.subfeature_template_state = self.infer_component_state(
                has_reference=self.subfeature_template_ref is not None,
                is_enabled=True,
                can_inherit=self.subfeature is not None,
            ).value
        if self.persona_state is None:
            self.persona_state = self.infer_component_state(
                has_reference=self.persona_ref is not None,
                is_enabled=True,
                can_inherit=True,
            ).value
        if self.plan_rules_state is None:
            self.plan_rules_state = self.infer_component_state(
                has_reference=self.plan_rules_ref is not None,
                is_enabled=True,
                can_inherit=self.plan is not None,
            ).value
        for key, value in legacy_enabled_flags.items():
            if value is not None:
                setattr(self, key, value)

    @property
    def feature_enabled(self) -> bool:
        """Expose la compatibilite legacy a partir de l'etat explicite."""
        return self.component_resolution_states()["feature_template"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    @feature_enabled.setter
    def feature_enabled(self, value: bool) -> None:
        self.feature_template_state = self.infer_component_state(
            has_reference=self.feature_template_ref is not None,
            is_enabled=bool(value),
            can_inherit=False,
        ).value

    @property
    def subfeature_enabled(self) -> bool:
        """Expose la compatibilite legacy a partir de l'etat explicite."""
        return self.component_resolution_states()["subfeature_template"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    @subfeature_enabled.setter
    def subfeature_enabled(self, value: bool) -> None:
        self.subfeature_template_state = self.infer_component_state(
            has_reference=self.subfeature_template_ref is not None,
            is_enabled=bool(value),
            can_inherit=self.subfeature is not None,
        ).value

    @property
    def persona_enabled(self) -> bool:
        """Expose la compatibilite legacy a partir de l'etat explicite."""
        return self.component_resolution_states()["persona"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    @persona_enabled.setter
    def persona_enabled(self, value: bool) -> None:
        self.persona_state = self.infer_component_state(
            has_reference=self.persona_ref is not None,
            is_enabled=bool(value),
            can_inherit=True,
        ).value

    @property
    def plan_rules_enabled(self) -> bool:
        """Expose la compatibilite legacy a partir de l'etat explicite."""
        return self.component_resolution_states()["plan_rules"] != (
            AssemblyComponentResolutionState.DISABLED
        )

    @plan_rules_enabled.setter
    def plan_rules_enabled(self, value: bool) -> None:
        self.plan_rules_state = self.infer_component_state(
            has_reference=self.plan_rules_ref is not None,
            is_enabled=bool(value),
            can_inherit=self.plan is not None,
        ).value

    __table_args__ = (
        published_unique_index(
            "ix_llm_assembly_config_active_unique",
            "feature",
            func.coalesce(subfeature, ""),
            func.coalesce(plan, ""),
            "locale",
            status_column=status,
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_interaction_mode",
            "interaction_mode",
            ("structured", "chat"),
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_user_question_policy",
            "user_question_policy",
            ("none", "optional", "required"),
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_feature_template_state",
            "feature_template_state",
            ("absent", "inherited", "enabled", "disabled"),
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_subfeature_template_state",
            "subfeature_template_state",
            ("absent", "inherited", "enabled", "disabled"),
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_persona_state",
            "persona_state",
            ("absent", "inherited", "enabled", "disabled"),
        ),
        allowed_values_check(
            "ck_llm_assembly_configs_plan_rules_state",
            "plan_rules_state",
            ("absent", "inherited", "enabled", "disabled"),
        ),
        Index("ix_llm_assembly_configs_created_at", "created_at"),
    )
