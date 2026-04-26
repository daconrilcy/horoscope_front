"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

from typing import Any
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.b2b.editorial_service import (
    B2BEditorialConfigData,
    B2BEditorialConfigUpdatePayload,
    B2BEditorialService,
    B2BEditorialServiceError,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/b2b/editorial", tags=["b2b-editorial"])


class ResponseMeta(BaseModel):
    request_id: str


class B2BEditorialConfigApiResponse(BaseModel):
    data: B2BEditorialConfigData
    meta: ResponseMeta
