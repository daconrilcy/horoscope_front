"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

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
from app.services.ops.audit_service import (
    AuditEventListData,
    AuditEventListFilters,
    AuditService,
    AuditServiceError,
)

router = APIRouter(prefix="/v1/audit", tags=["audit"])


class ResponseMeta(BaseModel):
    request_id: str


class AuditEventsApiResponse(BaseModel):
    data: AuditEventListData
    meta: ResponseMeta
