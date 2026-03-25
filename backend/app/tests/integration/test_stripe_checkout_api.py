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

def test_stripe_checkout_auth_required(clean_db):
    response = client.post("/v1/billing/stripe-checkout-session", json={"plan": "basic"})
    assert response.status_code == 401

def test_stripe_checkout_forbidden_role(clean_db):
    token = _register_user_with_role("support@example.com", "support")
    response = client.post(
        "/v1/billing/stripe-checkout-session",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan": "basic"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"

def test_stripe_checkout_invalid_plan(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    response = client.post(
        "/v1/billing/stripe-checkout-session",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan": "gold"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_checkout_request"

def test_stripe_checkout_stripe_unavailable(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    with patch("app.services.stripe_checkout_service.get_stripe_client", return_value=None):
        response = client.post(
            "/v1/billing/stripe-checkout-session",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic"}
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "stripe_unavailable"

def test_stripe_checkout_nominal_200(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_nominal"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch("app.services.stripe_checkout_service.get_stripe_client", return_value=mock_client):
        # We also need to mock the price map to ensure "basic" is found
        with patch(
            "app.services.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
            {"price_123": "basic"},
        ):
            response = client.post(
                "/v1/billing/stripe-checkout-session",
                headers={"Authorization": f"Bearer {token}"},
                json={"plan": "basic"},
            )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_nominal"

    # Verify audit event (indirectly by checking if it didn't crash)
    assert "request_id" in response.json()["meta"]


def test_stripe_checkout_plan_not_configured(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    mock_client = MagicMock()
    with patch("app.services.stripe_checkout_service.get_stripe_client", return_value=mock_client):
        with patch("app.services.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP", {}):
            response = client.post(
                "/v1/billing/stripe-checkout-session",
                headers={"Authorization": f"Bearer {token}"},
                json={"plan": "basic"}
            )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "plan_price_not_configured"
