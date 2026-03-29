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


@pytest.fixture
def clean_db():
    _cleanup_tables()
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
        with patch("app.services.stripe_customer_portal_service.get_stripe_client", return_value=MagicMock()):
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

        with patch("app.services.stripe_customer_portal_service.get_stripe_client", return_value=MagicMock()):
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

        with patch("app.services.stripe_customer_portal_service.get_stripe_client", return_value=None):
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
            profile = StripeBillingProfileModel(user_id=user.id, stripe_customer_id="cus_123")
            db.add(profile)
            db.commit()

        mock_session = MagicMock()
        mock_session.url = "https://billing.stripe.com/p/session/test_123"
        mock_client = MagicMock()
        mock_client.billing_portal.sessions.create.return_value = mock_session

        with patch("app.services.stripe_customer_portal_service.get_stripe_client", return_value=mock_client):
            response = client.post(
                "/v1/billing/stripe-customer-portal-session",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert response.json()["data"]["url"] == "https://billing.stripe.com/p/session/test_123"
        assert "request_id" in response.json()["meta"]
        
        # Verify call parameters
        mock_client.billing_portal.sessions.create.assert_called_once()
        args, kwargs = mock_client.billing_portal.sessions.create.call_args
        assert kwargs["params"]["customer"] == "cus_123"
        assert "return_url" in kwargs["params"]
