"""
Adapter for integrating the AI Engine into existing services.

This module provides a simplified interface for Chat and Guidance services
to interact with the new AI Engine while maintaining compatibility with
existing error handling patterns.
"""

from __future__ import annotations

__all__ = [
    "AIEngineAdapter",
    "AIEngineAdapterError",
    "assess_off_scope",
    "map_adapter_error_to_codes",
    "set_test_chat_generator",
    "set_test_guidance_generator",
    "reset_test_generators",
    "get_test_generators_state",
]

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, NoReturn, Optional

from sqlalchemy.orm import Session

from app.ai_engine.exceptions import (
    AIEngineError,
    ContextTooLargeError,
    ProviderNotConfiguredError,
    RateLimitExceededError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.ai_engine.exceptions import (
    ValidationError as AIEngineValidationError,
)
from app.core.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "AUTO"
DEFAULT_PROVIDER = "openai"


def _build_guidance_gateway_payload(
    use_case: str,
    context: dict[str, str | None],
    locale: str,
) -> tuple[dict[str, str], dict[str, str | None]]:
    """Normalize guidance inputs for Gateway V2 contracts."""
    normalized_context = dict(context)
    user_input: dict[str, str] = {
        "use_case": use_case,
        "locale": locale,
    }

    situation = (normalized_context.get("situation") or "").strip()
    objective = (normalized_context.get("objective") or "").strip()
    time_horizon = (normalized_context.get("time_horizon") or "").strip()

    if use_case == "guidance_daily" and not situation:
        situation = "Lecture astrologique quotidienne basee sur le profil natal du jour."
        normalized_context["situation"] = situation
    elif use_case == "guidance_weekly" and not situation:
        situation = "Lecture astrologique hebdomadaire basee sur le profil natal de la semaine."
        normalized_context["situation"] = situation

    if use_case == "guidance_contextual":
        if objective and time_horizon:
            question = f"{objective} Horizon: {time_horizon}."
        elif objective:
            question = objective
        else:
            question = situation or "Proposer une guidance contextuelle prudente."
    elif use_case == "guidance_weekly":
        question = "Quelle guidance astrologique ressort pour cette semaine ?"
    else:
        question = "Quelle guidance astrologique ressort pour aujourd hui ?"

    user_input["question"] = question
    if situation:
        user_input["situation"] = situation

    return user_input, normalized_context


def _is_non_production_env() -> bool:
    return settings.app_env not in {"production", "prod"}


def _build_test_chat_fallback(messages: list[dict[str, str]]) -> str:
    user_lines = [msg["content"].strip() for msg in messages if msg.get("role") == "user"]
    joined = " | ".join(line for line in user_lines if line)
    if joined:
        return f"Reponse test hors provider: {joined}"
    return "Reponse test hors provider."


def _build_test_guidance_fallback(use_case: str) -> str:
    return f"Guidance test hors provider pour {use_case}."


def _can_use_test_fallback(err: Exception) -> bool:
    if not _is_non_production_env():
        return False
    from app.llm_orchestration.models import GatewayError

    if isinstance(err, ProviderNotConfiguredError):
        return True

    # Search in message, details and causes
    texts = [str(err).lower()]
    if isinstance(err, GatewayError) and err.details:
        texts.append(str(err.details).lower())

    curr = err
    while curr.__cause__ or curr.__context__:
        curr = curr.__cause__ or curr.__context__
        texts.append(str(curr).lower())
        if hasattr(curr, "details") and getattr(curr, "details"):
            texts.append(str(getattr(curr, "details")).lower())

    markers = ["not configured", "api key", "auth", "invalid_api_key", "incorrect api key"]
    for t in texts:
        if any(m in t for m in markers):
            return True
    return False


def _handle_ai_engine_error(
    err: Exception,
    request_id: str,
    error_code_prefix: str,
) -> NoReturn:
    """
    Handle AI Engine errors and convert them to appropriate exceptions.

    Args:
        err: The original exception from AI Engine.
        request_id: Request identifier for logging.
        error_code_prefix: Prefix for error codes (e.g., "chat" or "guidance").

    Raises:
        AIEngineAdapterError: For rate limit, context size, or validation errors.
        ConnectionError: For upstream/generic AI engine errors.
    """
    if isinstance(err, RateLimitExceededError):
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            status_code=429,
            details={"retry_after_ms": str(err.retry_after_ms or 60000)},
        ) from err
    if isinstance(err, ContextTooLargeError):
        raise AIEngineAdapterError(
            code="context_too_large",
            message="context exceeds maximum tokens",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, AIEngineValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{error_code_prefix}_input",
            message=err.message,
            status_code=400,
            details=err.details,
        ) from err
    logger.error(
        "ai_engine_adapter_error request_id=%s error=%s",
        request_id,
        str(err),
    )
    raise ConnectionError("llm provider unavailable") from err


def _handle_gateway_error(
    err: Exception,
    request_id: str,
    use_case: str,
) -> NoReturn:
    """Handle LLM Gateway errors and map them to adapter exceptions."""
    from app.llm_orchestration.models import (
        GatewayConfigError,
        GatewayError,
        InputValidationError,
        OutputValidationError,
        PromptRenderError,
        UnknownUseCaseError,
    )

    if not isinstance(err, GatewayError):
        # Should not happen if used correctly, but safeguard
        raise ConnectionError(
            f"llm provider unavailable (v2: unexpected error type {type(err)})"
        ) from err

    if isinstance(err, PromptRenderError):
        raise AIEngineAdapterError(
            code="prompt_render_error",
            message=f"failed to render prompt for {use_case}",
            status_code=500,
            details=err.details,
        ) from err
    if isinstance(err, UnknownUseCaseError):
        raise AIEngineAdapterError(
            code="unknown_use_case",
            message=f"use case {use_case} is not configured",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, GatewayConfigError):
        raise AIEngineAdapterError(
            code="gateway_config_error",
            message=str(err),
            status_code=500,
            details=err.details,
        ) from err
    if isinstance(err, InputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_input",
            message=str(err),
            status_code=422,
            details=err.details,
        ) from err
    if isinstance(err, OutputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_output",
            message=str(err),
            status_code=502,
            details=err.details,
        ) from err

    # Map provider-originated GatewayError kinds
    kind = err.details.get("kind")
    if kind == "timeout":
        # Raise as standard TimeoutError or map to 504
        raise AIEngineAdapterError(
            code="upstream_timeout",
            message="llm provider timeout",
            status_code=504,
        ) from err
    if kind == "rate_limit":
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            status_code=429,
            details={"retry_after_ms": "60000"},
        ) from err

    logger.error(
        "ai_engine_adapter_gateway_error use_case=%s request_id=%s error=%s",
        use_case,
        request_id,
        str(err),
    )
    raise ConnectionError(f"llm provider unavailable (v2: {use_case})") from err


def assess_off_scope(content: str) -> tuple[bool, float, str | None]:
    """
    Assess if a response is off-scope with a confidence score.

    Args:
        content: The response content to evaluate.

    Returns:
        Tuple of (is_off_scope, confidence_score, reason).
        - is_off_scope: True if the response appears off-scope.
        - confidence_score: 0.0 to 1.0, higher means more confident it's off-scope.
        - reason: Short string explaining why it was flagged, or None if not off-scope.
    """
    normalized = content.strip().lower()
    if not normalized:
        return True, 1.0, "empty_response"
    if "[off_scope]" in normalized:
        return True, 0.95, "explicit_marker"
    if normalized.startswith("hors_scope:"):
        return True, 0.9, "explicit_prefix"
    return False, 0.0, None


def map_adapter_error_to_codes(
    err: AIEngineAdapterError | TimeoutError | ConnectionError,
) -> tuple[str, str]:
    """
    Map AI Engine adapter errors to standardized error codes and messages.

    Args:
        err: The exception to map.

    Returns:
        Tuple of (error_code, error_message) for service-level error handling.
    """
    if isinstance(err, AIEngineAdapterError):
        if err.code == "rate_limit_exceeded":
            return "rate_limit_exceeded", "rate limit exceeded"
        if err.code == "context_too_large":
            return "context_too_large", "context too large"
        return err.code, err.message
    if isinstance(err, TimeoutError):
        return "llm_timeout", "llm provider timeout"
    if isinstance(err, ConnectionError):
        return "llm_unavailable", "llm provider is unavailable"
    return "llm_unavailable", "llm provider is unavailable"


ChatGeneratorFunc = Callable[
    [list[dict[str, str]], dict[str, str | None], int, str, str, str],
    Awaitable[str],
]
GuidanceGeneratorFunc = Callable[
    [str, dict[str, str | None], int, str, str, str],
    Awaitable[str],
]

_test_chat_generator: ChatGeneratorFunc | None = None
_test_guidance_generator: GuidanceGeneratorFunc | None = None


def set_test_chat_generator(generator: ChatGeneratorFunc | None) -> None:
    """Set a test generator for chat (for unit testing)."""
    global _test_chat_generator
    _test_chat_generator = generator


def set_test_guidance_generator(generator: GuidanceGeneratorFunc | None) -> None:
    """Set a test generator for guidance (for unit testing)."""
    global _test_guidance_generator
    _test_guidance_generator = generator


def reset_test_generators() -> None:
    """Reset all test generators (for cleanup after tests)."""
    global _test_chat_generator, _test_guidance_generator
    _test_chat_generator = None
    _test_guidance_generator = None


def get_test_generators_state() -> tuple[bool, bool]:
    """Return state of test generators (for testing reset behavior)."""
    return (_test_chat_generator is not None, _test_guidance_generator is not None)


class AIEngineAdapterError(AIEngineError):
    """Exception raised by the AI Engine adapter."""

    def __init__(
        self, code: str, message: str, status_code: int = 400, details: dict[str, str] | None = None
    ) -> None:
        self.code = code
        self.message = message  # Compatibility with map_adapter_error_to_codes
        super().__init__(
            error_type=f"ADAPTER_{code.upper()}",
            message=message,
            status_code=status_code,
            details=details,
        )


class AIEngineAdapter:
    """
    Adapter for integrating the AI Engine into existing services.

    Provides a simplified interface for chat and guidance with
    error mapping to service exceptions.
    """

    @staticmethod
    async def generate_chat_reply(
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Optional[Session] = None,
    ) -> str:
        """
        Generate a chat reply via the AI Engine.

        Args:
            messages: List of messages in {"role": "...", "content": "..."} format.
            context: Additional context (natal_chart_summary, memory, etc.).
            user_id: User identifier.
            request_id: Request identifier for logging.
            trace_id: Trace identifier for distributed tracing.
            locale: Locale for the response (default: "fr-FR").
            db: Database session for orchestration v2.

        Returns:
            Generated response text.

        Raises:
            AIEngineAdapterError: On generation error.
            TimeoutError: If the provider exceeds the timeout.
            ConnectionError: If the provider is unavailable.
        """
        if _test_chat_generator is not None:
            return await _test_chat_generator(
                messages, context, user_id, request_id, trace_id, locale
            )

        logger.info(
            "chat_reply_path request_id=%s history_count=%d has_natal=%s conversation_id=%s",
            request_id,
            len(messages),
            bool(context.get("natal_chart_summary")),
            context.get("conversation_id", "none"),
        )

        try:
            from app.llm_orchestration.gateway import LLMGateway

            gateway = LLMGateway()
            # For chat, we use the 'chat_astrologer' use case from DB
            # user_input: includes 'message' (for schema) and 'last_user_msg' (for prompt)
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break

            gateway_user_input = {
                "message": last_user_msg,
                "last_user_msg": last_user_msg,
                "use_case": "chat_astrologer",
                "locale": locale,
            }
            conversation_id = context.get("conversation_id")
            if conversation_id is not None:
                gateway_user_input["conversation_id"] = str(conversation_id)

            result = await gateway.execute(
                use_case="chat_astrologer",
                user_input=gateway_user_input,
                context={
                    **context,
                    "history": messages[
                        :-1
                    ],  # Exclude the last message which is sent as user_input
                },
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
                db=db,
            )

            # If structured output is available (canonical ChatResponse_v1), return the message
            if result.structured_output and "message" in result.structured_output:
                validation_status = getattr(
                    getattr(result, "meta", None), "validation_status", "unknown"
                )
                logger.info(
                    "chat_reply_v2_output request_id=%s output=structured validation=%s",
                    request_id,
                    validation_status,
                )
                return result.structured_output["message"]

            meta = getattr(result, "meta", None)
            validation_status = getattr(meta, "validation_status", "unknown")
            validation_errors = getattr(meta, "validation_errors", None) or []
            raw_snippet = (result.raw_output or "")[:120].replace("\n", " ")
            logger.warning(
                "chat_reply_v2_output request_id=%s output=raw_fallback "
                "validation=%s errors=%s raw_snippet=%r",
                request_id,
                validation_status,
                validation_errors,
                raw_snippet,
            )
            return result.raw_output
        except Exception as err:
            if _can_use_test_fallback(err):
                return _build_test_chat_fallback(messages)
            # Preserve typed upstream errors so callers get correct HTTP codes (429/504/502).
            if isinstance(err, UpstreamRateLimitError):
                raise AIEngineAdapterError(
                    code="rate_limit_exceeded",
                    message="rate limit exceeded",
                    status_code=429,
                    details={"retry_after_ms": str(err.retry_after_ms or 60000)},
                ) from err
            if isinstance(err, UpstreamTimeoutError):
                raise AIEngineAdapterError(
                    code="upstream_timeout",
                    message="llm provider timeout",
                    status_code=504,
                ) from err
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, GatewayError):
                _handle_gateway_error(err, request_id, "chat")
            logger.error(
                "ai_engine_adapter_v2_unexpected_error request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err

    @staticmethod
    async def generate_guidance(
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
        db: Optional[Session] = None,
    ) -> Any:
        """
        Generate guidance via the AI Engine.

        Args:
            use_case: Use case identifier (guidance_daily, guidance_weekly,
                guidance_contextual).
            context: Context including birth_data, situation, objective,
                time_horizon, context_lines.
            user_id: User identifier.
            request_id: Request identifier for logging.
            trace_id: Trace identifier for distributed tracing.
            locale: Locale for the response (default: "fr-FR").
            db: Database session for orchestration v2.

        Returns:
            GatewayResult from the LLMGateway.

        Raises:
            AIEngineAdapterError: On generation error.
            ConnectionError: If the provider is unavailable.
        """
        if _test_guidance_generator is not None:
            # For testing, we mock a result object
            text = await _test_guidance_generator(
                use_case, context, user_id, request_id, trace_id, locale
            )
            from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
            return GatewayResult(
                use_case=use_case,
                request_id=request_id,
                trace_id=trace_id,
                raw_output=text,
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test-model"),
            )

        try:
            from app.llm_orchestration.gateway import LLMGateway

            gateway = LLMGateway()
            gateway_user_input, gateway_context = _build_guidance_gateway_payload(
                use_case,
                context,
                locale,
            )
            result = await gateway.execute(
                use_case=use_case,
                user_input=gateway_user_input,
                context=gateway_context,
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
                db=db,
            )
            return result
        except Exception as err:
            if _can_use_test_fallback(err):
                from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
                return GatewayResult(
                    use_case=use_case,
                    request_id=request_id,
                    trace_id=trace_id,
                    raw_output=_build_test_guidance_fallback(use_case),
                    usage=UsageInfo(),
                    meta=GatewayMeta(latency_ms=0, model="test-model"),
                )
            # Preserve typed upstream errors so callers get correct HTTP codes (429/504/502).
            if isinstance(err, UpstreamRateLimitError):
                raise AIEngineAdapterError(
                    code="rate_limit_exceeded",
                    message="rate limit exceeded",
                    status_code=429,
                    details={"retry_after_ms": str(err.retry_after_ms or 60000)},
                ) from err
            if isinstance(err, UpstreamTimeoutError):
                raise AIEngineAdapterError(
                    code="upstream_timeout",
                    message="llm provider timeout",
                    status_code=504,
                ) from err
            from app.llm_orchestration.models import GatewayError

            if isinstance(err, GatewayError):
                _handle_gateway_error(err, request_id, use_case)
            logger.error(
                "ai_engine_adapter_v2_unexpected_error use_case=%s request_id=%s error=%s",
                use_case,
                request_id,
                str(err),
            )
            raise ConnectionError("llm provider unavailable (v2)") from err
