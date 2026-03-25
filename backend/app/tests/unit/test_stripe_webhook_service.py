from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import stripe
from sqlalchemy.orm import Session

from app.services.stripe_webhook_service import StripeWebhookService, StripeWebhookServiceError


@pytest.fixture
def db():
    return MagicMock(spec=Session)


class TestStripeWebhookService:
    def test_verify_and_parse_success(self):
        payload = b'{"id": "evt_123", "type": "checkout.session.completed"}'
        sig_header = "valid_sig"
        secret = "whsec_test"

        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_event = MagicMock()
            mock_event.id = "evt_123"
            mock_event.type = "checkout.session.completed"
            mock_construct.return_value = mock_event

            result = StripeWebhookService.verify_and_parse(payload, sig_header, secret)

            assert result.id == "evt_123"
            mock_construct.assert_called_once_with(payload, sig_header, secret)

    def test_verify_and_parse_invalid_signature(self):
        payload = b'{"id": "evt_123"}'
        sig_header = "invalid_sig"
        secret = "whsec_test"

        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.side_effect = stripe.error.SignatureVerificationError(
                "Invalid signature", "sig_header"
            )

            with pytest.raises(StripeWebhookServiceError) as exc:
                StripeWebhookService.verify_and_parse(payload, sig_header, secret)

            assert exc.value.code == "invalid_signature"

    def test_handle_checkout_session_completed(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_123"
        mock_event.type = "checkout.session.completed"
        mock_event.data.object = MagicMock()
        mock_event.data.object.client_reference_id = "42"
        mock_event.to_dict.return_value = {"id": "evt_123"}

        with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload") as mock_update:
            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "processed"
            mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_subscription_updated(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_456"
        mock_event.type = "customer.subscription.updated"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_456"}

        with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id") as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload") as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_customer_updated(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_789"
        mock_event.type = "customer.updated"
        mock_event.data.object = MagicMock()
        mock_event.data.object.id = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_789"}

        with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id") as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.update_from_event_payload") as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_unknown_event(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_000"
        mock_event.type = "unknown.event"

        result = StripeWebhookService.handle_event(db, mock_event)
        assert result == "event_ignored"

    def test_handle_user_not_found(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_456"
        mock_event.type = "customer.subscription.updated"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_unknown"

        with patch("app.services.stripe_billing_profile_service.StripeBillingProfileService.get_by_stripe_customer_id") as mock_get_profile:
            mock_get_profile.return_value = None

            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "user_not_resolved"
