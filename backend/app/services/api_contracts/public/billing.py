"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.services.billing.service import (
    BillingPlanData,
    SubscriptionStatusData,
    TokenUsageData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class SubscriptionApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SubscriptionStatusData
    meta: ResponseMeta


class BillingPlansApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[BillingPlanData]
    meta: ResponseMeta


class StripeCheckoutRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    plan: Literal["basic", "premium"]


class StripeSubscriptionUpgradeRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    plan: Literal["basic", "premium"]


class StripeCheckoutResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    checkout_url: str


class StripeCheckoutApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: StripeCheckoutResponse
    meta: ResponseMeta


class StripePortalResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    url: str


class StripePortalApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: StripePortalResponse
    meta: ResponseMeta


class StripeSubscriptionStatusApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: SubscriptionStatusData
    meta: ResponseMeta


class StripeSubscriptionUpgradeResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    checkout_url: str | None
    invoice_status: str | None
    amount_due_cents: int
    currency: str | None


class StripeSubscriptionUpgradeApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: StripeSubscriptionUpgradeResponse
    meta: ResponseMeta


class TokenUsageApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: TokenUsageData
    meta: ResponseMeta
