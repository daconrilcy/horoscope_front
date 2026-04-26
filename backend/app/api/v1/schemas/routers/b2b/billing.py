"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.b2b.billing_service import (
    B2BBillingCycleData,
    B2BBillingCycleListData,
)

router = APIRouter(prefix="/v1/b2b/billing", tags=["b2b-billing"])


class ResponseMeta(BaseModel):
    request_id: str


class B2BBillingCycleApiResponse(BaseModel):
    data: B2BBillingCycleData | None
    meta: ResponseMeta


class B2BBillingCycleListApiResponse(BaseModel):
    data: B2BBillingCycleListData
    meta: ResponseMeta
