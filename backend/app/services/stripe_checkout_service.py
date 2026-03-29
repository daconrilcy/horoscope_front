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
        billing_address_collection: str = "auto",
        automatic_tax_enabled: bool = False,
        tax_id_collection_enabled: bool = False,
        trial_enabled: bool = False,
        trial_period_days: int | None = None,
        payment_method_collection: str = "always",
        missing_payment_method_behavior: str | None = None,
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
            "billing_address_collection": billing_address_collection,
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

        if automatic_tax_enabled:
            params["automatic_tax"] = {"enabled": True}

        if tax_id_collection_enabled:
            params["tax_id_collection"] = {"enabled": True}
            if profile.stripe_customer_id:
                params["customer_update"] = {"name": "auto", "address": "auto"}

        # Story 61.55 - Trial Configuration
        if trial_enabled and trial_period_days and trial_period_days > 0:
            params["subscription_data"]["trial_period_days"] = trial_period_days
            # On informe le frontend pour adapter le message de succès
            connector = "&" if "?" in success_url else "?"
            params["success_url"] = f"{success_url}{connector}is_trial=true"

        if payment_method_collection == "if_required":
            params["payment_method_collection"] = "if_required"

        if (
            trial_enabled
            and payment_method_collection == "if_required"
            and missing_payment_method_behavior
        ):
            params["subscription_data"].setdefault("trial_settings", {})
            params["subscription_data"]["trial_settings"]["end_behavior"] = {
                "missing_payment_method": missing_payment_method_behavior
            }

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
