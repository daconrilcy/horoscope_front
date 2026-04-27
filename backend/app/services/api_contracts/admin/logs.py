"""Schemas Pydantic des endpoints admin de journaux."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AdminAppErrorLog(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    timestamp: datetime
    request_id: str
    action: str
    status: str
    details: dict


class AdminAppErrorsResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminAppErrorLog]
    total: int


class AdminStripeEventLog(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    stripe_event_id: str
    event_type: str
    status: str
    received_at: datetime
    processed_at: datetime | None
    last_error: str | None


class AdminStripeEventsResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminStripeEventLog]
    total: int


class AdminQuotaAlert(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    user_id: int
    user_email_masked: str
    plan_code: str
    feature_code: str
    used: int
    limit: int
    consumption_rate: float


class AdminQuotaAlertsResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminQuotaAlert]
