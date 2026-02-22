"""Chat service for AI chat completions with streaming support."""

from __future__ import annotations

import json
import logging
from time import monotonic
from typing import TYPE_CHECKING, AsyncIterator

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.providers.base import ProviderResult
from app.ai_engine.services.context_compactor import compact_context, validate_context_size
from app.ai_engine.services.prompt_registry import PromptRegistry
from app.ai_engine.services.utils import calculate_cost, get_provider_client
from app.infra.observability.metrics import increment_counter, observe_duration

if TYPE_CHECKING:
    from app.ai_engine.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


def _build_system_prompt(request: "ChatRequest") -> str:
    """Build system prompt from chat context."""
    from app.ai_engine.schemas import GenerateContext, GenerateInput

    context = GenerateContext(
        natal_chart_summary=request.context.natal_chart_summary,
        extra={"memory": json.dumps(request.context.memory)} if request.context.memory else None,
    )
    input_data = GenerateInput()

    return PromptRegistry.render_prompt(
        use_case="chat",
        locale=request.locale,
        input_data=input_data,
        context=context,
    )


async def chat(
    request: "ChatRequest",
    *,
    request_id: str,
    trace_id: str,
) -> "ChatResponse":
    """
    Generate a chat completion (non-streaming).

    Args:
        request: Chat request
        request_id: Request identifier for logging
        trace_id: Trace identifier for distributed tracing

    Returns:
        ChatResponse with generated text and metadata
    """
    from app.ai_engine.schemas import ChatMessage, ChatResponse, GenerateMeta, UsageInfo

    start_time = monotonic()
    increment_counter("ai_engine_requests_total|use_case=chat|status=started", 1.0)

    logger.info(
        "ai_chat_start request_id=%s trace_id=%s locale=%s message_count=%d",
        request_id,
        trace_id,
        request.locale,
        len(request.messages),
    )

    messages = list(request.messages)
    has_system = any(m.role == "system" for m in messages)
    if not has_system:
        system_prompt = _build_system_prompt(request)
        validate_context_size(system_prompt)
        system_prompt = compact_context(system_prompt)
        messages.insert(0, ChatMessage(role="system", content=system_prompt))

    provider_name = request.provider.name
    model = request.provider.model
    client = get_provider_client(provider_name)
    config = PromptRegistry.get_config("chat")

    result: ProviderResult = await client.chat(
        messages,
        model=model if model != "AUTO" else None,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        timeout_seconds=ai_engine_settings.timeout_seconds,
        stream=False,
    )

    latency_ms = int((monotonic() - start_time) * 1000)
    usage = UsageInfo(
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        total_tokens=result.total_tokens,
        estimated_cost_usd=calculate_cost(result.input_tokens, result.output_tokens),
    )

    increment_counter("ai_engine_requests_total|use_case=chat|status=success", 1.0)
    increment_counter("ai_engine_tokens_total|direction=input", float(result.input_tokens))
    increment_counter("ai_engine_tokens_total|direction=output", float(result.output_tokens))
    observe_duration("ai_engine_latency_seconds", latency_ms / 1000.0)
    observe_duration("ai_engine_latency_seconds|use_case=chat", latency_ms / 1000.0)

    logger.info(
        "ai_chat_complete request_id=%s trace_id=%s "
        "latency_ms=%d input_tokens=%d output_tokens=%d cost_usd=%.4f",
        request_id,
        trace_id,
        latency_ms,
        result.input_tokens,
        result.output_tokens,
        usage.estimated_cost_usd,
    )

    return ChatResponse(
        request_id=request_id,
        trace_id=trace_id,
        provider=client.provider_name,
        model=result.model,
        text=result.text,
        usage=usage,
        meta=GenerateMeta(cached=False, latency_ms=latency_ms),
    )


async def chat_stream(
    request: "ChatRequest",
    *,
    request_id: str,
    trace_id: str,
) -> AsyncIterator[str]:
    """
    Generate a streaming chat completion.

    Yields SSE-formatted chunks:
    - data: {"delta": "..."}
    - data: {"done": true, "text": "..."}

    Args:
        request: Chat request
        request_id: Request identifier for logging
        trace_id: Trace identifier for distributed tracing

    Yields:
        SSE-formatted strings
    """
    from app.ai_engine.schemas import ChatMessage

    start_time = monotonic()
    increment_counter("ai_engine_requests_total|use_case=chat_stream|status=started", 1.0)

    logger.info(
        "ai_chat_stream_start request_id=%s trace_id=%s locale=%s message_count=%d",
        request_id,
        trace_id,
        request.locale,
        len(request.messages),
    )

    messages = list(request.messages)
    has_system = any(m.role == "system" for m in messages)
    if not has_system:
        system_prompt = _build_system_prompt(request)
        validate_context_size(system_prompt)
        system_prompt = compact_context(system_prompt)
        messages.insert(0, ChatMessage(role="system", content=system_prompt))

    provider_name = request.provider.name
    model = request.provider.model
    client = get_provider_client(provider_name)
    config = PromptRegistry.get_config("chat")

    full_text = ""
    chunk_count = 0

    try:
        stream = await client.chat(
            messages,
            model=model if model != "AUTO" else None,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout_seconds=ai_engine_settings.timeout_seconds,
            stream=True,
        )

        async for delta in stream:
            full_text += delta
            chunk_count += 1
            yield f"data: {json.dumps({'delta': delta})}\n\n"

        latency_ms = int((monotonic() - start_time) * 1000)
        yield f"data: {json.dumps({'done': True, 'text': full_text})}\n\n"

        increment_counter("ai_engine_requests_total|use_case=chat_stream|status=success", 1.0)
        observe_duration("ai_engine_latency_seconds", latency_ms / 1000.0)
        observe_duration("ai_engine_latency_seconds|use_case=chat_stream", latency_ms / 1000.0)

        logger.info(
            "ai_chat_stream_complete request_id=%s trace_id=%s "
            "latency_ms=%d chunks=%d text_length=%d",
            request_id,
            trace_id,
            latency_ms,
            chunk_count,
            len(full_text),
        )

    except Exception as err:
        increment_counter("ai_engine_requests_total|use_case=chat_stream|status=error", 1.0)
        logger.error(
            "ai_chat_stream_error request_id=%s trace_id=%s error=%s",
            request_id,
            trace_id,
            str(err),
        )
        error_data = {"error": {"type": type(err).__name__, "message": str(err)}}
        yield f"data: {json.dumps(error_data)}\n\n"
        raise
