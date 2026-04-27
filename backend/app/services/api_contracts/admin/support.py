"""Schemas Pydantic des endpoints admin support."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AdminSupportTicketItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    user_id: int
    user_email: str
    category: str
    title: str
    status: str
    priority: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminSupportTicketResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminSupportTicketItem]
    total: int


class AdminSupportTicketDetail(AdminSupportTicketItem):
    """Contrat Pydantic exposé par l'API."""

    description: str
    support_response: str | None
    resolved_at: datetime | None
    updated_at: datetime
    audit_trail: list[dict[str, Any]]


class AdminSupportTicketDetailResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminSupportTicketDetail


class AdminFlaggedContentItem(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: int
    user_id: int
    user_email: str
    content_type: str
    content_ref_id: str
    excerpt: str
    reason: str | None
    reported_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class AdminFlaggedContentResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminFlaggedContentItem]
    total: int


class TicketStatusUpdate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    status: str


class FlaggedContentReviewUpdate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    status: str  # resolved, dismissed
