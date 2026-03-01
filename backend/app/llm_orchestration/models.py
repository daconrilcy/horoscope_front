from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UseCaseConfig(BaseModel):
    """Configuration for a specific LLM use case."""

    model: str
    temperature: float = 0.7
    max_output_tokens: int = 1000
    system_core_key: str = "default_v1"
    developer_prompt: str
    prompt_version_id: str = "hardcoded-v1"
    persona_strategy: str = "optional"
    safety_profile: str = "astrology"
    input_schema: Optional[Dict[str, Any]] = None
    output_schema_id: Optional[str] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    fallback_use_case: Optional[str] = None


class ComposedMessages(BaseModel):
    """The 4-layer composed messages for the Responses API."""

    messages: List[Dict[str, str]]


class GatewayRequest(BaseModel):
    """Request to the LLM Gateway."""

    use_case: str
    user_input: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    trace_id: str


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
    output_schema_id: Optional[str] = None
    validation_status: str = "valid"  # valid, repaired, fallback, error, omitted
    repair_attempted: bool = False
    fallback_triggered: bool = False
    validation_errors: Optional[List[str]] = None


class GatewayResult(BaseModel):
    """Result from the LLM Gateway."""

    use_case: str
    request_id: str
    trace_id: str
    raw_output: str
    structured_output: Optional[Dict[str, Any]] = None
    usage: UsageInfo
    meta: GatewayMeta


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
