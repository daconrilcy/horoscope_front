"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigData,
    PersonaProfileListData,
    PersonaRollbackData,
)

router = APIRouter(prefix="/v1/ops/persona", tags=["ops-persona"])


class ResponseMeta(BaseModel):
    request_id: str


class PersonaConfigApiResponse(BaseModel):
    data: PersonaConfigData
    meta: ResponseMeta


class PersonaRollbackApiResponse(BaseModel):
    data: PersonaRollbackData
    meta: ResponseMeta


class PersonaProfileListApiResponse(BaseModel):
    data: PersonaProfileListData
    meta: ResponseMeta
