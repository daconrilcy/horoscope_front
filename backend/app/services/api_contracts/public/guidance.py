"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.llm_generation.guidance.guidance_service import (
    ContextualGuidanceData,
    GuidanceData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class GuidanceRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    period: str
    conversation_id: int | None = None


class GuidanceApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: GuidanceData
    meta: ResponseMeta


class ContextualGuidanceRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    situation: str
    objective: str
    time_horizon: str | None = None
    conversation_id: int | None = None


class ContextualGuidanceApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ContextualGuidanceData
    meta: ResponseMeta
