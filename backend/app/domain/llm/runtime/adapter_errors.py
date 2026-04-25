"""Centralise les erreurs stables exposees par la facade publique du runtime LLM."""

from __future__ import annotations

import logging
from typing import NoReturn

from app.domain.llm.runtime.errors import (
    AIEngineError,
    ContextTooLargeError,
    RateLimitExceededError,
    RetryBudgetExhaustedError,
    UpstreamAuthError,
    UpstreamBadRequestError,
    UpstreamCircuitOpenError,
    UpstreamConnectionError,
    UpstreamRateLimitError,
    UpstreamServerError,
    UpstreamTimeoutError,
)
from app.domain.llm.runtime.errors import ValidationError as AIEngineValidationError

logger = logging.getLogger(__name__)


class AIEngineAdapterError(AIEngineError):
    """Exception stable renvoyee aux couches consommatrices de la facade LLM."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        super().__init__(
            error_type=f"ADAPTER_{code.upper()}",
            message=message,
            status_code=status_code,
            details=details,
        )


def map_adapter_error_to_codes(
    err: AIEngineAdapterError | TimeoutError | ConnectionError,
) -> tuple[str, str]:
    """Mappe une erreur de facade vers un code stable pour les services metier."""
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


def handle_gateway_error(
    err: Exception,
    request_id: str,
    use_case: str,
) -> NoReturn:
    """Convertit les erreurs runtime LLM en erreurs stables pour les consommateurs."""
    from app.domain.llm.runtime.contracts import (
        GatewayConfigError,
        GatewayError,
        InputValidationError,
        OutputValidationError,
        PromptRenderError,
        UnknownUseCaseError,
    )

    if isinstance(err, UpstreamRateLimitError):
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message=err.message,
            status_code=429,
            details={"retry_after_ms": str(err.retry_after_ms or 60000), **err.details},
        ) from err
    if isinstance(err, UpstreamTimeoutError):
        raise AIEngineAdapterError(
            code="upstream_timeout",
            message="llm provider timeout",
            status_code=504,
            details=err.details,
        ) from err
    if isinstance(err, UpstreamConnectionError):
        raise AIEngineAdapterError(
            code="upstream_connection_error",
            message="llm provider connection failed",
            status_code=502,
            details=err.details,
        ) from err
    if isinstance(err, UpstreamCircuitOpenError):
        raise AIEngineAdapterError(
            code="upstream_circuit_open",
            message=err.message,
            status_code=503,
            details=err.details,
        ) from err
    if isinstance(err, RetryBudgetExhaustedError):
        raise AIEngineAdapterError(
            code="retry_budget_exhausted",
            message=err.message,
            status_code=502,
            details=err.details,
        ) from err
    if isinstance(err, (UpstreamAuthError, UpstreamBadRequestError, UpstreamServerError)):
        status = 400 if isinstance(err, UpstreamBadRequestError) else 502
        raise AIEngineAdapterError(
            code="upstream_error",
            message=f"llm provider error: {err.error_type}",
            status_code=status,
            details=err.details,
        ) from err
    if isinstance(err, PromptRenderError):
        raise AIEngineAdapterError(
            code="prompt_render_error",
            message=f"failed to render prompt for {use_case}",
            status_code=400,
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
            code=err.error_code or "gateway_config_error",
            message=str(err),
            status_code=500,
            details=err.details,
        ) from err
    if isinstance(err, InputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_input",
            message="Input validation failed",
            status_code=400,
            details=err.details,
        ) from err
    if isinstance(err, OutputValidationError):
        raise AIEngineAdapterError(
            code=f"invalid_{use_case}_output",
            message="Output validation failed",
            status_code=422,
            details=err.details,
        ) from err
    if isinstance(err, GatewayError):
        kind = err.details.get("kind")
        if kind == "timeout":
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


def handle_ai_engine_error(
    err: Exception,
    request_id: str,
    error_code_prefix: str,
) -> NoReturn:
    """Conserve le mapping historique encore attendu par certains consommateurs."""
    del request_id
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
    logger.error("ai_engine_adapter_error error=%s", str(err))
    raise ConnectionError("llm provider unavailable") from err
