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
    """Raised when upstream provider returns rate limit error."""

    def __init__(self, retry_after_ms: int = 60000) -> None:
        super().__init__(
            error_type="UPSTREAM_RATE_LIMIT",
            message="upstream provider rate limit exceeded",
            status_code=429,
            retry_after_ms=retry_after_ms,
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
