"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.privacy_service import (
    PrivacyComplianceEvidenceData,
    PrivacyRequestData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class PrivacyApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PrivacyRequestData
    meta: ResponseMeta


class PrivacyEvidenceApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PrivacyComplianceEvidenceData
    meta: ResponseMeta


class DeleteRequestPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    confirmation: str
