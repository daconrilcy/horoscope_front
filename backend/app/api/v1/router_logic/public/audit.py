"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse

from app.api.dependencies.auth import AuthenticatedUser
from app.api.v1.errors import api_error_response
from app.core.rate_limit import RateLimitError, check_rate_limit


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _ensure_allowed_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in {"support", "ops", "admin"}:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="audit_forbidden",
            message="role is not allowed for audit events",
            details={"required_roles": "support,ops,admin", "actual_role": user.role},
        )
    return None


def _enforce_audit_limits(
    *,
    role: str,
    user_id: int,
    operation: str,
    request_id: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"audit:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(key=f"audit:role:{role}:{operation}", limit=60, window_seconds=60)
        check_rate_limit(key=f"audit:user:{user_id}:{operation}", limit=30, window_seconds=60)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
