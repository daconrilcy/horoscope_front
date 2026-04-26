"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.auth import AuthenticatedUser
from app.core.rate_limit import RateLimitError, check_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/ops/b2b/entitlements/repair", tags=["ops-b2b-entitlements"])
from app.api.v1.schemas.routers.b2b.entitlement_repair import *


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
    # AC 17: Limites plus restrictives pour le repair
    try:
        check_rate_limit(key=f"b2b_repair:global:{operation}", limit=10, window_seconds=60)
        check_rate_limit(key=f"b2b_repair:role:{user.role}:{operation}", limit=5, window_seconds=60)
        check_rate_limit(key=f"b2b_repair:user:{user.id}:{operation}", limit=3, window_seconds=60)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
