"""OpenAI provider implementation."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Coroutine, TypeVar

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.ai_engine.providers.base import ProviderClient, ProviderResult

if TYPE_CHECKING:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion

    from app.ai_engine.schemas import ChatMessage

T = TypeVar("T")

logger = logging.getLogger(__name__)


class OpenAIClient(ProviderClient):
    """OpenAI API client implementation."""

    def __init__(self) -> None:
        self._async_client: "AsyncOpenAI | None" = None

    def _ensure_configured(self) -> None:
        """Ensure OpenAI is configured."""
        if not ai_engine_settings.is_openai_configured:
            raise ProviderNotConfiguredError("openai")

    def _get_model(self, model: str | None) -> str:
        """Resolve model name."""
        if model is None or model == "AUTO":
            return ai_engine_settings.openai_model_default
        return model

    async def _get_async_client(self) -> "AsyncOpenAI":
        """Get or create async OpenAI client."""
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

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "openai"

    async def _execute_with_retry(
        self,
        operation: str,
        func_factory: Callable[[], Coroutine[Any, Any, T]],
        *,
        timeout_seconds: int,
    ) -> T:
        """Execute an async function with exponential backoff retry."""
        self._ensure_configured()
        max_retries = ai_engine_settings.max_retries
        base_delay_ms = ai_engine_settings.retry_base_delay_ms
        max_delay_ms = ai_engine_settings.retry_max_delay_ms

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                coro = func_factory()
                return await asyncio.wait_for(coro, timeout=timeout_seconds)
            except asyncio.TimeoutError as err:
                logger.warning(
                    "openai_timeout operation=%s attempt=%d timeout=%ds",
                    operation,
                    attempt + 1,
                    timeout_seconds,
                )
                last_error = err
            except Exception as err:
                error_type = type(err).__name__
                error_msg = str(err)
                logger.warning(
                    "openai_error operation=%s attempt=%d error_type=%s error=%s",
                    operation,
                    attempt + 1,
                    error_type,
                    error_msg,
                )
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    raise UpstreamRateLimitError() from err
                last_error = err

            if attempt < max_retries:
                delay_ms = min(base_delay_ms * (2**attempt), max_delay_ms)
                jitter_ms = random.randint(0, delay_ms // 4)
                total_delay = (delay_ms + jitter_ms) / 1000.0
                logger.info(
                    "openai_retry operation=%s attempt=%d delay_ms=%d",
                    operation,
                    attempt + 1,
                    int(total_delay * 1000),
                )
                await asyncio.sleep(total_delay)

        if isinstance(last_error, asyncio.TimeoutError):
            raise UpstreamTimeoutError(timeout_seconds) from last_error
        raise UpstreamError(
            f"openai {operation} failed after {max_retries + 1} attempts",
            details={"error": str(last_error)},
        ) from last_error

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
    ) -> ProviderResult:
        """Generate text from a single prompt."""
        resolved_model = self._get_model(model)
        client = await self._get_async_client()

        async def do_completion() -> "ChatCompletion":
            return await client.chat.completions.create(
                model=resolved_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

        response = await self._execute_with_retry(
            "generate_text",
            do_completion,
            timeout_seconds=timeout_seconds,
        )

        text = response.choices[0].message.content or ""
        usage = response.usage
        return ProviderResult(
            text=text,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model=response.model,
        )

    async def chat(
        self,
        messages: list["ChatMessage"],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
        stream: bool = False,
    ) -> ProviderResult | AsyncIterator[str]:
        """Generate a chat completion."""
        resolved_model = self._get_model(model)
        client = await self._get_async_client()
        openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        if stream:
            return self._stream_chat(
                client,
                openai_messages,
                resolved_model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout_seconds=timeout_seconds,
            )

        async def do_chat() -> "ChatCompletion":
            return await client.chat.completions.create(
                model=resolved_model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        response = await self._execute_with_retry(
            "chat",
            do_chat,
            timeout_seconds=timeout_seconds,
        )

        text = response.choices[0].message.content or ""
        usage = response.usage
        return ProviderResult(
            text=text,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            model=response.model,
        )

    async def _stream_chat(
        self,
        client: "AsyncOpenAI",
        messages: list[dict[str, str]],
        model: str,
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        timeout_seconds: int = 30,
    ) -> AsyncIterator[str]:
        """
        Stream chat completion.

        Retries the initial connection on transient failures (up to max_retries).
        Once streaming has started, errors propagate without retry.

        Yields:
            Text deltas from the streaming response.

        Raises:
            UpstreamTimeoutError: If the request times out.
            UpstreamRateLimitError: If rate limit is exceeded.
            UpstreamError: For other upstream failures.
        """
        self._ensure_configured()
        max_retries = ai_engine_settings.max_retries
        base_delay_ms = ai_engine_settings.retry_base_delay_ms
        max_delay_ms = ai_engine_settings.retry_max_delay_ms

        last_error: Exception | None = None
        response = None

        for attempt in range(max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=True,
                    ),
                    timeout=timeout_seconds,
                )
                break
            except asyncio.TimeoutError as err:
                logger.warning(
                    "openai_timeout operation=stream_chat attempt=%d timeout=%ds",
                    attempt + 1,
                    timeout_seconds,
                )
                last_error = err
            except Exception as err:
                error_msg = str(err)
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    raise UpstreamRateLimitError() from err
                logger.warning(
                    "openai_error operation=stream_chat attempt=%d error=%s",
                    attempt + 1,
                    error_msg,
                )
                last_error = err

            if attempt < max_retries:
                delay_ms = min(base_delay_ms * (2**attempt), max_delay_ms)
                jitter_ms = random.randint(0, delay_ms // 4)
                await asyncio.sleep((delay_ms + jitter_ms) / 1000.0)

        if response is None:
            if isinstance(last_error, asyncio.TimeoutError):
                raise UpstreamTimeoutError(timeout_seconds) from last_error
            raise UpstreamError(
                f"openai stream_chat failed after {max_retries + 1} attempts",
                details={"error": str(last_error)},
            ) from last_error

        try:
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except asyncio.TimeoutError as err:
            raise UpstreamTimeoutError(timeout_seconds) from err
        except Exception as err:
            error_msg = str(err)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise UpstreamRateLimitError() from err
            raise UpstreamError(
                "openai streaming failed",
                details={"error": error_msg},
            ) from err
