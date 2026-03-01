from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.llm_orchestration.models import GatewayError, GatewayMeta, GatewayResult, UsageInfo

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
        response_format: Optional[Dict[str, Any]] = None,
    ) -> GatewayResult:
        """Execute a request via the Responses API with retry logic."""
        self._ensure_configured()
        client = await self._get_async_client()

        start_time = time.monotonic()

        async def do_create() -> "Response":
            # The Responses API uses 'input' for the conversation history.
            params = {
                "model": model,
                "input": messages,  # type: ignore
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
            if response_format:
                params["response_format"] = response_format

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

        # Extract content from response.
        # Response object structure for Responses API:
        # response.output is a list of items. We want the text content.
        output_text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if item.type == "message" and hasattr(item, "content"):
                    for part in item.content:
                        if part.type == "text":
                            output_text += part.text
                elif item.type == "text":  # Some items might be direct text
                    output_text += item.text

        usage = UsageInfo(
            input_tokens=response.usage.input_tokens if response.usage else 0,
            output_tokens=response.usage.output_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            estimated_cost_usd=0.0,  # Will be calculated in gateway or service
        )

        return GatewayResult(
            use_case=use_case,
            request_id=request_id,
            trace_id=trace_id,
            raw_output=output_text,
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
                error_msg = str(err).lower()
                if "rate_limit" in error_msg or "429" in error_msg:
                    raise UpstreamRateLimitError() from err
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
