from __future__ import annotations

import logging

import stripe
from sqlalchemy.orm import Session

from app.integrations.stripe_client import get_stripe_client
from app.services.stripe_billing_profile_service import StripeBillingProfileService

logger = logging.getLogger(__name__)


class StripeCustomerPortalServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class StripeCustomerPortalService:
    @staticmethod
    def create_portal_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
    ) -> str:
        """
        Crée une session Stripe Customer Portal pour un utilisateur.
        """
        # Lecture seule — NE PAS utiliser get_or_create_profile ici
        profile = StripeBillingProfileService.get_by_user_id(db, user_id)
        if profile is None or not profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_billing_profile_not_found",
                message="No Stripe customer ID found for this user",
            )

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            # Création de la session via le SDK Stripe
            session = client.billing_portal.sessions.create(
                params={
                    "customer": profile.stripe_customer_id,
                    "return_url": return_url,
                }
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal session creation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error
