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
        )

        assert result == portal_url
        mock_get_profile.assert_called_once_with(db, user_id)
        mock_get_client.assert_called_once_with()
        mock_client.billing_portal.sessions.create.assert_called_once_with(
            params={"customer": stripe_customer_id, "return_url": return_url}
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
        )

        assert result == portal_url
        mock_client.billing_portal.sessions.create.assert_called_once()
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["customer"] == stripe_customer_id
        assert params["flow_data"]["type"] == "subscription_update"
        assert (
            params["flow_data"]["subscription_update"]["subscription"] == stripe_subscription_id
        )

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
        )

        assert result == portal_url
        mock_client.billing_portal.sessions.create.assert_called_once()
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["customer"] == stripe_customer_id
        assert params["flow_data"]["type"] == "subscription_cancel"
        assert (
            params["flow_data"]["subscription_cancel"]["subscription"] == stripe_subscription_id
        )

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
            )

        assert exc.value.code == "stripe_subscription_not_found"
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

