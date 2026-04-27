"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str
    target_user_email: str


class SeedUserResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    user_id: int
    email: str
    birth_place_resolved_id: int
    birth_timezone: str
    chart_id: str
    chart_reused: bool


class GuidanceQaRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    period: Literal["daily", "weekly"] = "daily"
    target_email: str | None = None
    conversation_id: int | None = None


class ChatQaRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    message: str = Field(min_length=1)
    target_email: str | None = None
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class NatalQaRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    target_email: str | None = None
    use_case_level: Literal["short", "complete"] = "complete"
    locale: str = "fr"
    question: str | None = None
    persona_id: str | None = None
    force_refresh: bool = False
    module: str | None = None


class DailyQaRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    target_email: str | None = None
    date: str | None = None
