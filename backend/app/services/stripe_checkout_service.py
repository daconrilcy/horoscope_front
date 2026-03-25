from __future__ import annotations

import logging

import stripe
from sqlalchemy.orm import Session

from app.integrations.stripe_client import get_stripe_client
from app.services.stripe_billing_profile_service import (
    STRIPE_PRICE_ENTITLEMENT_MAP,
    StripeBillingProfileService,
)

logger = logging.getLogger(__name__)


class StripeCheckoutServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def _plan_to_price_id(plan: str) -> str | None:
    """Résolution inverse : plan applicatif → Stripe Price ID."""
    for price_id, mapped_plan in STRIPE_PRICE_ENTITLEMENT_MAP.items():
        if mapped_plan == plan:
            return price_id
    return None


class StripeCheckoutService:
    @staticmethod
    def create_checkout_session(
        db: Session,
        *,
        user_id: int,
        user_email: str | None,
        plan: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        client = get_stripe_client()
        if client is None:
            raise StripeCheckoutServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        price_id = _plan_to_price_id(plan)
        if not price_id:
            raise StripeCheckoutServiceError(
                code="plan_price_not_configured",
                message=f"Plan '{plan}' is not configured in Stripe mapping",
            )

        profile = StripeBillingProfileService.get_or_create_profile(db, user_id)

        params: dict = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(user_id),
            "metadata": {"app_user_id": str(user_id)},
            "subscription_data": {"metadata": {"app_user_id": str(user_id), "plan": plan}},
        }

        if profile.stripe_customer_id:
            params["customer"] = profile.stripe_customer_id
        elif user_email:
            params["customer_email"] = user_email
        else:
            raise StripeCheckoutServiceError(
                code="invalid_checkout_request",
                message="Cannot create checkout session without customer ID or email",
            )

        try:
            session = client.checkout.sessions.create(params=params)
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during checkout session creation")
            raise StripeCheckoutServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error
