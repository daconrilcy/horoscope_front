"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.api_entitlement_gate import B2BApiAccessDeniedError
from app.services.b2b.canonical_usage_service import (
    B2BCanonicalUsageSummary,
    B2BCanonicalUsageSummaryService,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/b2b/usage", tags=["b2b-usage"])


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class B2BUsageSummaryApiResponse(BaseModel):
    data: B2BCanonicalUsageSummary
    meta: ResponseMeta
