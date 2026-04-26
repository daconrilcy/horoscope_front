"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.billing.service import BillingService, SubscriptionStatusData
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.ops.incident_service import (
    IncidentService,
    IncidentServiceError,
    SupportIncidentCreatePayload,
    SupportIncidentData,
    SupportIncidentListData,
    SupportIncidentListFilters,
    SupportIncidentUpdatePayload,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/support", tags=["support"])


class ResponseMeta(BaseModel):
    request_id: str


class PrivacyRequestSummary(BaseModel):
    request_id: int
    request_kind: str
    status: str
    requested_at: datetime
    completed_at: datetime | None
    error_reason: str | None


class SupportContextUserData(BaseModel):
    user_id: int
    email: str
    role: str
    created_at: datetime


class SupportContextData(BaseModel):
    user: SupportContextUserData
    subscription: SubscriptionStatusData
    privacy_requests: list[PrivacyRequestSummary]
    incidents: list[SupportIncidentData]
    audit_events: list["SupportAuditEventSummary"]


class SupportContextApiResponse(BaseModel):
    data: SupportContextData
    meta: ResponseMeta


class SupportIncidentApiResponse(BaseModel):
    data: SupportIncidentData
    meta: ResponseMeta


class SupportIncidentListApiResponse(BaseModel):
    data: SupportIncidentListData
    meta: ResponseMeta


class SupportAuditEventSummary(BaseModel):
    event_id: int
    action: str
    status: str
    target_type: str
    target_id: str | None
    created_at: datetime
