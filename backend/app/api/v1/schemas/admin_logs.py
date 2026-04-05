from __future__ import annotations

from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class AdminAppErrorLog(BaseModel):
    id: int
    timestamp: datetime
    request_id: str
    action: str
    status: str
    details: dict


class AdminAppErrorsResponse(BaseModel):
    data: list[AdminAppErrorLog]
    total: int


class AdminStripeEventLog(BaseModel):
    id: int
    stripe_event_id: str
    event_type: str
    status: str
    received_at: datetime
    processed_at: datetime | None
    last_error: str | None


class AdminStripeEventsResponse(BaseModel):
    data: list[AdminStripeEventLog]
    total: int


class AdminQuotaAlert(BaseModel):
    user_id: int
    user_email_masked: str
    plan_code: str
    feature_code: str
    used: int
    limit: int
    consumption_rate: float


class AdminQuotaAlertsResponse(BaseModel):
    data: list[AdminQuotaAlert]
