from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.llm_orchestration.models import (
    GatewayError,
    GatewayMeta,
    GatewayResult,
    UsageInfo,
    is_reasoning_model,
)

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from openai.types.responses import Response

logger = logging.getLogger(__name__)


class ResponsesClient:
    """Wrapper for the OpenAI Responses API (POST /v1/responses)."""

    def __init__(self) -> None:
        self._async_client: "AsyncOpenAI | None" = None

    def _ensure_configured(self) -> None:
        if not ai_engine_settings.is_openai_configured:
            raise ProviderNotConfiguredError("openai")

    async def _get_async_client(self) -> "AsyncOpenAI":
        if self._async_client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as err:
                raise UpstreamError(
                    "openai package not installed",
                    details={"package": "openai"},
                ) from err
            self._async_client = AsyncOpenAI(api_key=ai_engine_settings.openai_api_key)
        return self._async_client

    @staticmethod
    def _to_typed_content_blocks(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert simple role/content messages to typed content blocks required by GPT-5.
        Format: {"role": "...", "content": [{"type": "input_text", "text": "..."}]}

        Idempotent: if content is already a list (typed blocks), returns as-is.
        Preserves all extra fields present on the message dict.
        """
        result = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                result.append({**msg, "content": [{"type": "input_text", "text": content}]})
            else:
                result.append(msg)
        return result

    async def execute(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_output_tokens: int = 1000,
        timeout_seconds: int = 30,
        request_id: str = "",
        trace_id: str = "",
        use_case: str = "",
        reasoning_effort: Optional[str] = None,
        verbosity: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> GatewayResult:
        """Execute a request via the Responses API with retry logic."""
        self._ensure_configured()
        client = await self._get_async_client()

        start_time = time.monotonic()

        async def do_create() -> "Response":
            # 1. GPT-5 requires typed content blocks.
            is_gpt5 = model == "gpt-5" or model.startswith("gpt-5-")
            effective_input = self._to_typed_content_blocks(messages) if is_gpt5 else messages

            # 2. Base parameters
            params: Dict[str, Any] = {
                "model": model,
                "input": effective_input,  # type: ignore
                "max_output_tokens": max_output_tokens,
            }

            # 3. Reasoning and Temperature
            # GPT-5 and o-series (o1, o3, o4) use reasoning config instead of temperature.
            is_reasoning = is_reasoning_model(model)

            if is_reasoning:
                if reasoning_effort:
                    params["reasoning"] = {"effort": reasoning_effort}
            else:
                params["temperature"] = temperature

            text_config: Dict[str, Any] = {}
            if is_gpt5 and verbosity:
                text_config["verbosity"] = verbosity

            if response_format:
                # Responses API uses `text.format` with a flat structure, whereas
                # Chat Completions API nests details under `json_schema`.
                # Transform: {"type": "json_schema", "json_schema": {"name": ..., "schema": ..., "strict": ...}}  # noqa: E501
                #        →   {"type": "json_schema", "name": ..., "schema": ..., "strict": ...}
                fmt = dict(response_format)
                if fmt.get("type") == "json_schema" and "json_schema" in fmt:
                    nested = fmt.pop("json_schema")
                    fmt.update(nested)
                text_config["format"] = fmt

            if text_config:
                params["text"] = text_config

            # Add tracing headers for observability
            headers: Dict[str, str] = {}
            if request_id:
                headers["x-request-id"] = request_id
            if trace_id:
                headers["x-trace-id"] = trace_id
            if use_case:
                headers["x-use-case"] = use_case
            if headers:
                params["extra_headers"] = headers

            return await client.responses.create(**params)

        try:
            response = await self._execute_with_retry(
                "responses_create", do_create, timeout_seconds=timeout_seconds
            )
        except Exception as err:
            if isinstance(err, (UpstreamRateLimitError, UpstreamTimeoutError, UpstreamError)):
                raise err
            raise GatewayError(
                f"Unexpected provider error: {str(err)}", details={"error": str(err)}
            )

        latency_ms = int((time.monotonic() - start_time) * 1000)

        # Use the SDK convenience property which handles all output_text aggregation.
        output_text = response.output_text if hasattr(response, "output_text") else ""

        usage = UsageInfo(
            input_tokens=response.usage.input_tokens if response.usage else 0,
            output_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            estimated_cost_usd=0.0,  # Will be calculated in gateway or service
        )

        # Parse structured output when response_format was requested
        structured_output: Any = None
        if response_format is not None and output_text:
            try:
                structured_output = json.loads(output_text)
            except (json.JSONDecodeError, ValueError):
                pass

        return GatewayResult(
            use_case=use_case,
            request_id=request_id,
            trace_id=trace_id,
            raw_output=output_text,
            structured_output=structured_output,
            usage=usage,
            meta=GatewayMeta(
                latency_ms=latency_ms,
                model=response.model,
                cached=False,  # Responses API might have cache info elsewhere
            ),
        )

    async def _execute_with_retry(
        self,
        operation: str,
        func_factory: Any,
        *,
        timeout_seconds: int,
    ) -> Any:
        """Reuse retry logic from OpenAIClient pattern."""
        max_retries = ai_engine_settings.max_retries
        base_delay_ms = ai_engine_settings.retry_base_delay_ms
        max_delay_ms = ai_engine_settings.retry_max_delay_ms

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return await asyncio.wait_for(func_factory(), timeout=timeout_seconds)
            except asyncio.TimeoutError as err:
                logger.warning(
                    "responses_timeout operation=%s attempt=%d timeout=%ds",
                    operation,
                    attempt + 1,
                    timeout_seconds,
                )
                last_error = err
            except Exception as err:
                # Handle OpenAI SDK-specific exceptions (non-retryable)
                if isinstance(err, RateLimitError):
                    raise UpstreamRateLimitError() from err
                if isinstance(err, APITimeoutError):
                    raise UpstreamTimeoutError(timeout_seconds) from err
                if isinstance(err, APIConnectionError):
                    raise UpstreamError(
                        f"Connection error: {str(err)}",
                        details={"kind": "connection_error"},
                    ) from err

                logger.warning(
                    "responses_error operation=%s attempt=%d error=%s",
                    operation,
                    attempt + 1,
                    str(err),
                )
                last_error = err

            if attempt < max_retries:
                delay_ms = min(base_delay_ms * (2**attempt), max_delay_ms)
                jitter_ms = random.randint(0, delay_ms // 4)
                await asyncio.sleep((delay_ms + jitter_ms) / 1000.0)

        if isinstance(last_error, asyncio.TimeoutError):
            raise UpstreamTimeoutError(timeout_seconds) from last_error
        raise UpstreamError(
            f"responses {operation} failed after {max_retries + 1} attempts",
            details={"error": str(last_error)},
        ) from last_error
