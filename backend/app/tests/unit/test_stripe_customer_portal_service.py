from unittest.mock import MagicMock, patch

import pytest
import stripe

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.services.stripe_customer_portal_service import (
    StripeCustomerPortalService,
    StripeCustomerPortalServiceError,
)


class TestStripeCustomerPortalService:
    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_success(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        user_id = 123
        return_url = "http://localhost:5173/return"
        stripe_customer_id = "cus_123"
        portal_url = "https://billing.stripe.com/session/123"

        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = portal_url
        mock_client.billing_portal.sessions.create.return_value = mock_session

        result = StripeCustomerPortalService.create_portal_session(
            db,
            user_id=user_id,
            return_url=return_url,
            configuration_id="bpc_123",
        )

        assert result == portal_url
        mock_get_profile.assert_called_once_with(db, user_id)
        mock_get_client.assert_called_once_with()
        mock_client.billing_portal.sessions.create.assert_called_once_with(
            params={
                "customer": stripe_customer_id,
                "return_url": return_url,
                "configuration": "bpc_123",
            }
        )

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_no_profile(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = None

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_billing_profile_not_found"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_no_customer_id(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id=None,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_billing_profile_not_found"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_stripe_unavailable(self, mock_get_profile, mock_get_client):
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
        )
        mock_get_client.return_value = None

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                MagicMock(),
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_unavailable"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_stripe_error(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.billing_portal.sessions.create.side_effect = stripe.StripeError("API Error")

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_api_error"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_update_session_success(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        user_id = 123
        return_url = "http://localhost:5173/return"
        stripe_customer_id = "cus_123"
        stripe_subscription_id = "sub_123"
        portal_url = "https://billing.stripe.com/session/123"

        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = portal_url
        mock_client.billing_portal.sessions.create.return_value = mock_session

        result = StripeCustomerPortalService.create_subscription_update_session(
            db,
            user_id=user_id,
            return_url=return_url,
            configuration_id="bpc_123",
        )

        assert result == portal_url
        mock_client.billing_portal.sessions.create.assert_called_once()
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["customer"] == stripe_customer_id
        assert params["flow_data"]["type"] == "subscription_update"
        assert params["flow_data"]["subscription_update"]["subscription"] == stripe_subscription_id

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_cancel_session_success(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        user_id = 123
        return_url = "http://localhost:5173/return"
        stripe_customer_id = "cus_123"
        stripe_subscription_id = "sub_123"
        portal_url = "https://billing.stripe.com/session/123"

        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = portal_url
        mock_client.billing_portal.sessions.create.return_value = mock_session

        result = StripeCustomerPortalService.create_subscription_cancel_session(
            db,
            user_id=user_id,
            return_url=return_url,
            configuration_id="bpc_123",
        )

        assert result == portal_url
        mock_client.billing_portal.sessions.create.assert_called_once()
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["customer"] == stripe_customer_id
        assert params["flow_data"]["type"] == "subscription_cancel"
        assert params["flow_data"]["subscription_cancel"]["subscription"] == stripe_subscription_id

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_cancel_session_rejects_already_scheduled_cancellation(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            cancel_at_period_end=True,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_cancel_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_portal_subscription_cancel_already_scheduled"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_no_subscription_id(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id=None,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_subscription_not_found"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_cancel_session_no_subscription_id(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id=None,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_cancel_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_subscription_not_found"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_no_profile(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = None

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_subscription_not_found"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_stripe_unavailable(self, mock_get_profile, mock_get_client):
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
        )
        mock_get_client.return_value = None

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                MagicMock(),
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_unavailable"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_stripe_error(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.billing_portal.sessions.create.side_effect = stripe.StripeError("API Error")

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_api_error"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_maps_missing_change_options_to_actionable_error(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.billing_portal.sessions.create.side_effect = stripe.InvalidRequestError(
            message=(
                "The subscription cannot be updated because there is no price in the "
                "portal configuration available to change to and the quantity cannot be changed."
            ),
            param=None,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_portal_subscription_update_no_change_options"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_rejects_trialing_subscription(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="trialing",
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_update_session(
                db,
                user_id=123,
                return_url="http://return",
                configuration_id="bpc_123",
            )

        assert exc.value.code == "stripe_portal_subscription_update_not_allowed_for_trial"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_update_session_with_configuration_id(self, mock_get_profile, mock_get_client):
        db = MagicMock()
        user_id = 123
        configuration_id = "bpc_123"
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = "http://portal"
        mock_client.billing_portal.sessions.create.return_value = mock_session

        StripeCustomerPortalService.create_subscription_update_session(
            db,
            user_id=user_id,
            return_url="http://return",
            configuration_id=configuration_id,
        )

        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["configuration"] == configuration_id

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_requires_configuration_id(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        user_id = 123
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id="cus_123",
        )

        # Should raise stripe_portal_configuration_missing if configuration_id is None
        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db,
                user_id=user_id,
                return_url="http://return",
                configuration_id=None,
            )
        assert exc.value.code == "stripe_portal_configuration_missing"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_uses_explicit_configuration_id(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        user_id = 123
        configuration_id = "bpc_123"
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=user_id,
            stripe_customer_id="cus_123",
        )
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = "http://portal"
        mock_client.billing_portal.sessions.create.return_value = mock_session

        StripeCustomerPortalService.create_portal_session(
            db,
            user_id=user_id,
            return_url="http://return",
            configuration_id=configuration_id,
        )

        mock_client.billing_portal.sessions.create.assert_called_once()
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["configuration"] == configuration_id

    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.update_from_event_payload")
    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_reactivate_subscription_success(
        self, mock_get_profile, mock_get_client, mock_update_from_event_payload
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            cancel_at_period_end=True,
        )
        updated_profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            cancel_at_period_end=False,
        )
        mock_get_profile.return_value = profile
        mock_update_from_event_payload.return_value = updated_profile
        mock_subscription = MagicMock()
        mock_subscription.to_dict.return_value = {"object": "subscription", "id": "sub_123"}
        mock_client = MagicMock()
        mock_client.subscriptions.update.return_value = mock_subscription
        mock_get_client.return_value = mock_client

        result = StripeCustomerPortalService.reactivate_subscription(db, user_id=123)

        assert result is updated_profile
        mock_client.subscriptions.update.assert_called_once_with(
            "sub_123",
            params={
                "cancel_at_period_end": False,
                "proration_behavior": "none",
            },
        )
        mock_update_from_event_payload.assert_called_once()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_reactivate_subscription_rejects_when_not_scheduled(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            cancel_at_period_end=False,
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.reactivate_subscription(db, user_id=123)

        assert exc.value.code == "stripe_subscription_reactivation_not_needed"
        mock_get_client.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_subscription_upgrade_payment_success(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic",
        )
        current_item = MagicMock()
        current_item.id = "si_123"
        current_item.quantity = 1
        current_price = MagicMock()
        current_price.id = "price_basic"
        current_item.price = current_price
        current_subscription = MagicMock()
        current_subscription.items.data = [current_item]
        preview_invoice = MagicMock()
        preview_invoice.to_dict_recursive.return_value = {
            "amount_due": 2000,
            "currency": "eur",
            "lines": {
                "data": [
                    {
                        "amount": -900,
                        "proration": True,
                        "price": {"id": "price_basic"},
                    },
                    {
                        "amount": 2900,
                        "proration": True,
                        "price": {"id": "price_premium"},
                    },
                ]
            },
        }
        checkout_session = MagicMock()
        checkout_session.url = "https://checkout.stripe.com/pay/cs_123"

        mock_client = MagicMock()
        mock_client.subscriptions.retrieve.return_value = current_subscription
        mock_client.invoices.create_preview.return_value = preview_invoice
        mock_client.checkout.sessions.create.return_value = checkout_session
        mock_get_client.return_value = mock_client
        mock_get_profile.return_value = profile

        with patch(
            "app.services.stripe_customer_portal_service.settings.stripe_price_premium",
            "price_premium",
        ):
            result = StripeCustomerPortalService.create_subscription_upgrade_payment(
                db,
                user_id=123,
                target_plan="premium",
            )

        assert result.checkout_url == "https://checkout.stripe.com/pay/cs_123"
        assert result.invoice_status == "requires_payment"
        assert result.amount_due_cents == 2000
        assert result.currency == "eur"
        mock_client.invoices.create_preview.assert_called_once_with(
            params={
                "customer": "cus_123",
                "subscription": "sub_123",
                "subscription_details": {
                    "items": [{"id": "si_123", "price": "price_premium", "quantity": 1}],
                    "proration_date": mock_client.invoices.create_preview.call_args[1]["params"][
                        "subscription_details"
                    ]["proration_date"],
                },
            }
        )
        mock_client.checkout.sessions.create.assert_called_once()
        checkout_params = mock_client.checkout.sessions.create.call_args[1]["params"]
        assert checkout_params["mode"] == "payment"
        assert checkout_params["customer"] == "cus_123"
        assert checkout_params["line_items"][0]["price_data"]["unit_amount"] == 2000
        assert checkout_params["metadata"]["billing_operation"] == "subscription_upgrade"
        assert checkout_params["metadata"]["stripe_subscription_item_id"] == "si_123"
        assert checkout_params["metadata"]["target_plan"] == "premium"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_subscription_upgrade_payment_ignores_next_renewal_line_in_preview(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic",
        )
        current_item = MagicMock()
        current_item.id = "si_123"
        current_item.quantity = 1
        current_price = MagicMock()
        current_price.id = "price_basic"
        current_item.price = current_price
        current_subscription = MagicMock()
        current_subscription.items.data = [current_item]
        preview_invoice = MagicMock()
        preview_invoice.to_dict_recursive.return_value = {
            "amount_due": 4900,
            "currency": "eur",
            "lines": {
                "data": [
                    {
                        "amount": -900,
                        "proration": True,
                        "price": {"id": "price_basic"},
                    },
                    {
                        "amount": 2900,
                        "proration": True,
                        "price": {"id": "price_premium"},
                    },
                    {
                        "amount": 2900,
                        "proration": False,
                        "price": {"id": "price_premium"},
                    },
                ]
            },
        }
        checkout_session = MagicMock()
        checkout_session.url = "https://checkout.stripe.com/pay/cs_123"

        mock_client = MagicMock()
        mock_client.subscriptions.retrieve.return_value = current_subscription
        mock_client.invoices.create_preview.return_value = preview_invoice
        mock_client.checkout.sessions.create.return_value = checkout_session
        mock_get_client.return_value = mock_client
        mock_get_profile.return_value = profile

        with patch(
            "app.services.stripe_customer_portal_service.settings.stripe_price_premium",
            "price_premium",
        ):
            result = StripeCustomerPortalService.create_subscription_upgrade_payment(
                db,
                user_id=123,
                target_plan="premium",
            )

        assert result.amount_due_cents == 2000
        checkout_params = mock_client.checkout.sessions.create.call_args[1]["params"]
        assert checkout_params["line_items"][0]["price_data"]["unit_amount"] == 2000

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_subscription_upgrade_payment_rejects_invalid_proration_preview(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic",
        )
        current_item = MagicMock()
        current_item.id = "si_123"
        current_item.quantity = 1
        current_price = MagicMock()
        current_price.id = "price_basic"
        current_item.price = current_price
        current_subscription = MagicMock()
        current_subscription.items.data = [current_item]
        preview_invoice = MagicMock()
        preview_invoice.to_dict_recursive.return_value = {
            "amount_due": 2900,
            "currency": "eur",
            "lines": {
                "data": [
                    {
                        "amount": 2900,
                        "proration": True,
                        "price": {"id": "price_premium"},
                    }
                ]
            },
        }

        mock_client = MagicMock()
        mock_client.subscriptions.retrieve.return_value = current_subscription
        mock_client.invoices.create_preview.return_value = preview_invoice
        mock_get_client.return_value = mock_client
        mock_get_profile.return_value = profile

        with (
            patch(
                "app.services.stripe_customer_portal_service.settings.stripe_price_premium",
                "price_premium",
            ),
            pytest.raises(StripeCustomerPortalServiceError) as exc,
        ):
            StripeCustomerPortalService.create_subscription_upgrade_payment(
                db,
                user_id=123,
                target_plan="premium",
            )

        assert exc.value.code == "stripe_subscription_upgrade_invalid_proration_preview"
        mock_client.checkout.sessions.create.assert_not_called()

    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.update_from_event_payload")
    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_apply_paid_subscription_upgrade_checkout_session_success(
        self, mock_get_profile, mock_get_client, mock_update_from_event_payload
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic",
            stripe_price_id="price_basic",
        )
        updated_profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="premium",
            stripe_price_id="price_premium",
        )
        subscription = MagicMock()
        subscription.to_dict.return_value = {"object": "subscription", "id": "sub_123"}
        mock_client = MagicMock()
        mock_client.subscriptions.update.return_value = subscription
        mock_get_client.return_value = mock_client
        mock_get_profile.return_value = profile
        mock_update_from_event_payload.return_value = updated_profile

        result = StripeCustomerPortalService.apply_paid_subscription_upgrade_checkout_session(
            db,
            session={
                "customer": "cus_123",
                "payment_status": "paid",
                "metadata": {
                    "app_user_id": "123",
                    "billing_operation": "subscription_upgrade",
                    "stripe_subscription_id": "sub_123",
                    "stripe_subscription_item_id": "si_123",
                    "target_price_id": "price_premium",
                    "target_plan": "premium",
                    "quantity": "1",
                },
            },
        )

        assert result is updated_profile
        mock_client.subscriptions.update.assert_called_once_with(
            "sub_123",
            params={
                "items": [{"id": "si_123", "price": "price_premium", "quantity": 1}],
                "billing_cycle_anchor": "unchanged",
                "proration_behavior": "none",
            },
        )

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_subscription_upgrade_payment_selects_current_plan_item(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        profile = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic",
            stripe_price_id="price_basic",
        )
        extra_item = {"id": "si_extra", "quantity": 1, "price": {"id": "price_other"}}
        current_item = {"id": "si_basic", "quantity": 1, "price": {"id": "price_basic"}}
        current_subscription = {"items": {"data": [extra_item, current_item]}}
        preview_invoice = MagicMock()
        preview_invoice.to_dict_recursive.return_value = {
            "amount_due": 2000,
            "currency": "eur",
            "lines": {
                "data": [
                    {
                        "amount": -900,
                        "proration": True,
                        "price": {"id": "price_basic"},
                    },
                    {
                        "amount": 2900,
                        "proration": True,
                        "price": {"id": "price_premium"},
                    },
                ]
            },
        }
        mock_client = MagicMock()
        mock_client.subscriptions.retrieve.return_value = current_subscription
        mock_client.invoices.create_preview.return_value = preview_invoice
        mock_client.checkout.sessions.create.return_value = MagicMock(url="https://checkout")
        mock_get_client.return_value = mock_client
        mock_get_profile.return_value = profile

        with patch(
            "app.services.stripe_customer_portal_service.settings.stripe_price_premium",
            "price_premium",
        ):
            StripeCustomerPortalService.create_subscription_upgrade_payment(
                db,
                user_id=123,
                target_plan="premium",
            )

        preview_params = mock_client.invoices.create_preview.call_args[1]["params"]
        assert preview_params["subscription_details"]["items"] == [
            {"id": "si_basic", "price": "price_premium", "quantity": 1}
        ]

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_subscription_upgrade_payment_rejects_non_upgrade(
        self, mock_get_profile, mock_get_client
    ):
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(
            user_id=123,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="premium",
        )

        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_subscription_upgrade_payment(
                db,
                user_id=123,
                target_plan="basic",
            )

        assert exc.value.code == "stripe_subscription_upgrade_not_allowed"
        mock_get_client.assert_not_called()
