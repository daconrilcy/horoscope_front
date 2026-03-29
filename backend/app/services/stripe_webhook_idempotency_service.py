from __future__ import annotations

import logging
from datetime import datetime, timezone

import stripe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel

logger = logging.getLogger(__name__)


class StripeWebhookIdempotencyService:

    @staticmethod
    def claim_event(db: Session, event: stripe.Event) -> str:
        """
        Tente de claimer l'événement pour traitement.
        Retourne :
          "accepted"          → nouvel événement ou re-claim d'un failed
          "duplicate_ignored" → déjà processed ou déjà processing
        """
        stripe_event_id = str(event.id)
        event_type = str(event.type)
        stripe_object_id = getattr(event.data.object, "id", None)
        if stripe_object_id is not None:
            stripe_object_id = str(stripe_object_id)

        try:
            # Utilisation de begin_nested() (savepoint) pour gérer l'IntegrityError
            # sans impacter la transaction globale du router.
            with db.begin_nested():
                record = StripeWebhookEventModel(
                    stripe_event_id=stripe_event_id,
                    event_type=event_type,
                    stripe_object_id=stripe_object_id,
                    livemode=bool(getattr(event, "livemode", False)),
                    status="processing",
                    processing_attempts=1,
                )
                db.add(record)
                db.flush()
            return "accepted"
        except IntegrityError:
            # Le savepoint est déjà rollbacké par SQLAlchemy.
            pass

        # L'événement existe déjà — lire son statut avec verrou row-level pour éviter race conditions
        record = (
            db.query(StripeWebhookEventModel)
            .filter_by(stripe_event_id=stripe_event_id)
            .with_for_update()
            .first()
        )
        if record is None:
            # Cas rare (suppression entre temps ?) -> on accepte pour recréation
            return "accepted"

        if record.status in ("processed", "processing"):
            logger.info(
                "stripe_webhook_idempotency: duplicate event_id=%s event_type=%s "
                "existing_status=%s outcome=duplicate_ignored",
                stripe_event_id,
                event_type,
                record.status,
            )
            return "duplicate_ignored"

        if record.status == "failed":
            # Re-claim : l'événement a échoué lors d'un traitement précédent, on réessaie
            record.status = "processing"
            record.last_error = None
            record.processed_at = None
            record.processing_attempts += 1
            db.flush()
            logger.info(
                "stripe_webhook_idempotency: retry_from_failed event_id=%s event_type=%s "
                "attempt=%s",
                stripe_event_id,
                event_type,
                record.processing_attempts,
            )
            return "accepted"

        return "duplicate_ignored"

    @staticmethod
    def mark_processed(db: Session, event_id: str) -> None:
        """Met à jour la ligne vers 'processed'."""
        record = db.query(StripeWebhookEventModel).filter_by(stripe_event_id=str(event_id)).first()
        if record:
            record.status = "processed"
            record.processed_at = datetime.now(timezone.utc)

    @staticmethod
    def mark_failed(db: Session, event_id: str, error_message: str) -> None:
        """Met à jour la ligne vers 'failed'. Appelé dans le bloc except de handle_event()."""
        record = db.query(StripeWebhookEventModel).filter_by(stripe_event_id=str(event_id)).first()
        if record:
            record.status = "failed"
            record.last_error = str(error_message)[:2000]
            db.flush()
