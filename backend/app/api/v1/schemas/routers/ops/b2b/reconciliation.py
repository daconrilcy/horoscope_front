"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

from datetime import date
from typing import Any
from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.reconciliation_service import (
    B2BReconciliationService,
    B2BReconciliationServiceError,
    ReconciliationActionPayload,
    ReconciliationActionResultData,
    ReconciliationIssueDetailData,
    ReconciliationIssueListData,
    ReconciliationSeverity,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/ops/b2b/reconciliation", tags=["ops-b2b-reconciliation"])


class ResponseMeta(BaseModel):
    request_id: str


class ReconciliationIssueListApiResponse(BaseModel):
    data: ReconciliationIssueListData
    meta: ResponseMeta


class ReconciliationIssueDetailApiResponse(BaseModel):
    data: ReconciliationIssueDetailData
    meta: ResponseMeta


class ReconciliationActionApiResponse(BaseModel):
    data: ReconciliationActionResultData
    meta: ResponseMeta
