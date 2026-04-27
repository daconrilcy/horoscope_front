"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from app.core.auth_context import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.core.rate_limit import RateLimitError, check_rate_limit


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> Any | None:
    if user.role not in ["ops", "admin"]:
        return _raise_error(
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(*, user: AuthenticatedUser, request_id: str, operation: str) -> Any | None:
    try:
        check_rate_limit(key=f"b2b_audit:global:{operation}", limit=60, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:role:{user.role}:{operation}", limit=30, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:user:{user.id}:{operation}", limit=15, window_seconds=60)
    except RateLimitError as error:
        return _raise_error(
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
