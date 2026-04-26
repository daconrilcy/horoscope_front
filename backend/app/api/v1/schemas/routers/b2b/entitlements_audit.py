"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.audit_service import B2BAuditService

router = APIRouter(prefix="/v1/ops/b2b/entitlements", tags=["ops-b2b-entitlements"])
VALID_RESOLUTION_SOURCES = {
    "canonical_quota",
    "canonical_unlimited",
    "canonical_disabled",
    "settings_fallback",
}


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class B2BAuditEntryPayload(BaseModel):
    account_id: int
    company_name: str
    enterprise_plan_id: int | None
    enterprise_plan_code: str | None
    canonical_plan_id: int | None
    canonical_plan_code: str | None
    feature_code: str
    resolution_source: str
    reason: str
    binding_status: str | None
    quota_limit: int | None
    remaining: int | None
    window_end: datetime | None
    admin_user_id_present: bool
    manual_review_required: bool


class B2BAuditListData(BaseModel):
    items: list[B2BAuditEntryPayload]
    total_count: int
    page: int
    page_size: int


class B2BAuditListApiResponse(BaseModel):
    data: B2BAuditListData
    meta: ResponseMeta
