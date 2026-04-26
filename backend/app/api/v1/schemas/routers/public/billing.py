"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.billing.service import (
    BillingPlanData,
    SubscriptionStatusData,
    TokenUsageData,
)

router = APIRouter(prefix="/v1/billing", tags=["billing"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class SubscriptionApiResponse(BaseModel):
    data: SubscriptionStatusData
    meta: ResponseMeta


class BillingPlansApiResponse(BaseModel):
    data: list[BillingPlanData]
    meta: ResponseMeta


class StripeCheckoutRequest(BaseModel):
    plan: Literal["basic", "premium"]


class StripeSubscriptionUpgradeRequest(BaseModel):
    plan: Literal["basic", "premium"]


class StripeCheckoutResponse(BaseModel):
    checkout_url: str


class StripeCheckoutApiResponse(BaseModel):
    data: StripeCheckoutResponse
    meta: ResponseMeta


class StripePortalResponse(BaseModel):
    url: str


class StripePortalApiResponse(BaseModel):
    data: StripePortalResponse
    meta: ResponseMeta


class StripeSubscriptionStatusApiResponse(BaseModel):
    data: SubscriptionStatusData
    meta: ResponseMeta


class StripeSubscriptionUpgradeResponse(BaseModel):
    checkout_url: str | None
    invoice_status: str | None
    amount_due_cents: int
    currency: str | None


class StripeSubscriptionUpgradeApiResponse(BaseModel):
    data: StripeSubscriptionUpgradeResponse
    meta: ResponseMeta


class TokenUsageApiResponse(BaseModel):
    data: TokenUsageData
    meta: ResponseMeta
