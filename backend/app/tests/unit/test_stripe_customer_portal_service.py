import pytest
from unittest.mock import MagicMock, patch
import stripe
from app.services.stripe_customer_portal_service import (
    StripeCustomerPortalService,
    StripeCustomerPortalServiceError,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel

class TestStripeCustomerPortalService:
    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_success(self, mock_get_profile, mock_get_client):
        # Arrange
        db = MagicMock()
        user_id = 123
        return_url = "http://localhost:5173/return"
        stripe_customer_id = "cus_123"
        portal_url = "https://billing.stripe.com/session/123"

        mock_profile = StripeBillingProfileModel(user_id=user_id, stripe_customer_id=stripe_customer_id)
        mock_get_profile.return_return_value = mock_profile # This is wrong, should be return_value
        # Wait, I used return_return_value by mistake. Let me fix it.
        mock_get_profile.return_value = mock_profile

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_session = MagicMock()
        mock_session.url = portal_url
        mock_client.billing_portal.sessions.create.return_value = mock_session

        # Act
        result = StripeCustomerPortalService.create_portal_session(
            db, user_id=user_id, return_url=return_url
        )

        # Assert
        assert result == portal_url
        mock_get_profile.assert_called_once_with(db, user_id)
        mock_client.billing_portal.sessions.create.assert_called_once_with(
            params={"customer": stripe_customer_id, "return_url": return_url}
        )

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_no_profile(self, mock_get_profile, mock_get_client):
        # Arrange
        db = MagicMock()
        mock_get_profile.return_value = None
        mock_get_client.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db, user_id=123, return_url="http://return"
            )
        assert exc.value.code == "stripe_billing_profile_not_found"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_no_customer_id(self, mock_get_profile, mock_get_client):
        # Arrange
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(user_id=123, stripe_customer_id=None)
        mock_get_client.return_value = MagicMock()

        # Act & Assert
        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db, user_id=123, return_url="http://return"
            )
        assert exc.value.code == "stripe_billing_profile_not_found"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    def test_create_portal_session_stripe_unavailable(self, mock_get_client):
        # Arrange
        mock_get_client.return_value = None

        # Act & Assert
        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                MagicMock(), user_id=123, return_url="http://return"
            )
        assert exc.value.code == "stripe_unavailable"

    @patch("app.services.stripe_customer_portal_service.get_stripe_client")
    @patch("app.services.stripe_customer_portal_service.StripeBillingProfileService.get_by_user_id")
    def test_create_portal_session_stripe_error(self, mock_get_profile, mock_get_client):
        # Arrange
        db = MagicMock()
        mock_get_profile.return_value = StripeBillingProfileModel(user_id=123, stripe_customer_id="cus_123")
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.billing_portal.sessions.create.side_effect = stripe.StripeError("API Error")

        # Act & Assert
        with pytest.raises(StripeCustomerPortalServiceError) as exc:
            StripeCustomerPortalService.create_portal_session(
                db, user_id=123, return_url="http://return"
            )
        assert exc.value.code == "stripe_api_error"
