from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AdminAuditLogItem(BaseModel):
    id: int
    timestamp: datetime
    actor_email_masked: str | None
    actor_role: str
    action: str
    target_type: str | None
    target_id_masked: str | None
    status: str
    details: dict

    model_config = ConfigDict(from_attributes=True)


class AdminAuditLogResponse(BaseModel):
    data: list[AdminAuditLogItem]
    total: int
    page: int
    per_page: int


class AdminAuditExportRequest(BaseModel):
    actor: str | None = None
    action: str | None = None
    target_type: str | None = None
    period: Literal["7d", "30d", "all"] | None = None
