"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.b2b.editorial_service import (
    B2BEditorialConfigData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class B2BEditorialConfigApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: B2BEditorialConfigData
    meta: ResponseMeta
