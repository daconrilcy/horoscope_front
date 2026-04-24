from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from app.domain.llm.governance.feature_taxonomy import (
    assert_nominal_feature_allowed,
    normalize_feature,
    normalize_subfeature,
)
from app.domain.llm.prompting.catalog import DEPRECATED_USE_CASE_MAPPING
from app.domain.llm.runtime.contracts import is_reasoning_model
from app.domain.llm.runtime.execution_profiles_types import (
    OutputMode,
    ReasoningProfile,
    ToolMode,
    VerbosityProfile,
)
from app.domain.llm.runtime.providers import is_provider_supported
from app.infra.db.models.llm.llm_assembly import AssemblyComponentResolutionState
from app.infra.db.models.llm.llm_prompt import PromptStatus


class LlmOutputSchema(BaseModel):
    id: uuid.UUID
    name: str
    json_schema: Dict[str, Any]
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SectionBudget(BaseModel):
    section_name: str
    target: str


class LengthBudget(BaseModel):
    target_response_length: Optional[str] = None
    global_max_tokens: Optional[int] = None
    section_budgets: List[SectionBudget] = Field(default_factory=list)


class LlmPersona(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    tone: str
    verbosity: str
    style_markers: List[str] = Field(default_factory=list)
    boundaries: List[str] = Field(default_factory=list)
    allowed_topics: List[str] = Field(default_factory=list)
    disallowed_topics: List[str] = Field(default_factory=list)
    formatting: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LlmPersonaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tone: str = "direct"
    verbosity: str = "medium"
    style_markers: List[str] = Field(default_factory=list)
    boundaries: List[str] = Field(default_factory=list)
    allowed_topics: List[str] = Field(default_factory=list)
    disallowed_topics: List[str] = Field(default_factory=list)
    formatting: Dict[str, Any] = Field(
        default_factory=lambda: {"sections": True, "bullets": False, "emojis": False}
    )
    enabled: bool = True


class LlmPersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    style_markers: Optional[List[str]] = None
    boundaries: Optional[List[str]] = None
    allowed_topics: Optional[List[str]] = None
    disallowed_topics: Optional[List[str]] = None
    formatting: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class AdminUseCaseAudit(BaseModel):
    maintenance_surface: Literal["canonical_runtime", "legacy_maintenance"]
    status: Literal["canonical_runtime", "legacy_alias", "legacy_registry_only"]
    canonical_feature: Optional[str] = None
    canonical_subfeature: Optional[str] = None
    canonical_plan: Optional[str] = None


def build_admin_use_case_audit(
    use_case_key: str | None,
    *,
    maintenance_surface: Literal["canonical_runtime", "legacy_maintenance"] = (
        "legacy_maintenance"
    ),
    canonical_feature: str | None = None,
    canonical_subfeature: str | None = None,
    canonical_plan: str | None = None,
) -> AdminUseCaseAudit | None:
    if not use_case_key:
        return None

    deprecated_mapping = DEPRECATED_USE_CASE_MAPPING.get(use_case_key)
    if deprecated_mapping is not None:
        return AdminUseCaseAudit(
            maintenance_surface="legacy_maintenance",
            status="legacy_alias",
            canonical_feature=deprecated_mapping.get("feature"),
            canonical_subfeature=deprecated_mapping.get("subfeature"),
            canonical_plan=deprecated_mapping.get("plan"),
        )

    if canonical_feature is not None:
        return AdminUseCaseAudit(
            maintenance_surface="canonical_runtime",
            status="canonical_runtime",
            canonical_feature=canonical_feature,
            canonical_subfeature=canonical_subfeature,
            canonical_plan=canonical_plan,
        )

    return AdminUseCaseAudit(
        maintenance_surface=maintenance_surface,
        status="legacy_registry_only",
    )


class LlmPromptVersion(BaseModel):
    id: uuid.UUID
    use_case_key: str
    status: PromptStatus
    developer_prompt: str
    use_case_audit: AdminUseCaseAudit | None = None
    created_by: str
    created_at: datetime
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("status")
    def serialize_status(self, status: PromptStatus) -> str:
        return status.value

    @model_validator(mode="after")
    def populate_admin_audit(self) -> "LlmPromptVersion":
        self.use_case_audit = build_admin_use_case_audit(self.use_case_key)
        return self


class LlmPromptVersionCreate(BaseModel):
    developer_prompt: str

    model_config = ConfigDict(extra="forbid")


class LlmUseCaseConfig(BaseModel):
    key: str
    display_name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    output_schema_id: Optional[str] = None
    persona_strategy: str = "optional"
    interaction_mode: str = "structured"
    user_question_policy: str = "none"
    safety_profile: str = "astrology"
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    eval_fixtures_path: Optional[str] = None
    eval_failure_threshold: Optional[float] = None
    golden_set_path: Optional[str] = None
    active_prompt_version_id: Optional[uuid.UUID] = None
    use_case_audit: AdminUseCaseAudit | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def populate_admin_audit(self) -> "LlmUseCaseConfig":
        self.use_case_audit = build_admin_use_case_audit(self.key)
        return self


class PromptAssemblyTarget(BaseModel):
    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"

    @model_validator(mode="after")
    def normalize_taxonomy(self) -> "PromptAssemblyTarget":
        assert_nominal_feature_allowed(self.feature)
        self.feature = normalize_feature(self.feature)
        self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        return self


class RuntimeSettingsAdmin(BaseModel):
    model: str
    temperature: Optional[float] = None
    max_output_tokens: int = 2048
    timeout_seconds: int = 30
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None
    verbosity: Optional[Literal["verbose", "normal", "concise"]] = None

    @model_validator(mode="after")
    def validate_provider_params(self) -> "RuntimeSettingsAdmin":
        is_reasoning = is_reasoning_model(self.model)
        if is_reasoning:
            if self.temperature is not None:
                raise ValueError("Temperature must be None for reasoning models")
        else:
            if self.reasoning_effort is not None:
                raise ValueError("Reasoning effort is only supported for reasoning models")
        return self


class PromptAssemblyConfig(BaseModel):
    id: Optional[uuid.UUID] = None
    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"
    feature_template_ref: uuid.UUID
    subfeature_template_ref: Optional[uuid.UUID] = None
    persona_ref: Optional[uuid.UUID] = None
    execution_profile_ref: Optional[uuid.UUID] = None
    output_schema_id: Optional[uuid.UUID] = None
    plan_rules_ref: Optional[str] = None
    length_budget: Optional[LengthBudget] = None
    feature_template_state: AssemblyComponentResolutionState = (
        AssemblyComponentResolutionState.ENABLED
    )
    subfeature_template_state: AssemblyComponentResolutionState = (
        AssemblyComponentResolutionState.ABSENT
    )
    persona_state: AssemblyComponentResolutionState = AssemblyComponentResolutionState.INHERITED
    plan_rules_state: AssemblyComponentResolutionState = AssemblyComponentResolutionState.ABSENT
    feature_enabled: bool = True
    subfeature_enabled: bool = True
    persona_enabled: bool = True
    plan_rules_enabled: bool = True
    published_at: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def normalize_taxonomy(self) -> "PromptAssemblyConfig":
        assert_nominal_feature_allowed(self.feature)
        self.feature = normalize_feature(self.feature)
        self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        self.feature_template_state = PromptAssemblyConfig._normalize_component_state(
            fallback_enabled=self.feature_enabled,
            explicit_state=self.feature_template_state,
            has_reference=True,
            can_inherit=False,
        )
        self.subfeature_template_state = PromptAssemblyConfig._normalize_component_state(
            fallback_enabled=self.subfeature_enabled,
            explicit_state=self.subfeature_template_state,
            has_reference=self.subfeature_template_ref is not None,
            can_inherit=self.subfeature is not None,
        )
        self.persona_state = PromptAssemblyConfig._normalize_component_state(
            fallback_enabled=self.persona_enabled,
            explicit_state=self.persona_state,
            has_reference=self.persona_ref is not None,
            can_inherit=True,
        )
        self.plan_rules_state = PromptAssemblyConfig._normalize_component_state(
            fallback_enabled=self.plan_rules_enabled,
            explicit_state=self.plan_rules_state,
            has_reference=self.plan_rules_ref is not None,
            can_inherit=self.plan is not None,
        )
        return self

    @staticmethod
    def _normalize_component_state(
        *,
        fallback_enabled: bool,
        explicit_state: AssemblyComponentResolutionState,
        has_reference: bool,
        can_inherit: bool,
    ) -> AssemblyComponentResolutionState:
        """Concilie les anciens booléens d'entrée avec les nouveaux états explicites."""
        if explicit_state != AssemblyComponentResolutionState.ABSENT or not fallback_enabled:
            if not fallback_enabled:
                return AssemblyComponentResolutionState.DISABLED
            return explicit_state
        if has_reference:
            return AssemblyComponentResolutionState.ENABLED
        if can_inherit:
            return AssemblyComponentResolutionState.INHERITED
        return AssemblyComponentResolutionState.ABSENT

    model_config = ConfigDict(from_attributes=True)


class ResolvedAssembly(BaseModel):
    target: PromptAssemblyTarget
    feature_template_id: uuid.UUID
    feature_template_prompt: str
    subfeature_template_id: Optional[uuid.UUID] = None
    subfeature_template_prompt: Optional[str] = None
    template_source: Literal["explicit_subfeature", "fallback_default"]
    persona_ref: Optional[uuid.UUID] = None
    persona_block: Optional[str] = None
    plan_rules_content: Optional[str] = None
    execution_profile_ref: Optional[uuid.UUID] = None
    output_schema_id: Optional[uuid.UUID] = None
    length_budget: Optional[LengthBudget] = None
    context_quality: str = "full"
    context_quality_instruction_injected: bool = False
    policy_layer_content: str


class PlaceholderInfo(BaseModel):
    name: str
    type: str
    origin: str
    example: str


class DraftPublishResponse(BaseModel):
    assembly_id: uuid.UUID
    status: str
    published_at: datetime
    archived_count: int


class PlaceholderResolutionStatus(BaseModel):
    name: str
    status: Literal["resolved", "missing_optional", "missing_required", "fallback_used", "unknown"]
    value_preview: Optional[str] = None


class PromptAssemblyPreview(BaseModel):
    target: PromptAssemblyTarget
    feature_block: str
    subfeature_block: Optional[str] = None
    persona_block: Optional[str] = None
    plan_rules_block: Optional[str] = None
    template_source: str
    rendered_developer_prompt: str
    hard_policy_block: str
    output_schema_id: Optional[str] = None
    available_variables: List[PlaceholderInfo]
    placeholder_resolution_status: List[PlaceholderResolutionStatus] = Field(default_factory=list)
    resolved_runtime_settings: RuntimeSettingsAdmin
    length_budget: Optional[LengthBudget] = None
    draft_preview: bool = True


class LlmExecutionProfile(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    model: str
    reasoning_profile: ReasoningProfile
    verbosity_profile: VerbosityProfile
    output_mode: OutputMode
    tool_mode: ToolMode
    max_output_tokens: Optional[int] = None
    timeout_seconds: int = 30
    fallback_profile_id: Optional[uuid.UUID] = None
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    status: PromptStatus
    created_at: datetime
    created_by: str
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LlmExecutionProfileCreate(BaseModel):
    name: str
    provider: str = "openai"
    model: str
    reasoning_profile: ReasoningProfile = "off"
    verbosity_profile: VerbosityProfile = "balanced"
    output_mode: OutputMode = "free_text"
    tool_mode: ToolMode = "none"
    max_output_tokens: Optional[int] = None
    timeout_seconds: int = 30
    fallback_profile_id: Optional[uuid.UUID] = None
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    plan: Optional[str] = None

    @model_validator(mode="after")
    def normalize_taxonomy(self) -> "LlmExecutionProfileCreate":
        if self.feature:
            assert_nominal_feature_allowed(self.feature)
            self.feature = normalize_feature(self.feature)
            self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        return self

    @model_validator(mode="after")
    def validate_provider(self) -> "LlmExecutionProfileCreate":
        self.provider = (self.provider or "").strip().lower()
        if not is_provider_supported(self.provider):
            raise ValueError(
                f"Provider '{self.provider}' is not nominally supported by the platform."
            )
        return self

    @model_validator(mode="after")
    def validate_reasoning(self) -> "LlmExecutionProfileCreate":
        if self.reasoning_profile != "off" and not is_reasoning_model(self.model):
            raise ValueError(
                f"reasoning_profile '{self.reasoning_profile}' requires a "
                f"reasoning-capable model — got: {self.model}"
            )
        return self


class ResolvedExecutionProfile(BaseModel):
    profile_id: Optional[uuid.UUID] = None
    provider: str
    model: str
    reasoning_profile: ReasoningProfile
    verbosity_profile: VerbosityProfile
    output_mode: OutputMode
    tool_mode: ToolMode
    max_output_tokens: Optional[int] = None
    timeout_seconds: int = 30
    source: Literal["explicit", "waterfall", "assembly_ref"]
    translated_provider_params: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "AdminUseCaseAudit",
    "DraftPublishResponse",
    "LengthBudget",
    "LlmExecutionProfile",
    "LlmExecutionProfileCreate",
    "LlmOutputSchema",
    "LlmPersona",
    "LlmPersonaCreate",
    "LlmPersonaUpdate",
    "LlmPromptVersion",
    "LlmPromptVersionCreate",
    "LlmUseCaseConfig",
    "PlaceholderInfo",
    "PlaceholderResolutionStatus",
    "PromptAssemblyConfig",
    "PromptAssemblyPreview",
    "PromptAssemblyTarget",
    "ResolvedAssembly",
    "ResolvedExecutionProfile",
    "RuntimeSettingsAdmin",
    "SectionBudget",
    "build_admin_use_case_audit",
]
