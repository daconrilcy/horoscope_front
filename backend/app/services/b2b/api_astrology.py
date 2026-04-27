"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
)
from app.core.exceptions import ApplicationError
from app.core.rate_limit import RateLimitError, check_rate_limit

logger = logging.getLogger(__name__)


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


def _enforce_limits(
    *,
    client: AuthenticatedEnterpriseClient,
    request_id: str,
    operation: str,
) -> Any | None:
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
        return _raise_error(
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None
