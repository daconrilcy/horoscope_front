"""AI Engine exceptions."""

from __future__ import annotations


class AIEngineError(Exception):
    """Base exception for AI Engine errors."""

    def __init__(
        self,
        error_type: str,
        message: str,
        *,
        status_code: int = 500,
        retry_after_ms: int | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        self.error_type = error_type
        self.message = message
        self.status_code = status_code
        self.retry_after_ms = retry_after_ms
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, object]:
        """Convert exception to response dict."""
        result: dict[str, object] = {
            "type": self.error_type,
            "message": self.message,
        }
        if self.retry_after_ms is not None:
            result["retry_after_ms"] = self.retry_after_ms
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(AIEngineError):
    """Raised when request validation fails."""

    def __init__(self, message: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(
            error_type="VALIDATION_ERROR",
            message=message,
            status_code=400,
            details=details,
        )


class UnknownUseCaseError(AIEngineError):
    """Raised when an unknown use_case is requested."""

    def __init__(self, use_case: str) -> None:
        super().__init__(
            error_type="VALIDATION_ERROR",
            message=f"unknown use_case: {use_case}",
            status_code=400,
            details={"use_case": use_case},
        )


class ContextTooLargeError(AIEngineError):
    """Raised when context exceeds maximum allowed tokens."""

    def __init__(self, token_count: int, max_tokens: int) -> None:
        super().__init__(
            error_type="VALIDATION_ERROR",
            message=f"context exceeds maximum tokens: {token_count} > {max_tokens}",
            status_code=400,
            details={"token_count": str(token_count), "max_tokens": str(max_tokens)},
        )


class UpstreamRateLimitError(AIEngineError):
    """Raised when upstream provider returns rate limit error (429)."""

    def __init__(
        self,
        retry_after_ms: int = 60000,
        provider_request_id: str | None = None,
        is_quota_exhausted: bool = False,
    ) -> None:
        error_type = "UPSTREAM_QUOTA_EXHAUSTED" if is_quota_exhausted else "UPSTREAM_RATE_LIMIT"
        message = (
            "upstream provider quota exhausted"
            if is_quota_exhausted
            else "upstream provider rate limit exceeded"
        )
        details = {"provider_request_id": provider_request_id} if provider_request_id else None
        super().__init__(
            error_type=error_type,
            message=message,
            status_code=429,
            retry_after_ms=retry_after_ms,
            details=details,
        )


class UpstreamCircuitOpenError(AIEngineError):
    """Raised when the circuit breaker is open for a provider+family."""

    def __init__(self, provider: str, family: str) -> None:
        super().__init__(
            error_type="UPSTREAM_CIRCUIT_OPEN",
            message=(
                f"upstream provider {provider} is unavailable for family {family} (circuit open)"
            ),
            status_code=503,
            details={"provider": provider, "family": family},
        )


class UpstreamError(AIEngineError):
    """Raised when upstream provider returns an error."""

    def __init__(self, message: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(
            error_type="UPSTREAM_ERROR",
            message=message,
            status_code=502,
            details=details,
        )


class UpstreamConnectionError(UpstreamError):
    """Raised when connection to upstream fails."""

    def __init__(self, message: str, provider_request_id: str | None = None) -> None:
        details = {"provider_request_id": provider_request_id} if provider_request_id else {}
        details["kind"] = "connection_error"
        super().__init__(message=message, details=details)


class UpstreamBadRequestError(UpstreamError):
    """Raised when upstream returns 400."""

    def __init__(self, message: str, provider_request_id: str | None = None) -> None:
        details = {"provider_request_id": provider_request_id} if provider_request_id else {}
        details["kind"] = "bad_request"
        super().__init__(message=message, details=details)


class UpstreamAuthError(UpstreamError):
    """Raised when upstream returns 401 or 403."""

    def __init__(self, message: str, provider_request_id: str | None = None) -> None:
        details = {"provider_request_id": provider_request_id} if provider_request_id else {}
        details["kind"] = "auth_error"
        super().__init__(message=message, details=details)


class UpstreamServerError(UpstreamError):
    """Raised when upstream returns 5xx (excluding timeout/connection)."""

    def __init__(self, message: str, provider_request_id: str | None = None) -> None:
        details = {"provider_request_id": provider_request_id} if provider_request_id else {}
        details["kind"] = "server_error"
        super().__init__(message=message, details=details)


class RetryBudgetExhaustedError(UpstreamError):
    """Raised when max retries or time budget is exceeded."""

    def __init__(self, attempts: int, last_error: str) -> None:
        super().__init__(
            message=f"retry budget exhausted after {attempts} attempts",
            details={"attempts": str(attempts), "last_error": last_error},
        )
        self.error_type = "RETRY_BUDGET_EXHAUSTED"


class UpstreamTimeoutError(AIEngineError):
    """Raised when upstream provider times out."""

    def __init__(self, timeout_seconds: int) -> None:
        super().__init__(
            error_type="UPSTREAM_TIMEOUT",
            message=f"upstream provider timeout after {timeout_seconds}s",
            status_code=504,
            details={"timeout_seconds": str(timeout_seconds)},
        )


class ProviderNotConfiguredError(AIEngineError):
    """Raised when the requested provider is not configured."""

    def __init__(self, provider: str) -> None:
        super().__init__(
            error_type="PROVIDER_NOT_CONFIGURED",
            message=f"provider {provider} is not configured",
            status_code=500,
            details={"provider": provider},
        )


class RateLimitExceededError(AIEngineError):
    """Raised when internal rate limit is exceeded."""

    def __init__(self, retry_after_ms: int, *, user_id: str | int) -> None:
        super().__init__(
            error_type="RATE_LIMIT_EXCEEDED",
            message="rate limit exceeded for AI engine requests",
            status_code=429,
            retry_after_ms=retry_after_ms,
            details={"user_id": str(user_id)},
        )
