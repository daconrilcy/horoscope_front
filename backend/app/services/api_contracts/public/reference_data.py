"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class CloneReferenceVersionPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    source_version: str
    new_version: str
