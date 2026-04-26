"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
from datetime import datetime
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
from app.infra.observability.metrics import increment_counter
from app.services.b2b.api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)
from app.services.b2b.astrology_service import (
    B2BAstrologyService,
    B2BAstrologyServiceError,
    WeeklyBySignData,
)
from app.services.b2b.editorial_service import B2BEditorialService, B2BEditorialServiceError

router = APIRouter(prefix="/v1/b2b/astrology", tags=["b2b-astrology"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class QuotaInfoPayload(BaseModel):
    source: str
    limit: int | None = None
    remaining: int | None = None
    window_end: datetime | None = None


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class WeeklyBySignApiResponse(BaseModel):
    data: WeeklyBySignData
    meta: ResponseMeta
    quota_info: QuotaInfoPayload | None = None
