"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.auth import AuthenticatedUser
from app.core.rate_limit import RateLimitError, check_rate_limit

router = APIRouter(prefix="/v1/ops/b2b/entitlements", tags=["ops-b2b-entitlements"])
VALID_RESOLUTION_SOURCES = {
    "canonical_quota",
    "canonical_unlimited",
    "canonical_disabled",
    "settings_fallback",
}
from app.api.v1.schemas.routers.b2b.entitlements_audit import *


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in ["ops", "admin"]:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_audit:global:{operation}", limit=60, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:role:{user.role}:{operation}", limit=30, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:user:{user.id}:{operation}", limit=15, window_seconds=60)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
