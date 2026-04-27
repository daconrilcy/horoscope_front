"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.b2b.enterprise_credentials_service import (
    EnterpriseCredentialListData,
    EnterpriseCredentialSecretData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class EnterpriseCredentialsListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: EnterpriseCredentialListData
    meta: ResponseMeta


class EnterpriseCredentialSecretApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: EnterpriseCredentialSecretData
    meta: ResponseMeta
