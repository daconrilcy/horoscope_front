from __future__ import annotations

import logging
from typing import Any

import stripe
from sqlalchemy.orm import Session

from app.services.stripe_billing_profile_service import StripeBillingProfileService
from app.services.stripe_customer_portal_service import StripeCustomerPortalService
from app.services.stripe_webhook_idempotency_service import (
    StripeWebhookIdempotencyService,
)

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
    ) -> stripe.Event:
        """
        Vérifie la signature de l'événement et retourne l'objet stripe.Event.
        """
        try:
            event = stripe.Webhook.construct_event(payload_bytes, sig_header, webhook_secret)
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
        Retourne un statut logique (processed, event_ignored, user_not_resolved, duplicate_ignored).
        """
        event_type = event.type
        event_id = event.id

        # Extraction du customer_id pour les logs structurés
        customer_id = StripeWebhookService._extract_customer_id(event)

        logger.info(
            "stripe_webhook: received event_id=%s type=%s customer_id=%s",
            event_id,
            event_type,
            customer_id,
        )

        # --- GARDE D'IDEMPOTENCE ---
        claim_status = StripeWebhookIdempotencyService.claim_event(db, event)
        if claim_status == "duplicate_ignored":
            return "duplicate_ignored"

        try:
            # On utilise un SAVEPOINT (begin_nested) pour la logique métier
            # afin de pouvoir rollback la logique métier mais committer le statut 'failed'
            # de l'événement idempotency en cas d'erreur.
            with db.begin_nested():
                data_obj = event.data.object
                user_id = StripeWebhookService._resolve_user_id(db, event)

                # Dispatching vers la couche service si l'événement est supporté
                if event_type in (
                    "checkout.session.completed",
                    "checkout.session.async_payment_succeeded",
                    "customer.subscription.created",
                    "customer.subscription.updated",
                    "customer.subscription.deleted",
                    "customer.subscription.paused",
                    "customer.subscription.resumed",
                    "customer.subscription.trial_will_end",
                    "subscription_schedule.created",
                    "subscription_schedule.updated",
                    "subscription_schedule.canceled",
                    "subscription_schedule.completed",
                    "customer.updated",
                    "invoice.paid",
                    "invoice.payment_failed",
                    "invoice.payment_action_required",
                ):
                    if event_type in {
                        "checkout.session.completed",
                        "checkout.session.async_payment_succeeded",
                    } and StripeCustomerPortalService.is_subscription_upgrade_checkout_session(
                        data_obj
                    ):
                        StripeCustomerPortalService.apply_paid_subscription_upgrade_checkout_session(
                            db,
                            session=data_obj,
                        )
                        logger.info(
                            "stripe_webhook: processed upgrade checkout event_id=%s type=%s "
                            "customer_id=%s outcome=processed",
                            event_id,
                            event_type,
                            customer_id,
                        )
                        StripeWebhookIdempotencyService.mark_processed(db, event_id)
                        return "processed"

                    if user_id is None:
                        logger.warning(
                            "stripe_webhook: user not resolved for event_id=%s type=%s "
                            "customer_id=%s outcome=user_not_resolved",
                            event_id,
                            event_type,
                            customer_id,
                        )
                        StripeWebhookIdempotencyService.mark_processed(db, event_id)
                        return "user_not_resolved"

                    StripeBillingProfileService.update_from_event_payload(
                        db,
                        user_id,
                        event.to_dict(),
                    )
                    logger.info(
                        "stripe_webhook: processed event_id=%s type=%s customer_id=%s "
                        "user_id=%s outcome=processed",
                        event_id,
                        event_type,
                        customer_id,
                        user_id,
                    )
                    StripeWebhookIdempotencyService.mark_processed(db, event_id)
                    return "processed"

                logger.info(
                    "stripe_webhook: ignored event_id=%s type=%s "
                    "customer_id=%s outcome=event_ignored",
                    event_id,
                    event_type,
                    customer_id,
                )
                StripeWebhookIdempotencyService.mark_processed(db, event_id)
                return "event_ignored"

        except Exception as exc:
            # Le savepoint a été rollbacké automatiquement par SQLAlchemy.
            # On enregistre l'échec pour le suivi idempotency.
            logger.error(
                "stripe_webhook: error processing event_id=%s type=%s: %s",
                event_id,
                event_type,
                str(exc),
            )
            StripeWebhookIdempotencyService.mark_failed(db, event_id, str(exc))
            # On retourne "failed_internal" pour que le router billing.py
            # puisse committer la marque de failure sans rollback global.
            return "failed_internal"

    @staticmethod
    def _extract_customer_id(event: stripe.Event) -> str | None:
        """
        Extrait l'ID client Stripe de l'événement si présent.
        """
        data_obj = event.data.object
        if isinstance(data_obj, dict):
            if event.type == "customer.updated":
                customer_id = data_obj.get("id")
                return customer_id if isinstance(customer_id, str) else None
            customer_id = data_obj.get("customer")
            return customer_id if isinstance(customer_id, str) else None
        if event.type == "customer.updated":
            return getattr(data_obj, "id", None)
        return getattr(data_obj, "customer", None)

    @staticmethod
    def _resolve_user_id(db: Session, event: stripe.Event) -> int | None:
        """
        Extrait le user_id local à partir de l'événement Stripe.
        """
        event_type = event.type
        data_obj = event.data.object

        if event_type == "checkout.session.completed":
            client_ref = (
                data_obj.get("client_reference_id")
                if isinstance(data_obj, dict)
                else getattr(data_obj, "client_reference_id", None)
            )
            if client_ref:
                try:
                    return int(client_ref)
                except ValueError:
                    logger.error("stripe_webhook: invalid client_reference_id=%s", client_ref)
                    return None
            return None

        if event_type in (
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "customer.subscription.paused",
            "customer.subscription.resumed",
            "customer.subscription.trial_will_end",
            "subscription_schedule.created",
            "subscription_schedule.updated",
            "subscription_schedule.canceled",
            "subscription_schedule.completed",
            "invoice.paid",
            "invoice.payment_failed",
            "invoice.payment_action_required",
            "checkout.session.async_payment_succeeded",
        ):
            customer_id = (
                data_obj.get("customer")
                if isinstance(data_obj, dict)
                else getattr(data_obj, "customer", None)
            )
            if customer_id:
                profile = StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)
                if profile:
                    return profile.user_id
            return None

        if event_type == "customer.updated":
            customer_id = getattr(data_obj, "id", None)
            if customer_id:
                profile = StripeBillingProfileService.get_by_stripe_customer_id(db, customer_id)
                if profile:
                    return profile.user_id
            return None

        return None
