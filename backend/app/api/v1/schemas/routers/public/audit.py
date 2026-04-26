"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ops.audit_service import (
    AuditEventListData,
)

router = APIRouter(prefix="/v1/audit", tags=["audit"])


class ResponseMeta(BaseModel):
    request_id: str


class AuditEventsApiResponse(BaseModel):
    data: AuditEventListData
    meta: ResponseMeta
