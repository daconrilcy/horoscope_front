from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AdminSupportTicketItem(BaseModel):
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
    data: list[AdminSupportTicketItem]
    total: int


class AdminSupportTicketDetail(AdminSupportTicketItem):
    description: str
    support_response: str | None
    resolved_at: datetime | None
    updated_at: datetime
    # We could add exchanges here later


class AdminSupportTicketDetailResponse(BaseModel):
    data: AdminSupportTicketDetail


class AdminFlaggedContentItem(BaseModel):
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
    data: list[AdminFlaggedContentItem]
    total: int


class TicketStatusUpdate(BaseModel):
    status: str


class FlaggedContentReviewUpdate(BaseModel):
    status: str # resolved, dismissed
