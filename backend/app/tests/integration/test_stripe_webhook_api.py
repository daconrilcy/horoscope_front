"""Tests d'integration du contrat HTTP public du webhook Stripe."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing.service import BillingService
from app.tests.helpers.db_session import open_app_test_db_session

client = TestClient(app)


def _sign_payload(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.".encode() + payload
    signature = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def _unique_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    payload = b'{"id": "evt_invalid", "type": "checkout.session.completed"}'
    headers = {"stripe-signature": "invalid"}

    with patch("app.core.config.settings.stripe_webhook_secret", "whsec_test"):
        response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_signature"


@pytest.mark.asyncio
async def test_webhook_no_secret_configured():
    payload = b'{"id": "evt_nosecret"}'
    headers = {"stripe-signature": "any"}

    with patch("app.core.config.settings.stripe_webhook_secret", None):
        response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "webhook_secret_not_configured"


@pytest.mark.asyncio
async def test_webhook_success_flow():
    event_id = _unique_id("evt_success")
    payload = (
        f'{{"id": "{event_id}", "type": "checkout.session.completed", '
        f'"data": {{"object": {{"client_reference_id": "42", "id": "cs_123"}}}}}}'
    ).encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        # On mock l'événement retourné par verify_and_parse
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "checkout.session.completed"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "cs_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_webhook_service.StripeWebhookService.handle_event"
            ) as mock_handle:
                mock_handle.return_value = "processed"

                response = client.post(
                    "/v1/billing/stripe-webhook", content=payload, headers=headers
                )

                assert response.status_code == 200
                assert response.json() == {"status": "processed"}
                mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_app_error_returns_retryable_error():
    """Une erreur signee inattendue doit rester retryable pour Stripe."""
    event_id = _unique_id("evt_error")
    payload = f'{{"id": "{event_id}", "type": "checkout.session.completed"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "checkout.session.completed"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "cs_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_webhook_service.StripeWebhookService.handle_event"
            ) as mock_handle:
                mock_handle.side_effect = Exception("Internal error")

                response = client.post(
                    "/v1/billing/stripe-webhook", content=payload, headers=headers
                )

                assert response.status_code == 500
                assert response.json()["error"]["code"] == "stripe_webhook_processing_failed"


@pytest.mark.asyncio
async def test_webhook_subscription_trial_will_end():
    event_id = _unique_id("evt_trial")
    payload = f'{{"id": "{event_id}", "type": "customer.subscription.trial_will_end"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "customer.subscription.trial_will_end"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "sub_123"
        mock_event.data.object.customer = "cus_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id"
            ) as mock_get_profile:
                mock_profile = MagicMock()
                mock_profile.user_id = 42
                mock_get_profile.return_value = mock_profile

                with patch(
                    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload"
                ) as mock_update:
                    response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )

                    assert response.status_code == 200
                    assert response.json() == {"status": "processed"}
                    mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_duplicate_ignored():
    """Vérifie que le second envoi du même event_id retourne duplicate_ignored"""
    event_id = _unique_id("evt_dup")
    payload = f'{{"id": "{event_id}", "type": "invoice.paid"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "invoice.paid"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "in_123"
        mock_event.data.object.customer = "cus_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id"
            ) as mock_get_profile:
                mock_profile = MagicMock()
                mock_profile.user_id = 42
                mock_get_profile.return_value = mock_profile

                with patch(
                    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload"
                ) as mock_update:
                    # Premier passage -> processed
                    response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )
                    assert response.status_code == 200
                    assert response.json() == {"status": "processed"}
                    assert mock_update.call_count == 1

                    # Second passage -> duplicate_ignored
                    response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )
                    assert response.status_code == 200
                    assert response.json() == {"status": "duplicate_ignored"}
                    assert mock_update.call_count == 1  # Pas d'appel supplémentaire


@pytest.mark.asyncio
async def test_webhook_invoice_payment_succeeded_remains_ignored():
    """L'ancien événement invoice success ne redevient pas supporté."""
    event_id = _unique_id("evt_ignored")
    payload = f'{{"id": "{event_id}", "type": "invoice.payment_succeeded"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "invoice.payment_succeeded"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "in_ignored_123"
        mock_event.data.object.customer = "cus_ignored_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "event_ignored"}


@pytest.mark.asyncio
async def test_webhook_business_failure_persists_failed_and_retry_is_accepted():
    event_id = _unique_id("evt_retry")
    payload = f'{{"id": "{event_id}", "type": "invoice.paid"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "invoice.paid"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "in_retry_123"
        mock_event.data.object.customer = "cus_retry_123"
        mock_event.to_dict.return_value = {"id": event_id, "type": "invoice.paid"}

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id"
            ) as mock_get_profile:
                mock_profile = MagicMock()
                mock_profile.user_id = 42
                mock_get_profile.return_value = mock_profile

                with patch(
                    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload",
                    side_effect=[RuntimeError("boom"), None],
                ) as mock_update:
                    first_response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )
                    assert first_response.status_code == 500
                    assert (
                        first_response.json()["error"]["code"] == "stripe_webhook_processing_failed"
                    )

                    with open_app_test_db_session() as db:
                        failed_record = (
                            db.query(StripeWebhookEventModel)
                            .filter_by(stripe_event_id=event_id)
                            .first()
                        )
                        assert failed_record is not None
                        assert failed_record.status == "failed"
                        assert failed_record.processing_attempts == 1
                        assert failed_record.last_error == "boom"

                    second_response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )
                    assert second_response.status_code == 200
                    assert second_response.json() == {"status": "processed"}
                    assert mock_update.call_count == 2

                    with open_app_test_db_session() as db:
                        processed_record = (
                            db.query(StripeWebhookEventModel)
                            .filter_by(stripe_event_id=event_id)
                            .first()
                        )
                        assert processed_record is not None
                        assert processed_record.status == "processed"
                        assert processed_record.processing_attempts == 2
                        assert processed_record.last_error is None


@pytest.mark.asyncio
async def test_webhook_subscription_paused():
    event_id = _unique_id("evt_paused")
    payload = f'{{"id": "{event_id}", "type": "customer.subscription.paused"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "customer.subscription.paused"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "sub_123"
        mock_event.data.object.customer = "cus_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id"
            ) as mock_get_profile:
                mock_profile = MagicMock()
                mock_profile.user_id = 42
                mock_get_profile.return_value = mock_profile

                with patch(
                    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload"
                ) as mock_update:
                    response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )

                    assert response.status_code == 200
                    assert response.json() == {"status": "processed"}
                    mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_subscription_resumed():
    event_id = _unique_id("evt_resumed")
    payload = f'{{"id": "{event_id}", "type": "customer.subscription.resumed"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        mock_event = MagicMock()
        mock_event.id = event_id
        mock_event.type = "customer.subscription.resumed"
        mock_event.livemode = False
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "sub_123"
        mock_event.data.object.customer = "cus_123"

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch(
                "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id"
            ) as mock_get_profile:
                mock_profile = MagicMock()
                mock_profile.user_id = 42
                mock_get_profile.return_value = mock_profile

                with patch(
                    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload"
                ) as mock_update:
                    response = client.post(
                        "/v1/billing/stripe-webhook", content=payload, headers=headers
                    )

                    assert response.status_code == 200
                    assert response.json() == {"status": "processed"}
                    mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_invalidates_billing_cache_for_next_read():
    BillingService.reset_subscription_status_cache()
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db,
            email=f"webhook-cache-{uuid.uuid4().hex[:8]}@example.com",
            password="strong-pass-123",
            role="user",
        )
        user_id = auth.user.id
        db.add(
            StripeBillingProfileModel(
                user_id=user_id,
                stripe_customer_id="cus_cache_test",
                subscription_status="incomplete",
                entitlement_plan="free",
            )
        )
        db.commit()

        before = BillingService.get_subscription_status_readonly(db, user_id=user_id)
        assert before.status == "inactive"
        assert before.subscription_status == "incomplete"
        assert before.plan is None

    event_id = _unique_id("evt_cache")
    payload = f'{{"id": "{event_id}", "type": "invoice.paid"}}'.encode()
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}

    mock_event = MagicMock()
    mock_event.id = event_id
    mock_event.type = "invoice.paid"
    mock_event.livemode = False
    mock_event.data.object = MagicMock()
    mock_event.data.object.id = "in_cache_123"
    mock_event.data.object.customer = "cus_cache_test"
    mock_event.to_dict.return_value = {
        "id": event_id,
        "type": "invoice.paid",
        "created": int(time.time()),
        "data": {
            "object": {
                "object": "subscription",
                "id": "sub_cache_123",
                "customer": "cus_cache_test",
                "status": "active",
                "items": {"data": [{"price": {"id": "price_basic"}}]},
            }
        },
    }

    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookService.verify_and_parse",
            return_value=mock_event,
        ):
            with patch.dict(
                "app.services.billing.stripe_billing_profile_service.STRIPE_PRICE_ENTITLEMENT_MAP",
                {"price_basic": "basic"},
                clear=True,
            ):
                response = client.post(
                    "/v1/billing/stripe-webhook", content=payload, headers=headers
                )

    assert response.status_code == 200
    assert response.json() == {"status": "processed"}

    with open_app_test_db_session() as db:
        after = BillingService.get_subscription_status_readonly(db, user_id=user_id)

    assert after.status == "active"
    assert after.subscription_status == "active"
    assert after.plan is not None
    assert after.plan.code == "basic"
