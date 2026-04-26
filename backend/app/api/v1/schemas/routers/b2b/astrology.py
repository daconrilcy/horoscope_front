"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.b2b.astrology_service import (
    WeeklyBySignData,
)

router = APIRouter(prefix="/v1/b2b/astrology", tags=["b2b-astrology"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class QuotaInfoPayload(BaseModel):
    source: str
    limit: int | None = None
    remaining: int | None = None
    window_end: datetime | None = None


class WeeklyBySignApiResponse(BaseModel):
    data: WeeklyBySignData
    meta: ResponseMeta
    quota_info: QuotaInfoPayload | None = None
