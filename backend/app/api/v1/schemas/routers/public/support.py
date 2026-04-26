"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.billing.service import SubscriptionStatusData
from app.services.ops.incident_service import (
    SupportIncidentData,
    SupportIncidentListData,
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
