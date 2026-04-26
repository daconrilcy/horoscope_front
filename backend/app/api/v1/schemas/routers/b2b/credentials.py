"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.b2b.enterprise_credentials_service import (
    EnterpriseCredentialListData,
    EnterpriseCredentialSecretData,
)

router = APIRouter(prefix="/v1/b2b/credentials", tags=["b2b-credentials"])


class ResponseMeta(BaseModel):
    request_id: str


class EnterpriseCredentialsListApiResponse(BaseModel):
    data: EnterpriseCredentialListData
    meta: ResponseMeta


class EnterpriseCredentialSecretApiResponse(BaseModel):
    data: EnterpriseCredentialSecretData
    meta: ResponseMeta
