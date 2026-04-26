"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
from typing import Any, Literal
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.config import settings
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.session import get_db_session
from app.services.billing.pricing_experiment_service import (
    PricingExperimentService,
    PricingExperimentServiceError,
)
from app.services.billing.service import (
    BillingPlanData,
    BillingService,
    SubscriptionStatusData,
    TokenUsageData,
)
from app.services.billing.stripe_checkout_service import (
    StripeCheckoutService,
    StripeCheckoutServiceError,
)
from app.services.billing.stripe_customer_portal_service import (
    StripeCustomerPortalService,
    StripeCustomerPortalServiceError,
)
from app.services.billing.stripe_webhook_service import (
    StripeWebhookService,
    StripeWebhookServiceError,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/billing", tags=["billing"])
logger = logging.getLogger(__name__)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


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
