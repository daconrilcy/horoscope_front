"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.ops.audit_service import (
    AuditEventListData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class AuditEventsApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AuditEventListData
    meta: ResponseMeta
