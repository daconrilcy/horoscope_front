"""Contrats Pydantic communs aux réponses API v1."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ResponseMeta(BaseModel):
    """Métadonnées communes des réponses API v1."""

    request_id: str


class ErrorPayload(BaseModel):
    """Payload documenté d'une erreur HTTP API v1."""

    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    """Enveloppe d'erreur standard des routeurs API v1."""

    error: ErrorPayload
