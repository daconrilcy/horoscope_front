from __future__ import annotations

from unittest.mock import MagicMock

import stripe
from sqlalchemy.orm import Session

from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.services.stripe_webhook_idempotency_service import StripeWebhookIdempotencyService


def make_mock_event(
    event_id: str,
    event_type: str,
    stripe_object_id: str | None = "obj_123",
) -> stripe.Event:
    event = MagicMock(spec=stripe.Event)
    event.id = event_id
    event.type = event_type
    event.livemode = False

    data_obj = MagicMock()
    data_obj.id = stripe_object_id

    event.data = MagicMock()
    event.data.object = data_obj

    return event


def test_claim_event_new_event_returns_accepted(db_session: Session):
    event = make_mock_event("evt_new_001", "invoice.paid")
    result = StripeWebhookIdempotencyService.claim_event(db_session, event)

    assert result == "accepted"
    record = (
        db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_new_001").first()
    )
    assert record is not None
    assert record.status == "processing"
    assert record.processing_attempts == 1
    assert record.event_type == "invoice.paid"
    assert record.stripe_object_id == "obj_123"


def test_claim_event_already_processed_returns_duplicate(db_session: Session):
    event = make_mock_event("evt_dup_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    StripeWebhookIdempotencyService.mark_processed(db_session, "evt_dup_001")
    db_session.commit()

    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "duplicate_ignored"


def test_claim_event_already_processing_returns_duplicate(db_session: Session):
    event = make_mock_event("evt_proc_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    db_session.commit()  # remains in processing

    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "duplicate_ignored"


def test_claim_event_failed_returns_accepted_and_increments_attempts(db_session: Session):
    event = make_mock_event("evt_fail_001", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)
    StripeWebhookIdempotencyService.mark_failed(db_session, "evt_fail_001", "some error")
    db_session.commit()

    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "accepted"

    record = (
        db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_fail_001").first()
    )
    assert record.processing_attempts == 2
    assert record.status == "processing"
    assert record.last_error is None


def test_mark_processed_updates_status(db_session: Session):
    event = make_mock_event("evt_proc_ok", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)

    StripeWebhookIdempotencyService.mark_processed(db_session, "evt_proc_ok")

    record = (
        db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_proc_ok").first()
    )
    assert record.status == "processed"
    assert record.processed_at is not None


def test_mark_failed_updates_status_and_error(db_session: Session):
    event = make_mock_event("evt_proc_fail", "invoice.paid")
    StripeWebhookIdempotencyService.claim_event(db_session, event)

    StripeWebhookIdempotencyService.mark_failed(db_session, "evt_proc_fail", "Critical Error")

    record = (
        db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="evt_proc_fail").first()
    )
    assert record.status == "failed"
    assert record.last_error == "Critical Error"


def test_claim_event_coerces_ids_to_strings(db_session: Session):
    # Simuler des types non-string (ex: entiers ou objets bizarres)
    event = MagicMock(spec=stripe.Event)
    event.id = 12345  # pas un string
    event.type = "test.event"
    event.livemode = False

    # Correction du mock pour éviter AttributeError
    event.data = MagicMock()
    event.data.object = MagicMock()
    event.data.object.id = 67890

    result = StripeWebhookIdempotencyService.claim_event(db_session, event)
    assert result == "accepted"

    record = db_session.query(StripeWebhookEventModel).filter_by(stripe_event_id="12345").first()
    assert record is not None
    assert record.stripe_object_id == "67890"
