"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
from typing import Any
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.billing.service import BillingService
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.privacy_service import (
    PrivacyComplianceEvidenceData,
    PrivacyRequestData,
    PrivacyService,
    PrivacyServiceError,
)

router = APIRouter(prefix="/v1/privacy", tags=["privacy"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class PrivacyApiResponse(BaseModel):
    data: PrivacyRequestData
    meta: ResponseMeta


class PrivacyEvidenceApiResponse(BaseModel):
    data: PrivacyComplianceEvidenceData
    meta: ResponseMeta


class DeleteRequestPayload(BaseModel):
    confirmation: str
