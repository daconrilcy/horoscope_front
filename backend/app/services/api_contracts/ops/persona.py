"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigData,
    PersonaProfileListData,
    PersonaRollbackData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class PersonaConfigApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PersonaConfigData
    meta: ResponseMeta


class PersonaRollbackApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PersonaRollbackData
    meta: ResponseMeta


class PersonaProfileListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PersonaProfileListData
    meta: ResponseMeta
