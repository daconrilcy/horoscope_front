from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminUserSearchItem(BaseModel):
    id: int
    email: str
    role: str
    plan_code: str | None
    subscription_status: str | None
    is_suspended: bool
    is_locked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserSearchResponse(BaseModel):
    data: list[AdminUserSearchItem]
    total: int


class AdminUserQuota(BaseModel):
    feature_code: str
    used: int
    limit: int | None  # None if unlimited
    period: str


class AdminUserLlmLog(BaseModel):
    id: str
    use_case: str
    timestamp: datetime
    status: str
    tokens_total: int


class AdminUserSupportTicket(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime


class AdminUserAuditEvent(BaseModel):
    id: int
    action: str
    actor_role: str
    created_at: datetime


class AdminUserActivitySummary(BaseModel):
    total_tokens: int
    tokens_in: int
    tokens_out: int
    messages_count: int
    natal_charts_total: int
    natal_charts_short: int
    natal_charts_complete: int


class AdminUserDetail(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime
    is_active: bool
    is_suspended: bool = False  # Story 65.9
    is_locked: bool = False  # Story 65.9

    # Subscription & Billing
    plan_code: str | None
    subscription_status: str | None
    stripe_customer_id_masked: str | None
    payment_method_summary: str | None
    last_invoice_amount_cents: int | None
    last_invoice_date: datetime | None

    # Related data summaries
    activity_summary: AdminUserActivitySummary
    quotas: list[AdminUserQuota]
    recent_llm_logs: list[AdminUserLlmLog]
    recent_tickets: list[AdminUserSupportTicket]
    recent_audit_events: list[AdminUserAuditEvent]

    model_config = ConfigDict(from_attributes=True)


class AdminUserDetailResponse(BaseModel):
    data: AdminUserDetail


class RevealStripeIdResponse(BaseModel):
    stripe_customer_id: str
