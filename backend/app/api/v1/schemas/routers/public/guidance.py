"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

from typing import Any
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_generation.guidance.guidance_service import (
    ContextualGuidanceData,
    GuidanceData,
    GuidanceService,
    GuidanceServiceError,
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
