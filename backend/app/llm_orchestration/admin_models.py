from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.infra.db.models.llm_prompt import PromptStatus
from app.llm_orchestration.execution_profiles_types import (
    OutputMode,
    ReasoningProfile,
    ToolMode,
    VerbosityProfile,
)
from app.llm_orchestration.feature_taxonomy import (
    assert_nominal_feature_allowed,
    normalize_feature,
    normalize_subfeature,
)
from app.llm_orchestration.models import is_reasoning_model


class LlmOutputSchema(BaseModel):
    """Serializable admin view of an output schema."""

    id: uuid.UUID
    name: str
    json_schema: Dict[str, Any]
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SectionBudget(BaseModel):
    """Target length for a specific section."""

    section_name: str
    target: str  # Editorial description (e.g. "2-3 sentences")


class LengthBudget(BaseModel):
    """Budget for response length (Story 66.12)."""

    target_response_length: Optional[str] = None  # Editorial overall (e.g. "concise (100 words)")
    global_max_tokens: Optional[int] = None  # Hard provider limit override
    section_budgets: List[SectionBudget] = Field(default_factory=list)


class LlmPersona(BaseModel):
    """
    Serializable admin view of an LLM persona.

    Source of truth for: stylistic voice and tone.
    See: ARCHITECTURE.md
    """

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
    """Payload for persona creation."""

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
    """Patch payload for persona updates."""

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


class LlmPromptVersion(BaseModel):
    """
    Serializable admin view of a prompt version.

    Source of truth for: prompt block textual content.
    See: ARCHITECTURE.md
    """

    id: uuid.UUID
    use_case_key: str
    status: PromptStatus
    developer_prompt: str
    model: str
    temperature: float
    max_output_tokens: int
    fallback_use_case_key: Optional[str] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None
    created_by: str
    created_at: datetime
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LlmPromptVersionCreate(BaseModel):
    """Payload for prompt draft creation."""

    developer_prompt: str
    model: str
    temperature: Optional[float] = 0.7
    max_output_tokens: int = 2048
    fallback_use_case_key: Optional[str] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None


class LlmUseCaseConfig(BaseModel):
    """Serializable admin view of a use case configuration."""

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
    fallback_use_case_key: Optional[str] = None
    allowed_persona_ids: List[str] = Field(default_factory=list)
    eval_fixtures_path: Optional[str] = None
    eval_failure_threshold: Optional[float] = None
    golden_set_path: Optional[str] = None
    active_prompt_version_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class PromptAssemblyTarget(BaseModel):
    """Target identifying a unique assembly configuration."""

    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"

    @model_validator(mode="after")
    def normalize_taxonomy(self) -> "PromptAssemblyTarget":
        # AC2/AC5: Rejeter l'utilisation nominale des anciennes clés AVANT normalisation
        assert_nominal_feature_allowed(self.feature)
        self.feature = normalize_feature(self.feature)
        self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        return self


class ExecutionConfigAdmin(BaseModel):
    """Execution parameters for an assembly config."""

    model: str
    temperature: Optional[float] = 0.7
    max_output_tokens: int = 2048
    timeout_seconds: int = 30
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None
    verbosity: Optional[Literal["verbose", "normal", "concise"]] = None
    fallback_use_case: Optional[str] = None

    @model_validator(mode="after")
    def validate_provider_params(self) -> "ExecutionConfigAdmin":
        is_reasoning = is_reasoning_model(self.model)

        if is_reasoning:
            if self.temperature is not None:
                raise ValueError("Temperature must be None for reasoning models")
        else:
            if self.reasoning_effort is not None:
                raise ValueError("Reasoning effort is only supported for reasoning models")

        if self.fallback_use_case:
            # We don't strictly validate fallback_use_case as reasoning or not here
            # because it's a full use case redirection, not just a model swap.
            pass

        return self


class PromptAssemblyConfig(BaseModel):
    """
    Pydantic model for reading/writing assembly configurations.

    Source of truth for: prompt composition selection and block activation.
    See: ARCHITECTURE.md
    """

    id: Optional[uuid.UUID] = None
    feature: str
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    locale: str = "fr-FR"

    feature_template_ref: uuid.UUID
    subfeature_template_ref: Optional[uuid.UUID] = None
    persona_ref: Optional[uuid.UUID] = None
    execution_profile_ref: Optional[uuid.UUID] = None
    plan_rules_ref: Optional[str] = None

    execution_config: ExecutionConfigAdmin
    output_contract_ref: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    length_budget: Optional[LengthBudget] = None

    interaction_mode: str = "structured"
    user_question_policy: str = "none"
    fallback_use_case: Optional[str] = None

    feature_enabled: bool = True
    subfeature_enabled: bool = True
    persona_enabled: bool = True
    plan_rules_enabled: bool = True

    published_at: Optional[datetime] = None

    @model_validator(mode="after")
    def normalize_taxonomy(self) -> "PromptAssemblyConfig":
        # AC2/AC5: Rejeter l'utilisation nominale des anciennes clés AVANT normalisation
        assert_nominal_feature_allowed(self.feature)
        self.feature = normalize_feature(self.feature)
        self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        return self

    model_config = ConfigDict(from_attributes=True)


class ResolvedAssembly(BaseModel):
    """Intermediate artifact between admin config and execution plan."""

    target: PromptAssemblyTarget

    feature_template_id: uuid.UUID
    feature_template_prompt: str

    subfeature_template_id: Optional[uuid.UUID] = None
    subfeature_template_prompt: Optional[str] = None

    template_source: Literal["explicit_subfeature", "fallback_default"]

    persona_ref: Optional[uuid.UUID] = None
    persona_block: Optional[str] = None

    plan_rules_content: Optional[str] = None

    execution_config: ExecutionConfigAdmin
    output_contract_ref: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    length_budget: Optional[LengthBudget] = None
    context_quality: str = "full"
    context_quality_instruction_injected: bool = False
    policy_layer_content: str


class PlaceholderInfo(BaseModel):
    """Info about an injectable variable in a prompt."""

    name: str
    type: str
    origin: str
    example: str


class DraftPublishResponse(BaseModel):
    """Result of a publish operation."""

    assembly_id: uuid.UUID
    status: str
    published_at: datetime
    archived_count: int


class PlaceholderResolutionStatus(BaseModel):
    """Status of a placeholder resolution in a preview (Story 66.13)."""

    name: str
    status: Literal["resolved", "missing_optional", "missing_required", "fallback_used", "unknown"]
    value_preview: Optional[str] = None


class PromptAssemblyPreview(BaseModel):
    """Full preview of a rendered assembly config."""

    target: PromptAssemblyTarget

    # Prompt blocks
    feature_block: str
    subfeature_block: Optional[str] = None
    persona_block: Optional[str] = None
    plan_rules_block: Optional[str] = None

    template_source: str

    # Final rendered prompt (concatenated blocks + rendered variables)
    rendered_developer_prompt: str

    # Separated layers
    hard_policy_block: str  # Immutable layer
    output_contract_ref: Optional[str] = None

    # Available variables for the feature
    available_variables: List[PlaceholderInfo]

    # Resolution status for each variable (Story 66.13)
    placeholder_resolution_status: List[PlaceholderResolutionStatus] = Field(default_factory=list)

    # Execution parameters
    resolved_execution_config: ExecutionConfigAdmin
    length_budget: Optional[LengthBudget] = None

    draft_preview: bool = True


class LlmExecutionProfile(BaseModel):
    """Serializable admin view of an execution profile."""

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
    """Payload for execution profile creation."""

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
            # AC2/AC5: Rejeter l'utilisation nominale des anciennes clés AVANT normalisation
            assert_nominal_feature_allowed(self.feature)
            self.feature = normalize_feature(self.feature)
            self.subfeature = normalize_subfeature(self.feature, self.subfeature)
        return self

    @model_validator(mode="after")
    def validate_provider(self) -> "LlmExecutionProfileCreate":
        from app.llm_orchestration.supported_providers import is_provider_supported

        if not is_provider_supported(self.provider):
            raise ValueError(
                f"Provider '{self.provider}' is not nominally supported by the platform."
            )
        return self

    @model_validator(mode="after")
    def validate_reasoning(self) -> "LlmExecutionProfileCreate":
        if self.reasoning_profile != "off":
            if not is_reasoning_model(self.model):
                raise ValueError(
                    f"reasoning_profile '{self.reasoning_profile}' requires a "
                    f"reasoning-capable model — got: {self.model}"
                )
        return self


class ResolvedExecutionProfile(BaseModel):
    """Runtime resolved profile with translated parameters."""

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
