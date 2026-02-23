"""Generate service for AI text generation."""

from __future__ import annotations

import json
import logging
from time import monotonic
from typing import TYPE_CHECKING

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.providers.base import ProviderResult
from app.ai_engine.services.cache_service import CachedResponse, CacheService
from app.ai_engine.services.context_compactor import compact_context, validate_context_size
from app.ai_engine.services.log_sanitizer import sanitize_request_for_logging
from app.ai_engine.services.prompt_registry import PromptRegistry
from app.ai_engine.services.utils import calculate_cost, get_provider_client
from app.infra.observability.metrics import increment_counter, observe_duration

if TYPE_CHECKING:
    from app.ai_engine.schemas import GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)

CACHEABLE_TEMPERATURE_THRESHOLD = 0.0


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
        user_id: User identifier for audit tracing

    Returns:
        GenerateResponse with generated text and metadata
    """
    from app.ai_engine.schemas import GenerateMeta, GenerateResponse, UsageInfo

    start_time = monotonic()
    use_case = request.use_case
    locale = request.locale

    increment_counter(f"ai_engine_requests_total|use_case={use_case}|status=started", 1.0)

    input_dict = request.input.model_dump()
    context_dict = request.context.model_dump()

    log_payload = sanitize_request_for_logging(
        use_case=use_case,
        user_id=user_id,
        request_id=request_id,
        trace_id=trace_id,
        input_data=input_dict,
        context=context_dict,
        locale=locale,
    )
    logger.info("ai_generate_start %s", json.dumps(log_payload))

    config = PromptRegistry.get_config(use_case)
    is_cacheable = config.temperature <= CACHEABLE_TEMPERATURE_THRESHOLD

    cache_service = CacheService.get_instance()
    cached = None
    if is_cacheable:
        cached = cache_service.get_cached_response(use_case, input_dict, context_dict)
    if cached:
        latency_ms = int((monotonic() - start_time) * 1000)
        usage = UsageInfo(
            input_tokens=cached.input_tokens,
            output_tokens=cached.output_tokens,
            total_tokens=cached.total_tokens,
            estimated_cost_usd=0.0,
        )
        increment_counter(f"ai_engine_requests_total|use_case={use_case}|status=cached", 1.0)
        increment_counter("ai_engine_cache_hits_total", 1.0)
        logger.info(
            "ai_generate_cached %s",
            json.dumps({
                "request_id": request_id,
                "trace_id": trace_id,
                "user_id": str(user_id),
                "use_case": use_case,
                "latency_ms": latency_ms,
                "status": "success",
                "tokens_used": cached.total_tokens,
                "cached": True,
            }),
        )
        return GenerateResponse(
            request_id=request_id,
            trace_id=trace_id,
            provider="openai",
            model=cached.model,
            text=cached.text,
            usage=usage,
            meta=GenerateMeta(cached=True, latency_ms=latency_ms),
        )

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

    if is_cacheable:
        cache_service.cache_response(
            use_case,
            input_dict,
            context_dict,
            CachedResponse(
                text=result.text,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                total_tokens=result.total_tokens,
                model=result.model,
            ),
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
        "ai_generate_complete %s",
        json.dumps({
            "request_id": request_id,
            "trace_id": trace_id,
            "user_id": str(user_id),
            "use_case": use_case,
            "latency_ms": latency_ms,
            "status": "success",
            "tokens_used": result.total_tokens,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "cost_usd": round(usage.estimated_cost_usd, 6),
            "cached": False,
        }),
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
