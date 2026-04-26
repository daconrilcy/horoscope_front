"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_generation.guidance.guidance_service import (
    ContextualGuidanceData,
    GuidanceData,
)

router = APIRouter(prefix="/v1/guidance", tags=["guidance"])


class ResponseMeta(BaseModel):
    request_id: str


class GuidanceRequest(BaseModel):
    period: str
    conversation_id: int | None = None


class GuidanceApiResponse(BaseModel):
    data: GuidanceData
    meta: ResponseMeta


class ContextualGuidanceRequest(BaseModel):
    situation: str
    objective: str
    time_horizon: str | None = None
    conversation_id: int | None = None


class ContextualGuidanceApiResponse(BaseModel):
    data: ContextualGuidanceData
    meta: ResponseMeta
