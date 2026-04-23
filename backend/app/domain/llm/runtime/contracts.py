"""Canonical runtime contracts entrypoint."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.datetime_provider import datetime_provider

EVIDENCE_ID_REGEX = r"^[A-Z0-9_\.:-]{3,80}$"


class FallbackStatus(str, Enum):
    TRANSITORY = "transitoire"
    TOLERATED = "toléré durablement"
    TO_REMOVE = "à retirer"


class FallbackType(str, Enum):
    LEGACY_WRAPPER = "legacy_wrapper"
    DEPRECATED_USE_CASE = "deprecated_use_case"
    USE_CASE_FIRST = "use_case_first"
    RESOLVE_MODEL = "resolve_model"
    EXECUTION_CONFIG_ADMIN = "execution_config_admin"
    PROVIDER_OPENAI = "provider_openai"
    NARRATOR_LEGACY = "narrator_legacy"
    TEST_LOCAL = "test_local"
    NATAL_NO_DB = "natal_no_db"
    DEPRECATED_FEATURE_ALIAS = "deprecated_feature_alias"


class ExecutionPathKind(str, Enum):
    CANONICAL_ASSEMBLY = "canonical_assembly"
    LEGACY_USE_CASE_FALLBACK = "legacy_use_case_fallback"
    LEGACY_EXECUTION_PROFILE_FALLBACK = "legacy_execution_profile_fallback"
    REPAIR = "repair"
    NON_NOMINAL_PROVIDER_TOLERATED = "non_nominal_provider_tolerated"
    UNKNOWN = "unknown"


class ContextCompensationStatus(str, Enum):
    NOT_NEEDED = "not_needed"
    TEMPLATE_HANDLED = "template_handled"
    INJECTOR_APPLIED = "injector_applied"
    UNKNOWN = "unknown"


class MaxTokensSource(str, Enum):
    LENGTH_BUDGET_GLOBAL = "length_budget_global"
    EXECUTION_PROFILE = "execution_profile"
    VERBOSITY_FALLBACK = "verbosity_fallback"
    UNSET = "unset"


class ExecutionObservabilitySnapshot(BaseModel):
    pipeline_kind: Literal["nominal_canonical", "transitional_governance"]
    execution_path_kind: ExecutionPathKind
    fallback_kind: Optional[FallbackType] = None
    requested_provider: str
    resolved_provider: str
    executed_provider: str
    context_quality: str
    context_compensation_status: ContextCompensationStatus
    max_output_tokens_source: MaxTokensSource
    max_output_tokens_final: int
    executed_provider_mode: str = "nominal"
    attempt_count: int = 1
    provider_error_code: Optional[str] = None
    breaker_state: Optional[str] = None
    breaker_scope: Optional[str] = None
    active_snapshot_id: Optional[uuid.UUID] = None
    active_snapshot_version: Optional[str] = None
    manifest_entry_id: Optional[str] = None

    model_config = ConfigDict(frozen=True, protected_namespaces=())


_REASONING_MODEL_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-")
_REASONING_MODEL_EXACT = {"o1", "o3", "o4", "gpt-5"}


def is_reasoning_model(model: str) -> bool:
    return model in _REASONING_MODEL_EXACT or model.startswith(_REASONING_MODEL_PREFIXES)


class ExecutionMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    content_blocks: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(frozen=True, protected_namespaces=())


class ExecutionUserInput(BaseModel):
    use_case: str
    locale: str = "fr-FR"
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    assembly_config_id: Optional[uuid.UUID] = None
    message: Optional[str] = None
    question: Optional[str] = None
    situation: Optional[str] = None
    conversation_id: Optional[str] = None
    persona_id_override: Optional[str] = None

    @property
    def last_user_msg(self) -> Optional[str]:
        return self.question or self.message


class ExecutionContext(BaseModel):
    history: List[ExecutionMessage] = Field(default_factory=list)
    natal_data: Optional[Dict[str, Any]] = None
    chart_json: Optional[str] = None
    precision_level: Optional[str] = None
    astro_context: Optional[Any] = None
    extra_context: Dict[str, Any] = Field(default_factory=dict)


class ExecutionFlags(BaseModel):
    is_repair_call: bool = False
    skip_common_context: bool = False
    test_fallback_active: bool = False
    validation_strict: bool = False
    evidence_catalog: Optional[Union[List[str], Dict[str, List[str]]]] = None
    prompt_version_id_override: Optional[str] = None
    visited_use_cases: List[str] = Field(default_factory=list)
    simulate_error: Optional[str] = None


class ExecutionOverrides(BaseModel):
    interaction_mode: Optional[Literal["structured", "chat"]] = None
    user_question_policy: Optional[Literal["none", "optional", "required"]] = None
    _applied_by: Optional[str] = None


class NatalExecutionInput(BaseModel):
    use_case_key: str
    locale: str = "fr-FR"
    level: Literal["short", "complete"]
    chart_json: str
    natal_data: Dict[str, Any]
    evidence_catalog: Union[List[str], Dict[str, List[str]]]
    persona_id: Optional[str] = None
    plan: str = "free"
    validation_strict: bool = True
    question: Optional[str] = None
    astro_context: Optional[str] = None
    module: Optional[str] = None
    variant_code: Optional[str] = None
    user_id: int
    request_id: str
    trace_id: str


class LLMExecutionRequest(BaseModel):
    user_input: ExecutionUserInput
    context: ExecutionContext = Field(default_factory=ExecutionContext)
    flags: ExecutionFlags = Field(default_factory=ExecutionFlags)
    overrides: Optional[ExecutionOverrides] = None
    user_id: Optional[int] = None
    request_id: str
    trace_id: str


class UseCaseConfig(BaseModel):
    model: str
    temperature: float = 0.7
    max_output_tokens: int = 1000
    timeout_seconds: int = 30
    system_core_key: str = "default_v1"
    developer_prompt: str
    prompt_version_id: str = "hardcoded-v1"
    persona_strategy: str = "optional"
    interaction_mode: str = "structured"
    user_question_policy: str = "none"
    safety_profile: str = "astrology"
    input_schema: Optional[Dict[str, Any]] = None
    output_schema_id: Optional[str] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    fallback_use_case: Optional[str] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None


class ComposedMessages(BaseModel):
    messages: List[Dict[str, Any]]


class GatewayRequest(BaseModel):
    use_case: str
    user_input: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    trace_id: str


class ResponseFormatConfig(BaseModel):
    type: Literal["json_schema", "json_object", "text"] = "text"
    json_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")

    model_config = ConfigDict(populate_by_name=True)


class ResolvedExecutionPlan(BaseModel):
    assembly_id: Optional[str] = None
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    feature_template_id: Optional[str] = None
    subfeature_template_id: Optional[str] = None
    template_source: Optional[str] = None
    model_id: str
    model_source: Literal["os_granular", "os_legacy", "config", "stub", "assembly"]
    model_override_active: bool = False
    is_legacy_compatibility: bool = False
    execution_profile_id: Optional[str] = None
    execution_profile_source: Optional[str] = None
    reasoning_profile: Optional[str] = None
    verbosity_profile: Optional[str] = None
    output_mode: Optional[str] = None
    tool_mode: Optional[str] = None
    requested_provider: str = "openai"
    provider: str = "openai"
    timeout_seconds: int = 30
    translated_provider_params: Dict[str, Any] = Field(default_factory=dict)
    prompt_version_id: Optional[str] = None
    rendered_developer_prompt: str
    system_core: str
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    persona_block: Optional[str] = None
    output_schema_id: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    output_schema_version: str = "v1"
    input_schema: Optional[Dict[str, Any]] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    interaction_mode: Literal["structured", "chat"]
    user_question_policy: Literal["none", "optional", "required"]
    overrides_applied: Dict[str, Any] = Field(default_factory=dict)
    temperature: float
    max_output_tokens: int
    max_output_tokens_source: Optional[str] = None
    response_format: Optional[ResponseFormatConfig] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None
    context_quality: str = "unknown"
    context_quality_instruction_injected: bool = False
    context_quality_handled_by_template: bool = False
    active_snapshot_id: Optional[uuid.UUID] = None
    active_snapshot_version: Optional[str] = None
    manifest_entry_id: Optional[str] = None

    model_config = ConfigDict(frozen=True, protected_namespaces=())

    @model_validator(mode="after")
    def validate_supported_perimeter_execution_profile_source(self) -> "ResolvedExecutionPlan":
        from app.domain.llm.governance.feature_taxonomy import is_supported_feature

        legacy_execution_profile_sources = {
            "fallback_resolve_model",
            "fallback_provider_unsupported",
        }
        if (
            is_supported_feature(self.feature)
            and self.execution_profile_source in legacy_execution_profile_sources
        ):
            raise ValueError(
                "Supported perimeter execution plans cannot use legacy execution-profile "
                f"source '{self.execution_profile_source}'."
            )
        return self

    def to_log_dict(self) -> Dict[str, Any]:
        dump = self.model_dump()
        for key in [
            "rendered_developer_prompt",
            "system_core",
            "persona_block",
            "output_schema",
            "input_schema",
        ]:
            dump.pop(key, None)
        return dump


class UsageInfo(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class GatewayMeta(BaseModel):
    latency_ms: int
    cached: bool = False
    prompt_version_id: str = "hardcoded-v1"
    assembly_id: Optional[str] = None
    feature: Optional[str] = None
    subfeature: Optional[str] = None
    plan: Optional[str] = None
    template_source: Optional[str] = None
    persona_id: Optional[str] = None
    model: str
    model_override_active: bool = False
    output_schema_id: Optional[str] = None
    schema_version: Optional[str] = "v1"
    validation_status: str = "valid"
    repair_attempted: bool = False
    fallback_triggered: bool = False
    validation_errors: Optional[List[str]] = None
    execution_path: Literal["nominal", "repaired", "fallback_use_case", "test_fallback"] = "nominal"
    context_quality: str = "unknown"
    context_quality_instruction_injected: bool = False
    missing_context_fields: List[str] = Field(default_factory=list)
    normalizations_applied: List[str] = Field(default_factory=list)
    repair_attempts: int = 0
    fallback_reason: Optional[str] = None
    execution_profile_id: Optional[str] = None
    execution_profile_source: Optional[str] = None
    max_output_tokens_source: Optional[str] = None
    reasoning_profile: Optional[str] = None
    verbosity_profile: Optional[str] = None
    output_mode: Optional[str] = None
    tool_mode: Optional[str] = None
    provider: Optional[str] = None
    translated_provider_params: Dict[str, Any] = Field(default_factory=dict)
    obs_snapshot: Optional[ExecutionObservabilitySnapshot] = None
    executed_provider_mode: str = "nominal"
    attempt_count: int = 1
    provider_error_code: Optional[str] = None
    breaker_state: Optional[str] = None
    breaker_scope: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=())


class GatewayResult(BaseModel):
    use_case: str
    request_id: str
    trace_id: str
    raw_output: str
    structured_output: Optional[Dict[str, Any]] = None
    usage: UsageInfo
    meta: GatewayMeta

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_log_dict(self) -> Dict[str, Any]:
        dump = self.model_dump()
        dump["raw_output"] = "[REDACTED]"
        if dump.get("structured_output"):
            dump["structured_output"] = {"status": "redacted_for_logging"}
        return dump


class RecoveryResult(BaseModel):
    result: Any
    repair_attempts: int = 0
    fallback_reason: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ReplayResult(BaseModel):
    use_case: str
    prompt_version_id: str
    persona_id: Optional[str] = None
    raw_output: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    validation_status: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    diff_vs_original: Optional[Dict[str, Any]] = None


class EvalFixtureResult(BaseModel):
    fixture_id: str
    status: str
    validation_errors: List[str] = Field(default_factory=list)
    field_mismatches: List[Dict[str, Any]] = Field(default_factory=list)


class EvalReport(BaseModel):
    use_case: str
    prompt_version_id: str
    total: int
    passed: int
    failed: int
    failure_rate: float
    blocked_publication: bool
    results: List[EvalFixtureResult]


class PerformanceSLO(BaseModel):
    p95_latency_ms: float
    p99_latency_ms: float
    min_success_rate: float
    max_protection_rate: float
    max_error_rate: float
    model_config = ConfigDict(frozen=True)


class PerformanceSLA(BaseModel):
    p95_latency_max_ms: float
    max_error_rate_threshold: float
    model_config = ConfigDict(frozen=True)


class PerformanceQualificationReport(BaseModel):
    active_snapshot_id: Optional[uuid.UUID] = None
    active_snapshot_version: Optional[str] = None
    manifest_entry_id: Optional[str] = None
    environment: str
    family: str
    profile: str
    total_requests: int
    success_count: int
    protection_count: int
    error_count: int
    error_rate: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rps: float
    budget_remaining: float
    verdict: Literal["go", "no-go", "go-with-constraints"]
    constraints: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime_provider.utcnow())


class GoldenRegressionResult(BaseModel):
    fixture_id: str
    family: str
    verdict: Literal["pass", "fail", "constrained", "invalid"]
    diffs_structure: Dict[str, Any] = Field(default_factory=dict)
    diffs_obs: Dict[str, Any] = Field(default_factory=dict)
    legacy_errors: List[str] = Field(default_factory=list)
    details: Optional[str] = None


class GoldenRegressionReport(BaseModel):
    active_snapshot_id: Optional[uuid.UUID] = None
    active_snapshot_version: Optional[str] = None
    manifest_entry_id: Optional[str] = None
    environment: str
    verdict: Literal["pass", "fail", "constrained", "invalid"]
    total: int
    passed: int
    failed: int
    constrained: int
    results: List[GoldenRegressionResult] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime_provider.utcnow())


class GatewayError(Exception):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        if self.error_code and "error_code" not in self.details:
            self.details["error_code"] = self.error_code
        super().__init__(self.message)


class UnknownUseCaseError(GatewayError):
    pass


class GatewayConfigError(GatewayError):
    pass


class PromptRenderError(GatewayError):
    pass


class InputValidationError(GatewayError):
    pass


class OutputValidationError(GatewayError):
    pass


__all__ = [
    "ComposedMessages",
    "ContextCompensationStatus",
    "ExecutionContext",
    "ExecutionFlags",
    "ExecutionMessage",
    "ExecutionObservabilitySnapshot",
    "ExecutionPathKind",
    "ExecutionUserInput",
    "FallbackStatus",
    "FallbackType",
    "GatewayConfigError",
    "GatewayError",
    "GatewayMeta",
    "GatewayRequest",
    "GatewayResult",
    "GoldenRegressionReport",
    "GoldenRegressionResult",
    "InputValidationError",
    "NatalExecutionInput",
    "LLMExecutionRequest",
    "MaxTokensSource",
    "OutputValidationError",
    "PerformanceSLA",
    "PerformanceSLO",
    "PerformanceQualificationReport",
    "PromptRenderError",
    "ReplayResult",
    "EvalFixtureResult",
    "EvalReport",
    "RecoveryResult",
    "ResolvedExecutionPlan",
    "ResponseFormatConfig",
    "UnknownUseCaseError",
    "UseCaseConfig",
    "EVIDENCE_ID_REGEX",
    "UsageInfo",
    "is_reasoning_model",
]
