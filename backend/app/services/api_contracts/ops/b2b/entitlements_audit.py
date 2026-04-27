"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class B2BAuditEntryPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    account_id: int
    company_name: str
    enterprise_plan_id: int | None
    enterprise_plan_code: str | None
    canonical_plan_id: int | None
    canonical_plan_code: str | None
    feature_code: str
    resolution_source: str
    reason: str
    binding_status: str | None
    quota_limit: int | None
    remaining: int | None
    window_end: datetime | None
    admin_user_id_present: bool
    manual_review_required: bool


class B2BAuditListData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    items: list[B2BAuditEntryPayload]
    total_count: int
    page: int
    page_size: int


class B2BAuditListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: B2BAuditListData
    meta: ResponseMeta
