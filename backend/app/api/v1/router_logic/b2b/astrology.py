"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
)
from app.core.rate_limit import RateLimitError, check_rate_limit

router = APIRouter(prefix="/v1/b2b/astrology", tags=["b2b-astrology"])
logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.b2b.astrology import *


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


def _enforce_limits(
    *,
    client: AuthenticatedEnterpriseClient,
    request_id: str,
    operation: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_astrology:global:{operation}", limit=240, window_seconds=60)
        check_rate_limit(
            key=f"b2b_astrology:account:{client.account_id}:{operation}",
            limit=120,
            window_seconds=60,
        )
        check_rate_limit(
            key=f"b2b_astrology:credential:{client.credential_id}:{operation}",
            limit=60,
            window_seconds=60,
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
