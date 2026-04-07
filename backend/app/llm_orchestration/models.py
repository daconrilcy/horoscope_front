from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

EVIDENCE_ID_REGEX = r"^[A-Z0-9_\.:-]{3,80}$"

# Shared reasoning-model detection — single source of truth for gateway and provider.
# L1 fix: "gpt-5-" prefix (with dash) avoids false match on hypothetical "gpt-50", "gpt-500".
_REASONING_MODEL_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-")
_REASONING_MODEL_EXACT = {"o1", "o3", "o4", "gpt-5"}


def is_reasoning_model(model: str) -> bool:
    """Return True if model uses reasoning config (o-series or GPT-5) instead of temperature."""
    return model in _REASONING_MODEL_EXACT or model.startswith(_REASONING_MODEL_PREFIXES)


class UseCaseConfig(BaseModel):
    """Configuration for a specific LLM use case."""

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
    """The 4-layer composed messages for the Responses API."""

    # Dict[str, Any] : content peut être str (gpt-4o) ou List[TypedBlock] (gpt-5)
    messages: List[Dict[str, Any]]


class GatewayRequest(BaseModel):
    """Request to the LLM Gateway."""

    use_case: str
    user_input: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    trace_id: str


class ExecutionMessage(BaseModel):
    """A single message in the conversational history."""

    role: Literal["user", "assistant", "system"]
    content: str
    content_blocks: Optional[List[Dict[str, Any]]] = None
    """Réservé aux blocs multi-modaux (GPT-5+). Si renseigné, prend la priorité sur content
    lors de la composition des messages dans ResponsesClient."""

    model_config = ConfigDict(frozen=True)


class ExecutionUserInput(BaseModel):
    """Structured and typed user input for an LLM execution."""

    use_case: str
    locale: str = "fr-FR"
    """Format BCP-47 (ex: 'fr-FR', 'en-US')."""

    message: Optional[str] = None
    question: Optional[str] = None
    situation: Optional[str] = None
    conversation_id: Optional[str] = None
    persona_id_override: Optional[str] = None

    @property
    def last_user_msg(self) -> Optional[str]:
        """Alias for question or message, used by prompt renderer."""
        return self.question or self.message


class ExecutionContext(BaseModel):
    """Contextual data for an LLM execution, including history and domain data."""

    history: List[ExecutionMessage] = Field(default_factory=list)
    natal_data: Optional[Dict[str, Any]] = None
    chart_json: Optional[str] = None
    precision_level: Optional[str] = None
    astro_context: Optional[Any] = None
    extra_context: Dict[str, Any] = Field(default_factory=dict)
    """Extension transitoire pour payloads métier non structurants.
    Interdit pour tout nouveau champ structurant. Destiné à être progressivement vidé."""


class ExecutionFlags(BaseModel):
    """Operational flags for the orchestration pipeline."""

    is_repair_call: bool = False
    skip_common_context: bool = False
    test_fallback_active: bool = False
    validation_strict: bool = False
    evidence_catalog: Optional[Union[List[str], Dict[str, List[str]]]] = None
    prompt_version_id_override: Optional[str] = None
    visited_use_cases: List[str] = Field(default_factory=list)
    """Usage interne plateforme uniquement — ne pas renseigner côté appelant métier."""


class ExecutionOverrides(BaseModel):
    """
    Surcharges de stratégie use case. Sémantique contractuelle :
    - USAGE AUTORISÉ : migrations, tests d'infrastructure, use cases expérimentaux non encore en config DB.
    - USAGE INTERDIT : services métier normaux (chat, guidance, natal en production stable).
    - EFFET : les valeurs non-None remplacent celles résolues par _resolve_config() dans ResolvedExecutionPlan.
    - JOURNALISATION : toute surcharge effective est tracée dans ResolvedExecutionPlan.to_log_dict()
      sous une clé 'overrides_applied' pour auditabilité.
    - RÈGLE : un nouveau use case ne doit JAMAIS dépendre d'ExecutionOverrides pour fonctionner
      nominalement — la config DB doit être sa source de vérité.
    """

    interaction_mode: Optional[Literal["structured", "chat"]] = None
    user_question_policy: Optional[Literal["none", "optional", "required"]] = None
    _applied_by: Optional[str] = None  # Internal audit identifier


class NatalExecutionInput(BaseModel):
    """Structured input for natal interpretation requests (Story 66.7)."""

    use_case_key: str
    locale: str = "fr-FR"
    level: Literal["short", "complete"]
    chart_json: str
    natal_data: Dict[str, Any]
    evidence_catalog: Union[List[str], Dict[str, List[str]]]
    persona_id: Optional[str] = None
    validation_strict: bool = True
    question: Optional[str] = None
    astro_context: Optional[str] = None
    module: Optional[str] = None
    variant_code: Optional[str] = None
    user_id: int
    request_id: str
    trace_id: str


class LLMExecutionRequest(BaseModel):
    """Canonical request contract for the LLM Gateway."""

    user_input: ExecutionUserInput
    context: ExecutionContext = Field(default_factory=ExecutionContext)
    flags: ExecutionFlags = Field(default_factory=ExecutionFlags)
    overrides: Optional[ExecutionOverrides] = None

    # Runtime identifiers (not infrastructure)
    user_id: Optional[int] = None
    request_id: str
    trace_id: str


class ResponseFormatConfig(BaseModel):
    """Configuration for the LLM response format."""

    type: Literal["json_schema", "text"] = "text"
    json_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema")

    model_config = ConfigDict(populate_by_name=True)


class ResolvedExecutionPlan(BaseModel):
    """Artifact representing the final resolved configuration for an LLM call."""

    # Model resolution
    model_id: str
    model_source: Literal["os_granular", "os_legacy", "config", "stub"]

    # Prompts & Persona
    prompt_version_id: Optional[str] = None
    rendered_developer_prompt: str
    system_core: str
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    persona_block: Optional[str] = None

    # Schemas
    output_schema_id: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    output_schema_version: str = "v1"
    input_schema: Optional[Dict[str, Any]] = None

    # Strategy & Strategy resolution
    interaction_mode: Literal["structured", "chat"]
    user_question_policy: Literal["none", "optional", "required"]
    overrides_applied: Dict[str, Any] = Field(default_factory=dict)

    # Provider params
    temperature: float
    max_output_tokens: int
    response_format: Optional[ResponseFormatConfig] = None
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None

    # Quality metadata
    context_quality: str = "unknown"


class RecoveryResult(BaseModel):
    """Artifact representing the result of a repair or fallback operation."""

    result: Any
    repair_attempts: int = 0
    fallback_reason: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UsageInfo(BaseModel):
    """Token usage information."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class GatewayMeta(BaseModel):
    """Metadata for the gateway result."""

    latency_ms: int
    cached: bool = False
    prompt_version_id: str = "hardcoded-v1"
    persona_id: Optional[str] = None
    model: str
    model_override_active: bool = False
    output_schema_id: Optional[str] = None
    schema_version: Optional[str] = "v1"  # v1, v2
    validation_status: str = "valid"  # valid, repair_success, fallback, error, omitted
    repair_attempted: bool = False
    fallback_triggered: bool = False
    validation_errors: Optional[List[str]] = None

    # Enriched Telemetry (Story 66.6)
    execution_path: Literal["nominal", "repaired", "fallback_use_case", "test_fallback"] = "nominal"
    context_quality: str = "unknown"
    missing_context_fields: List[str] = Field(default_factory=list)
    normalizations_applied: List[str] = Field(default_factory=list)
    repair_attempts: int = 0
    fallback_reason: Optional[str] = None


class GatewayResult(BaseModel):
    """Result from the LLM Gateway."""

    use_case: str
    request_id: str
    trace_id: str
    raw_output: str
    structured_output: Optional[Dict[str, Any]] = None
    usage: UsageInfo
    meta: GatewayMeta

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_log_dict(self) -> Dict[str, Any]:
        """
        Returns a JSON-serializable dict for logging, excluding verbose artifacts.
        (AC4: filter verbose fields)
        """
        dump = self.model_dump()
        # The meta and result are already fairly clean, but we can filter if needed.
        # Actually, the user report said it was missing from GatewayResult.
        return dump


class ReplayResult(BaseModel):
    """Result from a prompt replay."""

    use_case: str
    prompt_version_id: str
    persona_id: Optional[str] = None
    raw_output: str
    structured_output: Optional[Dict[str, Any]] = None
    validation_status: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    diff_vs_original: Optional[Dict[str, Any]] = None


class EvalFixtureResult(BaseModel):
    fixture_id: str
    status: str  # passed, failed
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


class GatewayError(Exception):
    """Base error for LLM Gateway."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class UnknownUseCaseError(GatewayError):
    """Raised when an unknown use case is requested."""

    pass


class GatewayConfigError(GatewayError):
    """Raised when use case configuration is missing or invalid."""

    pass


class PromptRenderError(GatewayError):
    """Raised when prompt rendering fails (e.g., missing variables)."""

    pass


class InputValidationError(GatewayError):
    """Raised when user input violates the use case JSON schema."""

    pass


class OutputValidationError(GatewayError):
    """Raised when LLM output fails schema validation after repair/fallback."""

    pass
