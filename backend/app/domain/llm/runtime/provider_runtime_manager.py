import asyncio
import logging
import random
from typing import Any, Dict, List, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    RateLimitError,
)

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    RetryBudgetExhaustedError,
    UpstreamAuthError,
    UpstreamBadRequestError,
    UpstreamCircuitOpenError,
    UpstreamConnectionError,
    UpstreamRateLimitError,
    UpstreamServerError,
    UpstreamTimeoutError,
)
from app.llm_orchestration.models import GatewayResult
from app.llm_orchestration.providers.circuit_breaker import get_circuit_breaker
from app.llm_orchestration.providers.responses_client import ResponsesClient

logger = logging.getLogger(__name__)


class ProviderRuntimeManager:
    """
    Hardened runtime layer for provider calls.
    Manages retries, circuit breaking, and error classification for OpenAI.
    """

    def __init__(self, responses_client: Optional[ResponsesClient] = None):
        self.client = responses_client or ResponsesClient()

    def _get_timeout(self, family: Optional[str]) -> int:
        """Resolve family-specific timeout from settings."""
        if family == "chat":
            return ai_engine_settings.timeout_seconds_chat
        if family == "guidance":
            return ai_engine_settings.timeout_seconds_guidance
        if family == "natal":
            return ai_engine_settings.timeout_seconds_natal
        if family == "horoscope_daily":
            return ai_engine_settings.timeout_seconds_horoscope_daily
        return ai_engine_settings.timeout_seconds

    async def execute_with_resilience(
        self,
        messages: List[Dict[str, str]],
        model: str,
        family: Optional[str] = None,
        **kwargs: Any,
    ) -> GatewayResult:
        """
        Execute an OpenAI call with circuit breaking and bounded retries.
        """
        provider = "openai"
        effective_family = family or "global"
        breaker = get_circuit_breaker(
            provider=provider,
            family=effective_family,
            failure_threshold=ai_engine_settings.circuit_breaker_failure_threshold,
            recovery_timeout_sec=ai_engine_settings.circuit_breaker_recovery_timeout_sec,
        )

        if not breaker.allow_request():
            logger.warning(
                "provider_circuit_open provider=%s family=%s", provider, effective_family
            )
            open_exc = UpstreamCircuitOpenError(provider, effective_family)
            setattr(open_exc, "_executed_provider_mode", "circuit_open")
            setattr(open_exc, "_attempt_count", 0)
            setattr(open_exc, "_breaker_state", breaker.state.value)
            setattr(open_exc, "_breaker_scope", f"{provider}:{effective_family}")
            setattr(open_exc, "_provider_error_code", open_exc.error_type)
            raise open_exc

        max_retries = ai_engine_settings.max_retries
        base_delay_ms = ai_engine_settings.retry_base_delay_ms
        max_delay_ms = ai_engine_settings.retry_max_delay_ms
        timeout_seconds = self._get_timeout(family)

        last_error: Exception | None = None
        attempt_count = 0
        headers: Dict[str, str] = {}

        for attempt in range(max_retries + 1):
            attempt_count = attempt + 1
            try:
                from app.llm_orchestration.simulation_context import (
                    simulation_error as simulation_error_ctx,
                )

                sim_err = simulation_error_ctx.get()
                if sim_err:
                    if sim_err == "rate_limit":
                        raise UpstreamRateLimitError(retry_after_ms=60000)
                    if sim_err == "timeout":
                        raise UpstreamTimeoutError(timeout_seconds)
                    if sim_err == "server_error":
                        raise UpstreamServerError("Simulated server error")

                provider_response = await self.client.execute(
                    messages=messages,
                    model=model,
                    timeout_seconds=timeout_seconds,
                    **kwargs,
                )
                if isinstance(provider_response, tuple) and len(provider_response) == 2:
                    result, headers = provider_response
                else:
                    result = provider_response
                    headers = {}

                breaker.record_success()
                result.meta.provider = provider
                result.meta.executed_provider_mode = "nominal"
                result.meta.attempt_count = attempt_count
                result.meta.breaker_state = breaker.state.value
                result.meta.breaker_scope = f"{provider}:{effective_family}"
                return result

            except Exception as err:
                last_error = err
                effective_headers = getattr(err, "_provider_headers", {}) or headers
                is_retryable, mapped_exc = self._classify_error(
                    err, effective_headers, timeout_seconds
                )

                if not is_retryable or attempt >= max_retries:
                    breaker.record_failure()

                if not is_retryable:
                    logger.error(
                        "provider_terminal_error provider=%s family=%s attempt=%d error=%s",
                        provider,
                        effective_family,
                        attempt_count,
                        str(err),
                    )
                    setattr(mapped_exc, "_executed_provider_mode", "nominal")
                    setattr(mapped_exc, "_attempt_count", attempt_count)
                    setattr(mapped_exc, "_breaker_state", breaker.state.value)
                    setattr(mapped_exc, "_breaker_scope", f"{provider}:{effective_family}")

                    error_code = getattr(err, "_provider_error_code", None)
                    if not error_code and hasattr(mapped_exc, "error_type"):
                        error_code = mapped_exc.error_type
                    setattr(mapped_exc, "_provider_error_code", error_code)
                    raise mapped_exc

                logger.warning(
                    "provider_retryable_error provider=%s family=%s attempt=%d error=%s",
                    provider,
                    effective_family,
                    attempt_count,
                    str(err),
                )

                if attempt < max_retries:
                    delay_ms = self._compute_delay(attempt, base_delay_ms, max_delay_ms, mapped_exc)
                    await asyncio.sleep(delay_ms / 1000.0)

        budget_exc = RetryBudgetExhaustedError(attempts=attempt_count, last_error=str(last_error))
        setattr(budget_exc, "_executed_provider_mode", "nominal")
        setattr(budget_exc, "_attempt_count", attempt_count)
        setattr(budget_exc, "_breaker_state", breaker.state.value)
        setattr(budget_exc, "_breaker_scope", f"{provider}:{effective_family}")

        error_code = None
        if last_error and hasattr(last_error, "_provider_error_code"):
            error_code = getattr(last_error, "_provider_error_code")
        if not error_code:
            error_code = budget_exc.error_type
        setattr(budget_exc, "_provider_error_code", error_code)
        raise budget_exc

    def _classify_error(
        self, err: Exception, headers: Dict[str, str], timeout_seconds: int
    ) -> tuple[bool, Exception]:
        provider_request_id = headers.get("x-request-id")

        if isinstance(err, RateLimitError):
            retry_after_ms = 60000
            if "retry-after" in headers:
                try:
                    retry_after_ms = int(headers["retry-after"]) * 1000
                except (ValueError, TypeError):
                    pass

            is_quota = bool(hasattr(err, "code") and err.code == "insufficient_quota")
            return (not is_quota), UpstreamRateLimitError(
                retry_after_ms=retry_after_ms,
                provider_request_id=provider_request_id,
                is_quota_exhausted=is_quota,
            )

        if isinstance(err, APITimeoutError) or isinstance(err, asyncio.TimeoutError):
            return True, UpstreamTimeoutError(timeout_seconds)
        if isinstance(err, APIConnectionError):
            return True, UpstreamConnectionError(str(err), provider_request_id)
        if isinstance(err, InternalServerError):
            return True, UpstreamServerError(str(err), provider_request_id)
        if isinstance(err, ConflictError):
            return True, UpstreamServerError(f"Conflict (409): {str(err)}", provider_request_id)
        if isinstance(err, AuthenticationError):
            return False, UpstreamAuthError(str(err), provider_request_id)
        if isinstance(err, BadRequestError):
            return False, UpstreamBadRequestError(str(err), provider_request_id)
        return False, err

    def _compute_delay(
        self, attempt: int, base_delay_ms: int, max_delay_ms: int, exc: Exception
    ) -> int:
        if isinstance(exc, UpstreamRateLimitError) and exc.retry_after_ms:
            return min(exc.retry_after_ms, max_delay_ms * 2)

        delay_ms = min(base_delay_ms * (2**attempt), max_delay_ms)
        jitter_ms = random.randint(0, delay_ms // 4)
        return delay_ms + jitter_ms
