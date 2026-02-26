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
from typing import TYPE_CHECKING, Awaitable, Callable, NoReturn

from app.ai_engine.exceptions import (
    AIEngineError,
    ContextTooLargeError,
    RateLimitExceededError,
    UpstreamError,
    UpstreamTimeoutError,
)
from app.ai_engine.exceptions import (
    ValidationError as AIEngineValidationError,
)
from app.ai_engine.schemas import (
    ChatContext,
    ChatMessage,
    ChatRequest,
    GenerateContext,
    GenerateInput,
    GenerateRequest,
    ProviderConfig,
)
from app.ai_engine.services import chat_service, generate_service

if TYPE_CHECKING:
    from app.ai_engine.schemas import ChatResponse, GenerateResponse

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "AUTO"
DEFAULT_PROVIDER = "openai"


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
            details={"retry_after_ms": str(err.retry_after_ms or 60000)},
        ) from err
    if isinstance(err, ContextTooLargeError):
        raise AIEngineAdapterError(
            code="context_too_large",
            message="context exceeds maximum tokens",
            details=err.details,
        ) from err
    if isinstance(err, AIEngineValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{error_code_prefix}_input",
            message=err.message,
            details=err.details,
        ) from err
    logger.error(
        "ai_engine_adapter_error request_id=%s error=%s",
        request_id,
        str(err),
    )
    raise ConnectionError("llm provider unavailable") from err


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


class AIEngineAdapterError(Exception):
    """Exception raised by the AI Engine adapter."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


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

        chat_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in messages]

        chat_context = ChatContext(
            natal_chart_summary=context.get("natal_chart_summary"),
            memory={"persona_line": context["persona_line"]}
            if context.get("persona_line")
            else None,
        )

        request = ChatRequest(
            locale=locale,
            request_id=request_id,
            trace_id=trace_id,
            messages=chat_messages,
            context=chat_context,
            provider=ProviderConfig(name=DEFAULT_PROVIDER, model=DEFAULT_MODEL),
        )

        try:
            response: ChatResponse = await chat_service.chat(
                request,
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
            )
            return response.text
        except UpstreamTimeoutError as err:
            logger.warning(
                "ai_engine_adapter_timeout request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise TimeoutError("llm provider timeout") from err
        except (UpstreamError, AIEngineError) as err:
            _handle_ai_engine_error(err, request_id, "chat")

    @staticmethod
    async def generate_guidance(
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str = "fr-FR",
    ) -> str:
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

        Returns:
            Generated guidance text.

        Raises:
            AIEngineAdapterError: On generation error.
            TimeoutError: If the provider exceeds the timeout.
            ConnectionError: If the provider is unavailable.
        """
        if _test_guidance_generator is not None:
            return await _test_guidance_generator(
                use_case, context, user_id, request_id, trace_id, locale
            )

        birth_data = None
        if context.get("birth_date"):
            birth_data = {
                "birth_date": context.get("birth_date", ""),
                "birth_time": context.get("birth_time", ""),
                "birth_timezone": context.get("birth_timezone", ""),
            }

        extra_context: dict[str, str] = {}
        if context.get("persona_line"):
            extra_context["persona_line"] = str(context["persona_line"])
        if context.get("context_lines"):
            extra_context["context_lines"] = str(context["context_lines"])
        if context.get("situation"):
            extra_context["situation"] = str(context["situation"])
        if context.get("objective"):
            extra_context["objective"] = str(context["objective"])
        if context.get("time_horizon"):
            extra_context["time_horizon"] = str(context["time_horizon"])

        generate_context = GenerateContext(
            natal_chart_summary=context.get("natal_chart_summary"),
            birth_data=birth_data,
            extra=extra_context if extra_context else None,
        )

        request = GenerateRequest(
            use_case=use_case,
            locale=locale,
            request_id=request_id,
            trace_id=trace_id,
            input=GenerateInput(),
            context=generate_context,
            provider=ProviderConfig(name=DEFAULT_PROVIDER, model=DEFAULT_MODEL),
        )

        try:
            response: GenerateResponse = await generate_service.generate_text(
                request,
                request_id=request_id,
                trace_id=trace_id,
                user_id=user_id,
            )
            return response.text
        except UpstreamTimeoutError as err:
            logger.warning(
                "ai_engine_adapter_timeout request_id=%s error=%s",
                request_id,
                str(err),
            )
            raise TimeoutError("llm provider timeout") from err
        except (UpstreamError, AIEngineError) as err:
            _handle_ai_engine_error(err, request_id, "guidance")
