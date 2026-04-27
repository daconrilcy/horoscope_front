"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.b2b.canonical_usage_service import (
    B2BCanonicalUsageSummary,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class B2BUsageSummaryApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: B2BCanonicalUsageSummary
    meta: ResponseMeta
