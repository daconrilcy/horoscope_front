from __future__ import annotations

import logging
from typing import Any

import stripe
from sqlalchemy.orm import Session

from app.services.stripe_billing_profile_service import StripeBillingProfileService

logger = logging.getLogger(__name__)


class StripeWebhookServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class StripeWebhookService:
    """
    Service gérant la réception, la vérification et le dispatching des événements Stripe.
    """

    @staticmethod
    def verify_and_parse(
        payload_bytes: bytes, sig_header: str, webhook_secret: str
    ) -> dict[str, Any]:
        """
        Vérifie la signature de l'événement et retourne le payload sous forme de dictionnaire.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload_bytes, sig_header, webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.warning("stripe_webhook: signature verification failed: %s", str(e))
            raise StripeWebhookServiceError(
                code="invalid_signature",
                message="Stripe webhook signature verification failed",
            ) from e
        except Exception as e:
            logger.exception("stripe_webhook: unexpected error during verification")
            raise StripeWebhookServiceError(
                code="verification_error",
                message="An unexpected error occurred during webhook verification",
            ) from e

    @staticmethod
    def handle_event(db: Session, event: stripe.Event) -> str:
        """
        Traite un événement Stripe validé.
        Retourne un statut logique (processed, ignored, user_not_resolved).
        """
        event_type = event.type
        event_id = event.id

        logger.info(
            "stripe_webhook: received event_id=%s type=%s", event_id, event_type
        )

        user_id = StripeWebhookService._resolve_user_id(db, event)

        if user_id is None:
            if event_type in (
                "checkout.session.completed",
                "customer.subscription.created",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "customer.updated",
            ):
                logger.warning(
                    "stripe_webhook: user not resolved for event_id=%s type=%s",
                    event_id,
                    event_type,
                )
                return "user_not_resolved"
            
            # Pour les autres événements, c'est normal de ne pas résoudre l'utilisateur
            # car nous ne les traitons pas.
            logger.info("stripe_webhook: event_id=%s type=%s ignored", event_id, event_type)
            return "event_ignored"

        # Dispatching vers la couche service
        if event_type in (
            "checkout.session.completed",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "customer.updated",
        ):
            # On repasse le dict à l'ancien service car il attend probablement un dict
            StripeBillingProfileService.update_from_event_payload(db, user_id, event.to_dict())
            logger.info(
                "stripe_webhook: event_id=%s type=%s processed for user_id=%s",
                event_id,
                event_type,
                user_id,
            )
            return "processed"

        logger.info("stripe_webhook: event_id=%s type=%s ignored", event_id, event_type)
        return "event_ignored"

    @staticmethod
    def _resolve_user_id(db: Session, event: stripe.Event) -> int | None:
        """
        Extrait le user_id local à partir de l'événement Stripe.
        """
        event_type = event.type
        data_obj = event.data.object

        if event_type == "checkout.session.completed":
            # Pour checkout.session, l'objet est un stripe.CheckoutSession
            client_ref = getattr(data_obj, "client_reference_id", None)
            if client_ref:
                try:
                    return int(client_ref)
                except ValueError:
                    logger.error(
                        "stripe_webhook: invalid client_reference_id=%s", client_ref
                    )
                    return None
            return None

        if event_type in (
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            customer_id = getattr(data_obj, "customer", None)
            if customer_id:
                profile = StripeBillingProfileService.get_by_stripe_customer_id(
                    db, customer_id
                )
                if profile:
                    return profile.user_id
            return None

        if event_type == "customer.updated":
            customer_id = getattr(data_obj, "id", None)
            if customer_id:
                profile = StripeBillingProfileService.get_by_stripe_customer_id(
                    db, customer_id
                )
                if profile:
                    return profile.user_id
            return None

        return None
