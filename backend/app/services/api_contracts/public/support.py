"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.services.billing.service import SubscriptionStatusData
from app.services.ops.incident_service import (
    SupportIncidentData,
    SupportIncidentListData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class PrivacyRequestSummary(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: int
    request_kind: str
    status: str
    requested_at: datetime
    completed_at: datetime | None
    error_reason: str | None


class SupportContextUserData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    user_id: int
    email: str
    role: str
    created_at: datetime


class SupportContextData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    user: SupportContextUserData
    subscription: SubscriptionStatusData
    privacy_requests: list[PrivacyRequestSummary]
    incidents: list[SupportIncidentData]
    audit_events: list["SupportAuditEventSummary"]


class SupportContextApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SupportContextData
    meta: ResponseMeta


class SupportIncidentApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SupportIncidentData
    meta: ResponseMeta


class SupportIncidentListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SupportIncidentListData
    meta: ResponseMeta


class SupportAuditEventSummary(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    event_id: int
    action: str
    status: str
    target_type: str
    target_id: str | None
    created_at: datetime
