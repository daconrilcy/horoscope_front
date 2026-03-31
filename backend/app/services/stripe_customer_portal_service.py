from __future__ import annotations

import logging

import stripe
from sqlalchemy.orm import Session

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
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
    def _ensure_subscription_update_is_allowed(
        profile: StripeBillingProfileModel,
    ) -> None:
        if profile.subscription_status == "trialing":
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_subscription_update_not_allowed_for_trial",
                message="Subscription updates are not allowed during the Stripe trial period",
            )

    @staticmethod
    def _map_stripe_portal_error_code(error: stripe.StripeError, *, flow_type: str) -> str:
        if isinstance(error, stripe.InvalidRequestError):
            message = (str(error) or "").lower()
            if (
                flow_type == "subscription_update"
                and "subscription update feature" in message
                and "disabled" in message
            ):
                return "stripe_portal_subscription_update_disabled"
            if (
                flow_type == "subscription_cancel"
                and "subscription cancel feature" in message
                and "disabled" in message
            ):
                return "stripe_portal_subscription_cancel_disabled"
        return "stripe_api_error"

    @staticmethod
    def _get_customer_subscription_profile(
        db: Session,
        *,
        user_id: int,
    ) -> StripeBillingProfileModel:
        profile = StripeBillingProfileService.get_by_user_id(db, user_id)
        if profile is None or not profile.stripe_customer_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_not_found",
                message="No Stripe customer found for this user",
            )
        if not profile.stripe_subscription_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_subscription_not_found",
                message="No active Stripe subscription found for this user",
            )
        return profile

    @staticmethod
    def _create_subscription_flow_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        flow_type: str,
        configuration_id: str | None = None,
    ) -> str:
        if not configuration_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_configuration_missing",
                message="Stripe Customer Portal configuration ID is missing",
            )

        profile = StripeCustomerPortalService._get_customer_subscription_profile(
            db,
            user_id=user_id,
        )
        if flow_type == "subscription_update":
            StripeCustomerPortalService._ensure_subscription_update_is_allowed(profile)

        client = get_stripe_client()
        if client is None:
            raise StripeCustomerPortalServiceError(
                code="stripe_unavailable",
                message="Stripe client is not configured",
            )

        try:
            flow_payload = {
                "subscription": profile.stripe_subscription_id,
            }
            params: dict[str, object] = {
                "customer": profile.stripe_customer_id,
                "return_url": return_url,
                "flow_data": {
                    "type": flow_type,
                    flow_type: flow_payload,
                    "after_completion": {
                        "type": "redirect",
                        "redirect": {"return_url": return_url},
                    },
                },
                "configuration": configuration_id,
            }

            session = client.billing_portal.sessions.create(params=params)
            logger.info(
                "Stripe portal %s session created for user=%s configuration=%s",
                flow_type,
                user_id,
                configuration_id,
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal %s session creation", flow_type)
            raise StripeCustomerPortalServiceError(
                code=StripeCustomerPortalService._map_stripe_portal_error_code(
                    error, flow_type=flow_type
                ),
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error

    @staticmethod
    def create_portal_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """
        Crée une session Stripe Customer Portal pour un utilisateur.
        """
        if not configuration_id:
            raise StripeCustomerPortalServiceError(
                code="stripe_portal_configuration_missing",
                message="Stripe Customer Portal configuration ID is missing",
            )

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
                    "configuration": configuration_id,
                }
            )
            logger.info(
                "Stripe portal session created for user=%s configuration=%s",
                user_id,
                configuration_id,
            )
            return session.url
        except stripe.StripeError as error:
            logger.exception("Stripe API error during portal session creation")
            raise StripeCustomerPortalServiceError(
                code="stripe_api_error",
                message="Stripe API error",
                details={"error_message": str(error)},
            ) from error

    @staticmethod
    def create_subscription_update_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """Crée une session Stripe Customer Portal avec flow subscription_update."""
        return StripeCustomerPortalService._create_subscription_flow_session(
            db,
            user_id=user_id,
            return_url=return_url,
            flow_type="subscription_update",
            configuration_id=configuration_id,
        )

    @staticmethod
    def create_subscription_cancel_session(
        db: Session,
        *,
        user_id: int,
        return_url: str,
        configuration_id: str | None = None,
    ) -> str:
        """Crée une session Stripe Customer Portal avec flow subscription_cancel."""
        return StripeCustomerPortalService._create_subscription_flow_session(
            db,
            user_id=user_id,
            return_url=return_url,
            flow_type="subscription_cancel",
            configuration_id=configuration_id,
        )
