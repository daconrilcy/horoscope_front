"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from typing import Any
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.ops.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagListData,
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/ops/feature-flags", tags=["ops-feature-flags"])


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class FeatureFlagListApiResponse(BaseModel):
    data: FeatureFlagListData
    meta: ResponseMeta


class FeatureFlagApiResponse(BaseModel):
    data: FeatureFlagData
    meta: ResponseMeta
