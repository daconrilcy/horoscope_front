"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/v1/astrologers", tags=["astrologers"])
from app.api.v1.schemas.routers.public.astrologers import *


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
