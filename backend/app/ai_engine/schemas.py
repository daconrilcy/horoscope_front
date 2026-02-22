"""AI Engine Pydantic schemas for request/response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Provider configuration for AI requests."""

    name: str = Field(default="openai", description="Provider name")
    model: str = Field(default="AUTO", description="Model name or AUTO for default")


class OutputConfig(BaseModel):
    """Output configuration for AI requests."""

    format: str = Field(default="text", description="Output format")
    stream: bool = Field(default=False, description="Enable SSE streaming")


class InputConstraints(BaseModel):
    """Constraints for input handling."""

    max_chars: int | None = Field(default=None, description="Maximum characters in response")


class GenerateInput(BaseModel):
    """Input section of generate request."""

    question: str | None = Field(default=None, description="User question or prompt")
    tone: str = Field(default="warm", description="Response tone")
    constraints: InputConstraints = Field(default_factory=InputConstraints)


class GenerateContext(BaseModel):
    """Context section of generate request."""

    natal_chart_summary: str | None = Field(default=None, description="Natal chart summary")
    birth_data: dict[str, str] | None = Field(default=None, description="Birth data")
    extra: dict[str, str] | None = Field(default=None, description="Extra context")


class GenerateRequest(BaseModel):
    """Request body for POST /v1/ai/generate."""

    use_case: str = Field(..., description="Use case identifier")
    locale: str = Field(default="fr-FR", description="Locale for response")
    user_id: str | None = Field(default=None, description="User identifier")
    request_id: str | None = Field(default=None, description="Request identifier")
    trace_id: str | None = Field(default=None, description="Trace identifier")
    input: GenerateInput = Field(default_factory=GenerateInput)
    context: GenerateContext = Field(default_factory=GenerateContext)
    output: OutputConfig = Field(default_factory=OutputConfig)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)


class UsageInfo(BaseModel):
    """Token usage information."""

    input_tokens: int = Field(default=0, description="Input tokens used")
    output_tokens: int = Field(default=0, description="Output tokens generated")
    total_tokens: int = Field(default=0, description="Total tokens")
    estimated_cost_usd: float = Field(default=0.0, description="Estimated cost in USD")


class GenerateMeta(BaseModel):
    """Metadata for generate response."""

    cached: bool = Field(default=False, description="Whether response was cached")
    latency_ms: int = Field(default=0, description="Response latency in milliseconds")


class GenerateResponse(BaseModel):
    """Response body for POST /v1/ai/generate."""

    request_id: str = Field(..., description="Request identifier")
    trace_id: str = Field(..., description="Trace identifier")
    provider: str = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")
    text: str = Field(..., description="Generated text")
    usage: UsageInfo = Field(default_factory=UsageInfo)
    meta: GenerateMeta = Field(default_factory=GenerateMeta)


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: system, user, assistant")
    content: str = Field(..., description="Message content")


class ChatContext(BaseModel):
    """Context for chat requests."""

    natal_chart_summary: str | None = Field(default=None, description="Natal chart summary")
    memory: dict[str, str] | None = Field(default=None, description="Memory/style preferences")


class ChatRequest(BaseModel):
    """Request body for POST /v1/ai/chat."""

    conversation_id: str | None = Field(default=None, description="Conversation identifier")
    locale: str = Field(default="fr-FR", description="Locale for response")
    user_id: str | None = Field(default=None, description="User identifier")
    request_id: str | None = Field(default=None, description="Request identifier")
    trace_id: str | None = Field(default=None, description="Trace identifier")
    messages: list[ChatMessage] = Field(..., description="Conversation messages")
    context: ChatContext = Field(default_factory=ChatContext)
    output: OutputConfig = Field(default_factory=OutputConfig)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)


class ChatResponse(BaseModel):
    """Response body for POST /v1/ai/chat (non-streaming)."""

    request_id: str = Field(..., description="Request identifier")
    trace_id: str = Field(..., description="Trace identifier")
    provider: str = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")
    text: str = Field(..., description="Generated text")
    usage: UsageInfo = Field(default_factory=UsageInfo)
    meta: GenerateMeta = Field(default_factory=GenerateMeta)


class StreamChunk(BaseModel):
    """SSE stream chunk for chat."""

    delta: str | None = Field(default=None, description="Text delta")
    done: bool = Field(default=False, description="Whether stream is complete")
    text: str | None = Field(default=None, description="Full text when done")


class ErrorResponse(BaseModel):
    """Error response body."""

    error: dict[str, object] = Field(..., description="Error details")
