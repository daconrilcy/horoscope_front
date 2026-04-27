"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from app.core.exceptions import ApplicationError


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict,
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )
