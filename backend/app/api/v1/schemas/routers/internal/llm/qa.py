"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/internal/llm/qa", tags=["internal-llm-qa"])


class ResponseMeta(BaseModel):
    request_id: str
    target_user_email: str


class SeedUserResponse(BaseModel):
    user_id: int
    email: str
    birth_place_resolved_id: int
    birth_timezone: str
    chart_id: str
    chart_reused: bool


class GuidanceQaRequest(BaseModel):
    period: Literal["daily", "weekly"] = "daily"
    target_email: str | None = None
    conversation_id: int | None = None


class ChatQaRequest(BaseModel):
    message: str = Field(min_length=1)
    target_email: str | None = None
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class NatalQaRequest(BaseModel):
    target_email: str | None = None
    use_case_level: Literal["short", "complete"] = "complete"
    locale: str = "fr"
    question: str | None = None
    persona_id: str | None = None
    force_refresh: bool = False
    module: str | None = None


class DailyQaRequest(BaseModel):
    target_email: str | None = None
    date: str | None = None
