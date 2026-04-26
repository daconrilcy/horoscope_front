"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.enterprise_credentials_service import (
    EnterpriseCredentialListData,
    EnterpriseCredentialSecretData,
    EnterpriseCredentialsService,
    EnterpriseCredentialsServiceError,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/b2b/credentials", tags=["b2b-credentials"])


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class EnterpriseCredentialsListApiResponse(BaseModel):
    data: EnterpriseCredentialListData
    meta: ResponseMeta


class EnterpriseCredentialSecretApiResponse(BaseModel):
    data: EnterpriseCredentialSecretData
    meta: ResponseMeta
