"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.services.b2b.astrology_service import (
    WeeklyBySignData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class QuotaInfoPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    source: str
    limit: int | None = None
    remaining: int | None = None
    window_end: datetime | None = None


class WeeklyBySignApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: WeeklyBySignData
    meta: ResponseMeta
    quota_info: QuotaInfoPayload | None = None
