"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse

from app.api.v1.errors import api_error_response


def _build_user_alias(email: str) -> str:
    local_part = email.split("@", 1)[0].strip()
    cleaned = "".join(
        character for character in local_part if character.isalnum() or character in {"-", "_", "."}
    )
    return cleaned[:120] or "membre"


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
