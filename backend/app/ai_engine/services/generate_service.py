"""Generate service for AI text generation."""

from __future__ import annotations

import logging
from time import monotonic
from typing import TYPE_CHECKING

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.providers.base import ProviderResult
from app.ai_engine.services.context_compactor import compact_context, validate_context_size
from app.ai_engine.services.prompt_registry import PromptRegistry
from app.ai_engine.services.utils import calculate_cost, get_provider_client
from app.infra.observability.metrics import increment_counter, observe_duration

if TYPE_CHECKING:
    from app.ai_engine.schemas import GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)


async def generate_text(
    request: "GenerateRequest",
    *,
    request_id: str,
    trace_id: str,
    user_id: int,
) -> "GenerateResponse":
    """
    Generate text using the AI engine.

    Args:
        request: Generation request
        request_id: Request identifier for logging
        trace_id: Trace identifier for distributed tracing

    Returns:
        GenerateResponse with generated text and metadata
    """
    from app.ai_engine.schemas import GenerateMeta, GenerateResponse, UsageInfo

    start_time = monotonic()
    use_case = request.use_case
    locale = request.locale

    increment_counter(f"ai_engine_requests_total|use_case={use_case}|status=started", 1.0)

    logger.info(
        "ai_generate_start request_id=%s trace_id=%s user_id=%d use_case=%s locale=%s",
        request_id,
        trace_id,
        user_id,
        use_case,
        locale,
    )

    config = PromptRegistry.get_config(use_case)
    prompt = PromptRegistry.render_prompt(
        use_case=use_case,
        locale=locale,
        input_data=request.input,
        context=request.context,
    )

    validate_context_size(prompt)
    prompt = compact_context(prompt)

    provider_name = request.provider.name
    model = request.provider.model if request.provider.model != "AUTO" else config.model
    client = get_provider_client(provider_name)

    result: ProviderResult = await client.generate_text(
        prompt,
        model=model if model != "AUTO" else None,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        timeout_seconds=ai_engine_settings.timeout_seconds,
    )

    latency_ms = int((monotonic() - start_time) * 1000)
    usage = UsageInfo(
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        total_tokens=result.total_tokens,
        estimated_cost_usd=calculate_cost(result.input_tokens, result.output_tokens),
    )

    increment_counter(f"ai_engine_requests_total|use_case={use_case}|status=success", 1.0)
    increment_counter("ai_engine_tokens_total|direction=input", float(result.input_tokens))
    increment_counter("ai_engine_tokens_total|direction=output", float(result.output_tokens))
    observe_duration("ai_engine_latency_seconds", latency_ms / 1000.0)
    observe_duration(f"ai_engine_latency_seconds|use_case={use_case}", latency_ms / 1000.0)

    logger.info(
        "ai_generate_complete request_id=%s trace_id=%s user_id=%d use_case=%s "
        "latency_ms=%d input_tokens=%d output_tokens=%d cost_usd=%.4f",
        request_id,
        trace_id,
        user_id,
        use_case,
        latency_ms,
        result.input_tokens,
        result.output_tokens,
        usage.estimated_cost_usd,
    )

    return GenerateResponse(
        request_id=request_id,
        trace_id=trace_id,
        provider=client.provider_name,
        model=result.model,
        text=result.text,
        usage=usage,
        meta=GenerateMeta(cached=False, latency_ms=latency_ms),
    )
