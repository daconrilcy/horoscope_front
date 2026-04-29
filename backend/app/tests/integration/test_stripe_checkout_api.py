from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing.service import BillingService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session

client = TestClient(app)


def _cleanup_tables():
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(StripeBillingProfileModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role(email: str, role: str) -> str:
    with open_app_test_db_session() as db:
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
        json={"plan": "basic"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_stripe_checkout_invalid_plan(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    response = client.post(
        "/v1/billing/stripe-checkout-session",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan": "gold"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_checkout_request"


def test_stripe_checkout_stripe_unavailable(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    with patch("app.services.billing.stripe_checkout_service.get_stripe_client", return_value=None):
        response = client.post(
            "/v1/billing/stripe-checkout-session",
            headers={"Authorization": f"Bearer {token}"},
            json={"plan": "basic"},
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "stripe_unavailable"


def test_stripe_checkout_nominal_200(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_nominal"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch(
        "app.services.billing.stripe_checkout_service.get_stripe_client", return_value=mock_client
    ):
        # We also need to mock the price map to ensure "basic" is found
        with patch(
            "app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
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
    assert "request_id" in response.json()["meta"]

    # Verify client_reference_id and metadata.app_user_id are correctly set in Stripe params
    with open_app_test_db_session() as db:
        user = db.query(UserModel).filter_by(email="user@example.com").first()
        user_id = str(user.id)
    call_kwargs = mock_client.checkout.sessions.create.call_args
    params = call_kwargs[1]["params"] if call_kwargs[1] else call_kwargs[0][0]
    assert params["client_reference_id"] == user_id
    assert params["metadata"]["app_user_id"] == user_id


def test_stripe_checkout_plan_not_configured(clean_db):
    token = _register_user_with_role("user@example.com", "user")
    mock_client = MagicMock()
    with patch(
        "app.services.billing.stripe_checkout_service.get_stripe_client", return_value=mock_client
    ):
        with patch("app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP", {}):
            response = client.post(
                "/v1/billing/stripe-checkout-session",
                headers={"Authorization": f"Bearer {token}"},
                json={"plan": "basic"},
            )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "plan_price_not_configured"


def test_stripe_checkout_with_tax_enabled(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_tax"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch("app.api.v1.routers.public.billing.settings") as mock_settings:
        mock_settings.stripe_tax_enabled = True
        mock_settings.stripe_tax_id_collection_enabled = True
        mock_settings.stripe_checkout_billing_address_collection = "required"
        mock_settings.stripe_checkout_success_url = "http://s"
        mock_settings.stripe_checkout_cancel_url = "http://c"
        # Story 61.55 defaults to prevent TypeError
        mock_settings.stripe_trial_enabled = False
        mock_settings.stripe_trial_period_days = 0
        mock_settings.stripe_payment_method_collection = "always"
        mock_settings.stripe_trial_missing_payment_method_behavior = None

        with patch(
            "app.services.billing.stripe_checkout_service.get_stripe_client",
            return_value=mock_client,
        ):
            with patch(
                "app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
                {"price_123": "basic"},
            ):
                response = client.post(
                    "/v1/billing/stripe-checkout-session",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"plan": "basic"},
                )

    assert response.status_code == 200
    call_kwargs = mock_client.checkout.sessions.create.call_args
    params = call_kwargs[1]["params"] if call_kwargs[1] else call_kwargs[0][0]
    assert params["automatic_tax"]["enabled"] is True
    assert params["tax_id_collection"]["enabled"] is True
    assert params["billing_address_collection"] == "required"


def test_stripe_checkout_tax_disabled_no_regression(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_notax"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch("app.api.v1.routers.public.billing.settings") as mock_settings:
        mock_settings.stripe_tax_enabled = False
        mock_settings.stripe_tax_id_collection_enabled = False
        mock_settings.stripe_checkout_billing_address_collection = "auto"
        mock_settings.stripe_checkout_success_url = "http://s"
        mock_settings.stripe_checkout_cancel_url = "http://c"
        # Story 61.55 defaults to prevent TypeError
        mock_settings.stripe_trial_enabled = False
        mock_settings.stripe_trial_period_days = 0
        mock_settings.stripe_payment_method_collection = "always"
        mock_settings.stripe_trial_missing_payment_method_behavior = None

        with patch(
            "app.services.billing.stripe_checkout_service.get_stripe_client",
            return_value=mock_client,
        ):
            with patch(
                "app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
                {"price_123": "basic"},
            ):
                response = client.post(
                    "/v1/billing/stripe-checkout-session",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"plan": "basic"},
                )

    assert response.status_code == 200
    call_kwargs = mock_client.checkout.sessions.create.call_args
    params = call_kwargs[1]["params"] if call_kwargs[1] else call_kwargs[0][0]
    assert "automatic_tax" not in params
    assert "tax_id_collection" not in params


def test_stripe_checkout_audit_enriched_with_tax_flags(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_audit"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch("app.api.v1.routers.public.billing.settings") as mock_settings:
        mock_settings.stripe_tax_enabled = True
        mock_settings.stripe_tax_id_collection_enabled = False
        mock_settings.stripe_checkout_billing_address_collection = "auto"
        mock_settings.stripe_checkout_success_url = "http://s"
        mock_settings.stripe_checkout_cancel_url = "http://c"
        # Story 61.55 defaults to prevent TypeError
        mock_settings.stripe_trial_enabled = False
        mock_settings.stripe_trial_period_days = 0
        mock_settings.stripe_payment_method_collection = "always"
        mock_settings.stripe_trial_missing_payment_method_behavior = None

        with patch(
            "app.services.billing.stripe_checkout_service.get_stripe_client",
            return_value=mock_client,
        ):
            with patch(
                "app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
                {"price_123": "basic"},
            ):
                with patch("app.api.v1.routers.public.billing._record_audit_event") as mock_audit:
                    client.post(
                        "/v1/billing/stripe-checkout-session",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"plan": "basic"},
                    )

    # Verify audit details
    # Last call to _record_audit_event in the try block
    success_call = [
        call for call in mock_audit.call_args_list if call.kwargs["status"] == "success"
    ][0]
    details = success_call.kwargs["details"]
    assert details["automatic_tax_enabled"] is True
    assert details["tax_id_collection_enabled"] is False


def test_stripe_checkout_with_trial_enabled(clean_db):
    token = _register_user_with_role("user@example.com", "user")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_trial"
    mock_client = MagicMock()
    mock_client.checkout.sessions.create.return_value = mock_session

    with patch("app.api.v1.routers.public.billing.settings") as mock_settings:
        mock_settings.stripe_trial_enabled = True
        mock_settings.stripe_trial_period_days = 14
        mock_settings.stripe_payment_method_collection = "if_required"
        mock_settings.stripe_trial_missing_payment_method_behavior = "pause"
        mock_settings.stripe_checkout_success_url = "http://s"
        mock_settings.stripe_checkout_cancel_url = "http://c"
        mock_settings.stripe_tax_enabled = False
        mock_settings.stripe_tax_id_collection_enabled = False
        mock_settings.stripe_checkout_billing_address_collection = "auto"

        with patch(
            "app.services.billing.stripe_checkout_service.get_stripe_client",
            return_value=mock_client,
        ):
            with patch(
                "app.services.billing.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
                {"price_123": "basic"},
            ):
                with patch("app.api.v1.routers.public.billing._record_audit_event") as mock_audit:
                    response = client.post(
                        "/v1/billing/stripe-checkout-session",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"plan": "basic"},
                    )

    assert response.status_code == 200
    call_kwargs = mock_client.checkout.sessions.create.call_args
    params = call_kwargs[1]["params"] if call_kwargs[1] else call_kwargs[0][0]

    assert params["subscription_data"]["trial_period_days"] == 14
    assert params["payment_method_collection"] == "if_required"
    assert (
        params["subscription_data"]["trial_settings"]["end_behavior"]["missing_payment_method"]
        == "pause"
    )
    assert params["success_url"] == "http://s"

    # Verify audit details
    success_call = [
        call for call in mock_audit.call_args_list if call.kwargs["status"] == "success"
    ][0]
    details = success_call.kwargs["details"]
    assert details["trial_enabled"] is True
    assert details["trial_period_days"] == 14
    assert details["payment_method_collection"] == "if_required"
    assert details["missing_payment_method_behavior"] == "pause"
