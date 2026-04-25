from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import stripe
from sqlalchemy.orm import Session

from app.services.billing.stripe_webhook_service import (
    StripeWebhookService,
    StripeWebhookServiceError,
)

STRIPE_BILLING_SERVICE_PATH = (
    "app.services.billing.stripe_billing_profile_service.StripeBillingProfileService"
)
UPDATE_EVENT_PAYLOAD_PATH = f"{STRIPE_BILLING_SERVICE_PATH}.update_from_event_payload"
GET_BY_CUSTOMER_ID_PATH = f"{STRIPE_BILLING_SERVICE_PATH}.get_by_stripe_customer_id"


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
        mock_event.data.object.metadata = {}
        mock_event.data.object.client_reference_id = "42"
        mock_event.to_dict.return_value = {"id": "evt_123"}

        with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "processed"
            mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_checkout_session_completed_for_subscription_upgrade(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_upgrade_123"
        mock_event.type = "checkout.session.completed"
        mock_event.data.object = {
            "customer": "cus_123",
            "payment_status": "paid",
            "metadata": {
                "billing_operation": "subscription_upgrade",
                "app_user_id": "42",
                "stripe_subscription_id": "sub_123",
                "stripe_subscription_item_id": "si_123",
                "target_price_id": "price_premium",
                "target_plan": "premium",
                "quantity": "1",
            },
        }

        with patch(
            "app.services.billing.stripe_webhook_service.StripeCustomerPortalService."
            "apply_paid_subscription_upgrade_checkout_session"
        ) as mock_apply:
            result = StripeWebhookService.handle_event(db, mock_event)

        assert result == "processed"
        mock_apply.assert_called_once_with(db, session=mock_event.data.object)

    def test_handle_subscription_updated(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_456"
        mock_event.type = "customer.subscription.updated"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_456"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
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

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_invoice_paid(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_inv_paid"
        mock_event.type = "invoice.paid"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_inv_paid"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_invoice_payment_failed(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_inv_fail"
        mock_event.type = "invoice.payment_failed"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_inv_fail"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_invoice_paid_user_not_resolved(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_inv_unkn"
        mock_event.type = "invoice.paid"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_unknown"

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_get_profile.return_value = None

            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "user_not_resolved"

    def test_handle_unknown_event(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_000"
        mock_event.type = "unknown.event"
        mock_event.data.object = MagicMock()

        result = StripeWebhookService.handle_event(db, mock_event)
        assert result == "event_ignored"

    def test_handle_user_not_found(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_456"
        mock_event.type = "customer.subscription.updated"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_unknown"

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_get_profile.return_value = None

            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "user_not_resolved"

    def test_handle_invoice_payment_action_required(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_inv_act"
        mock_event.type = "invoice.payment_action_required"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_inv_act"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_invoice_payment_action_required_user_not_resolved(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_inv_act_unkn"
        mock_event.type = "invoice.payment_action_required"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_unknown"

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_get_profile.return_value = None

            result = StripeWebhookService.handle_event(db, mock_event)

            assert result == "user_not_resolved"

    def test_invoice_payment_succeeded_is_now_ignored(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_test_legacy"
        mock_event.type = "invoice.payment_succeeded"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_test123"

        result = StripeWebhookService.handle_event(db, mock_event)
        assert result == "event_ignored"

    def test_handle_invoice_paid_is_idempotent_same_event_id_twice(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_idempotent"
        mock_event.type = "invoice.paid"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_idempotent"}

        with patch(
            "app.services.billing.stripe_webhook_service.StripeWebhookIdempotencyService.claim_event",
            side_effect=["accepted", "duplicate_ignored"],
        ) as mock_claim:
            with patch(
                "app.services.billing.stripe_webhook_service.StripeWebhookIdempotencyService.mark_processed"
            ) as mock_mark_processed:
                with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
                    mock_profile = MagicMock()
                    mock_profile.user_id = 42
                    mock_get_profile.return_value = mock_profile

                    with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                        result1 = StripeWebhookService.handle_event(db, mock_event)
                        result2 = StripeWebhookService.handle_event(db, mock_event)

        assert result1 == "processed"
        assert result2 == "duplicate_ignored"
        assert mock_claim.call_count == 2
        mock_update.assert_called_once_with(db, 42, mock_event.to_dict())
        mock_mark_processed.assert_called_once_with(db, "evt_idempotent")

    def test_handle_subscription_paused(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_sub_paused"
        mock_event.type = "customer.subscription.paused"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_sub_paused"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_subscription_resumed(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_sub_resumed"
        mock_event.type = "customer.subscription.resumed"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_sub_resumed"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())

    def test_handle_subscription_trial_will_end(self, db):
        mock_event = MagicMock()
        mock_event.id = "evt_sub_trial_will_end"
        mock_event.type = "customer.subscription.trial_will_end"
        mock_event.data.object = MagicMock()
        mock_event.data.object.customer = "cus_123"
        mock_event.to_dict.return_value = {"id": "evt_sub_trial_will_end"}

        with patch(GET_BY_CUSTOMER_ID_PATH) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.user_id = 42
            mock_get_profile.return_value = mock_profile

            with patch(UPDATE_EVENT_PAYLOAD_PATH) as mock_update:
                result = StripeWebhookService.handle_event(db, mock_event)

                assert result == "processed"
                mock_update.assert_called_once_with(db, 42, mock_event.to_dict())
