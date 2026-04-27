"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.b2b.billing_service import (
    B2BBillingCycleData,
    B2BBillingCycleListData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class B2BBillingCycleApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: B2BBillingCycleData | None
    meta: ResponseMeta


class B2BBillingCycleListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: B2BBillingCycleListData
    meta: ResponseMeta
