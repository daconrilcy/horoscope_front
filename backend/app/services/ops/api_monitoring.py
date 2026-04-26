"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from app.api.dependencies.auth import (
    AuthenticatedUser,
)
from app.api.v1.errors import api_error_response
from app.core.rate_limit import RateLimitError, check_rate_limit


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> Any:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _enforce_limits(*, user: AuthenticatedUser, request_id: str, operation: str) -> Any | None:
    try:
        check_rate_limit(key=f"ops_monitoring:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"ops_monitoring:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(
            key=f"ops_monitoring:user:{user.id}:{operation}", limit=30, window_seconds=60
        )
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
