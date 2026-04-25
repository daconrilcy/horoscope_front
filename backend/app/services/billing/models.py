"""Porte les DTO et constantes partages du domaine billing."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

FREE_PLAN_CODE = "free"
BASIC_PLAN_CODE = "basic"
PREMIUM_PLAN_CODE = "premium"

PLAN_DEFAULTS: dict[str, dict[str, object]] = {
    FREE_PLAN_CODE: {
        "display_name": "Free",
        "monthly_price_cents": 0,
        "currency": "EUR",
        "daily_message_limit": 1,
    },
    BASIC_PLAN_CODE: {
        "display_name": "Basic",
        "monthly_price_cents": 900,
        "currency": "EUR",
        "daily_message_limit": 50,
    },
    PREMIUM_PLAN_CODE: {
        "display_name": "Premium",
        "monthly_price_cents": 2900,
        "currency": "EUR",
        "daily_message_limit": 1000,
    },
}

STRIPE_ENTITLEMENT_TO_PLAN_CODE: dict[str, str] = {}
PLAN_CODE_TO_STRIPE_ENTITLEMENT: dict[str, str] = {}


class BillingServiceError(Exception):
    """Exception levee lors d erreurs de facturation."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class BillingPlanData(BaseModel):
    """Modele representant un plan tarifaire expose au runtime."""

    code: str
    display_name: str
    monthly_price_cents: int
    currency: str
    daily_message_limit: int
    is_visible_to_users: bool = True
    is_available_to_users: bool = True
    is_active: bool


class CurrentQuotaData(BaseModel):
    """Modele representant l usage courant du quota principal de billing."""

    feature_code: str
    quota_key: str
    quota_limit: int
    consumed: int
    remaining: int
    period_unit: str
    period_value: int
    reset_mode: str
    window_start: datetime
    window_end: datetime | None = None


class SubscriptionStatusData(BaseModel):
    """Modele representant le statut d abonnement runtime."""

    status: str
    subscription_status: str | None = None
    plan: BillingPlanData | None
    scheduled_plan: BillingPlanData | None = None
    change_effective_at: datetime | None = None
    cancel_at_period_end: bool = False
    current_period_end: datetime | None = None
    failure_reason: str | None
    current_quota: CurrentQuotaData | None = None
    updated_at: datetime | None


class TokenUsagePeriod(BaseModel):
    """Fenetre de temps de l usage tokens."""

    unit: str
    window_start: datetime
    window_end: datetime | None = None


class TokenUsageSummary(BaseModel):
    """Resume global de consommation tokens."""

    tokens_total: int
    tokens_in: int
    tokens_out: int


class TokenUsageFeatureSummary(BaseModel):
    """Resume tokens par feature."""

    feature_code: str
    tokens_total: int
    tokens_in: int
    tokens_out: int


class TokenUsageData(BaseModel):
    """Charge utile retournee par la lecture d usage tokens."""

    period: TokenUsagePeriod
    summary: TokenUsageSummary
    by_feature: list[TokenUsageFeatureSummary]
