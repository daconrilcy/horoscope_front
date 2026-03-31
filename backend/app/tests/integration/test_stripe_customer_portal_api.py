from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService

client = TestClient(app)


def _cleanup_tables():
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(StripeBillingProfileModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _get_profile_snapshot(email: str) -> dict[str, object]:
    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email=email).first()
        assert user is not None
        profile = db.query(StripeBillingProfileModel).filter_by(user_id=user.id).first()
        assert profile is not None
        return {
            "stripe_customer_id": profile.stripe_customer_id,
            "stripe_subscription_id": profile.stripe_subscription_id,
            "stripe_price_id": profile.stripe_price_id,
            "subscription_status": profile.subscription_status,
            "current_period_end": profile.current_period_end,
            "cancel_at_period_end": profile.cancel_at_period_end,
            "entitlement_plan": profile.entitlement_plan,
            "billing_email": profile.billing_email,
            "last_stripe_event_id": profile.last_stripe_event_id,
            "last_stripe_event_created": profile.last_stripe_event_created,
            "last_stripe_event_type": profile.last_stripe_event_type,
            "synced_at": profile.synced_at,
        }


@pytest.fixture
def clean_db():
    _cleanup_tables()
    with patch("app.api.v1.routers.billing.settings.stripe_portal_configuration_id", "bpc_test_123"):
        yield


class TestStripeCustomerPortalApi:
    def test_portal_session_auth_required(self, clean_db):
        response = client.post("/v1/billing/stripe-customer-portal-session")
        assert response.status_code == 401

    def test_portal_session_forbidden_role(self, clean_db):
        token = _register_user_with_role("support@example.com", "support")
        response = client.post(
            "/v1/billing/stripe-customer-portal-session",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "insufficient_role"

    def test_portal_session_profile_not_found(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        # No profile created yet
        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=MagicMock(),
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "stripe_billing_profile_not_found"

    def test_portal_session_no_customer_id(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(user_id=user.id, stripe_customer_id=None)
            db.add(profile)
            db.commit()

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=MagicMock(),
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "stripe_billing_profile_not_found"

    def test_portal_session_stripe_unavailable(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(user_id=user.id, stripe_customer_id="cus_123")
            db.add(profile)
            db.commit()

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client", return_value=None
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "stripe_unavailable"

    def test_portal_session_nominal_200(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
                stripe_price_id="price_basic",
                subscription_status="active",
                entitlement_plan="basic",
                billing_email="user@example.com",
                last_stripe_event_id="evt_existing",
                last_stripe_event_type="customer.subscription.updated",
            )
            db.add(profile)
            db.commit()

        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/p/session/test_123"
        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.return_value = mock_session
        before_snapshot = _get_profile_snapshot("user@example.com")

        with (
            patch(
                "app.services.stripe_customer_portal_service.get_stripe_client",
                return_value=mock_client,
            ),
            patch.object(
                EffectiveEntitlementResolverService,
                "resolve_b2c_user_snapshot",
                side_effect=AssertionError("portal endpoint must not recalculate entitlements"),
            ),
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://billing.stripe.com/p/session/test_123"
        assert "request_id" in response.json()["meta"]

        mock_client.billing_portal.sessions.create.assert_called_once()
        args, kwargs = mock_client.billing_portal.sessions.create.call_args
        assert kwargs["params"]["customer"] == "cus_123"
        assert "return_url" in kwargs["params"]
        after_snapshot = _get_profile_snapshot("user@example.com")
        assert after_snapshot == before_snapshot

    def test_portal_session_stripe_sdk_error_returns_502(self, clean_db):
        import stripe

        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                entitlement_plan="basic",
            )
            db.add(profile)
            db.commit()

        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.side_effect = stripe.StripeError("API down")

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=mock_client,
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 502
        assert response.json()["error"]["code"] == "stripe_api_error"

    def test_update_session_nominal_200(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
            )
            db.add(profile)
            db.commit()

        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/update"
        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.return_value = mock_session
        before_snapshot = _get_profile_snapshot("user@example.com")

        with (
            patch(
                "app.services.stripe_customer_portal_service.get_stripe_client",
                return_value=mock_client,
            ),
            patch.object(
                EffectiveEntitlementResolverService,
                "resolve_b2c_user_snapshot",
                side_effect=AssertionError("portal endpoint must not recalculate entitlements"),
            ),
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-subscription-update-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://billing.stripe.com/update"
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["flow_data"]["type"] == "subscription_update"
        assert params["flow_data"]["subscription_update"]["subscription"] == "sub_123"
        assert _get_profile_snapshot("user@example.com") == before_snapshot

    def test_cancel_session_nominal_200(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
            )
            db.add(profile)
            db.commit()

        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/cancel"
        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.return_value = mock_session
        before_snapshot = _get_profile_snapshot("user@example.com")

        with (
            patch(
                "app.services.stripe_customer_portal_service.get_stripe_client",
                return_value=mock_client,
            ),
            patch.object(
                EffectiveEntitlementResolverService,
                "resolve_b2c_user_snapshot",
                side_effect=AssertionError("portal endpoint must not recalculate entitlements"),
            ),
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-subscription-cancel-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://billing.stripe.com/cancel"
        params = mock_client.billing_portal.sessions.create.call_args[1]["params"]
        assert params["flow_data"]["type"] == "subscription_cancel"
        assert params["flow_data"]["subscription_cancel"]["subscription"] == "sub_123"
        assert _get_profile_snapshot("user@example.com") == before_snapshot

    def test_update_session_no_subscription_404(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id=None,
            )
            db.add(profile)
            db.commit()

        response = client.post(
            "/v1/billing/stripe-customer-portal-subscription-update-session",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "stripe_subscription_not_found"

    def test_cancel_session_no_subscription_404(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id=None,
            )
            db.add(profile)
            db.commit()

        response = client.post(
            "/v1/billing/stripe-customer-portal-subscription-cancel-session",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "stripe_subscription_not_found"

    def test_update_session_stripe_unavailable(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
            )
            db.add(profile)
            db.commit()

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=None,
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-subscription-update-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "stripe_unavailable"

    def test_update_session_stripe_api_error(self, clean_db):
        import stripe

        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
            )
            db.add(profile)
            db.commit()

        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.side_effect = stripe.StripeError("API down")

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=mock_client,
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-subscription-update-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 502
        assert response.json()["error"]["code"] == "stripe_api_error"

    def test_update_session_returns_422_when_subscription_update_feature_is_disabled(
        self, clean_db
    ):
        import stripe

        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
            )
            db.add(profile)
            db.commit()

        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.side_effect = stripe.InvalidRequestError(
            message=(
                "This subscription cannot be updated because the subscription update "
                "feature in the portal configuration is disabled."
            ),
            param=None,
        )

        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=mock_client,
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-subscription-update-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "stripe_portal_subscription_update_disabled"

    def test_update_session_returns_422_for_trialing_subscription(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
                stripe_subscription_id="sub_123",
                subscription_status="trialing",
                entitlement_plan="basic",
            )
            db.add(profile)
            db.commit()

        response = client.post(
            "/v1/billing/stripe-customer-portal-subscription-update-session",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        assert (
            response.json()["error"]["code"]
            == "stripe_portal_subscription_update_not_allowed_for_trial"
        )

    def test_update_session_no_jwt_401(self, clean_db):
        response = client.post("/v1/billing/stripe-customer-portal-subscription-update-session")
        assert response.status_code == 401

    def test_cancel_session_no_jwt_401(self, clean_db):
        response = client.post("/v1/billing/stripe-customer-portal-subscription-cancel-session")
        assert response.status_code == 401

    def test_portal_session_missing_configuration_503(self, clean_db):
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
            )
            db.add(profile)
            db.commit()

        # Mock settings.stripe_portal_configuration_id to None
        with patch("app.api.v1.routers.billing.settings.stripe_portal_configuration_id", None):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "stripe_portal_configuration_missing"

    def test_portal_session_invalid_configuration_502(self, clean_db):
        import stripe
        token = _register_user_with_role("user@example.com", "user")
        with SessionLocal() as db:
            user = db.query(UserModel).filter_by(email="user@example.com").first()
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id="cus_123",
            )
            db.add(profile)
            db.commit()

        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.side_effect = stripe.InvalidRequestError(
            message="No such configuration: 'bpc_invalid'",
            param="configuration"
        )
        with patch(
            "app.services.stripe_customer_portal_service.get_stripe_client",
            return_value=mock_client,
        ):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 502
        assert response.json()["error"]["code"] == "stripe_api_error"
