from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.services.stripe_checkout_service import StripeCheckoutService, StripeCheckoutServiceError


@pytest.fixture
def db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_stripe_client():
    with patch("app.services.stripe_checkout_service.get_stripe_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_profile_service():
    with patch("app.services.stripe_checkout_service.StripeBillingProfileService") as mock:
        yield mock


@pytest.fixture
def mock_price_map():
    with patch(
        "app.services.stripe_checkout_service.STRIPE_PRICE_ENTITLEMENT_MAP",
        {"price_basic_123": "basic", "price_premium_456": "premium"},
    ):
        yield


def test_create_checkout_session_nominal_existing_customer(
    db, mock_stripe_client, mock_profile_service, mock_price_map
):
    # Setup
    user_id = 1
    user_email = "test@example.com"
    plan = "basic"
    success_url = "http://success"
    cancel_url = "http://cancel"

    profile = StripeBillingProfileModel(user_id=user_id, stripe_customer_id="cus_123")
    mock_profile_service.get_or_create_profile.return_value = profile

    mock_session = MagicMock()
    mock_session.url = "http://stripe.checkout/session_123"
    mock_stripe_client.checkout.sessions.create.return_value = mock_session

    # Execute
    url = StripeCheckoutService.create_checkout_session(
        db,
        user_id=user_id,
        user_email=user_email,
        plan=plan,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    # Verify
    assert url == "http://stripe.checkout/session_123"
    args, kwargs = mock_stripe_client.checkout.sessions.create.call_args
    params = kwargs["params"]
    assert params["customer"] == "cus_123"
    assert "customer_email" not in params
    assert params["line_items"][0]["price"] == "price_basic_123"
    assert params["client_reference_id"] == "1"
    assert params["metadata"]["app_user_id"] == "1"
    assert params["subscription_data"]["metadata"]["plan"] == "basic"


def test_create_checkout_session_nominal_new_customer(
    db, mock_stripe_client, mock_profile_service, mock_price_map
):
    # Setup
    user_id = 1
    user_email = "test@example.com"
    plan = "premium"

    profile = StripeBillingProfileModel(user_id=user_id, stripe_customer_id=None)
    mock_profile_service.get_or_create_profile.return_value = profile

    mock_session = MagicMock()
    mock_session.url = "http://stripe.checkout/session_456"
    mock_stripe_client.checkout.sessions.create.return_value = mock_session

    # Execute
    url = StripeCheckoutService.create_checkout_session(
        db,
        user_id=user_id,
        user_email=user_email,
        plan=plan,
        success_url="http://s",
        cancel_url="http://c",
    )

    # Verify
    assert url == "http://stripe.checkout/session_456"
    args, kwargs = mock_stripe_client.checkout.sessions.create.call_args
    params = kwargs["params"]
    assert params["customer_email"] == "test@example.com"
    assert "customer" not in params
    assert params["line_items"][0]["price"] == "price_premium_456"


def test_create_checkout_session_invalid_plan(db, mock_stripe_client, mock_price_map):
    with pytest.raises(StripeCheckoutServiceError) as excinfo:
        StripeCheckoutService.create_checkout_session(
            db, user_id=1, user_email="t@e.c", plan="gold", success_url="h", cancel_url="c"
        )
    assert excinfo.value.code == "plan_price_not_configured"


def test_create_checkout_session_stripe_unavailable(db, mock_price_map):
    with patch("app.services.stripe_checkout_service.get_stripe_client", return_value=None):
        with pytest.raises(StripeCheckoutServiceError) as excinfo:
            StripeCheckoutService.create_checkout_session(
                db, user_id=1, user_email="t@e.c", plan="basic", success_url="h", cancel_url="c"
            )
        assert excinfo.value.code == "stripe_unavailable"


def test_create_checkout_session_no_email_no_customer(
    db, mock_stripe_client, mock_profile_service, mock_price_map
):
    profile = StripeBillingProfileModel(user_id=1, stripe_customer_id=None)
    mock_profile_service.get_or_create_profile.return_value = profile

    with pytest.raises(StripeCheckoutServiceError) as excinfo:
        StripeCheckoutService.create_checkout_session(
            db, user_id=1, user_email=None, plan="basic", success_url="h", cancel_url="c"
        )
    assert excinfo.value.code == "invalid_checkout_request"


def test_create_checkout_session_stripe_error(
    db, mock_stripe_client, mock_profile_service, mock_price_map
):
    import stripe

    mock_profile_service.get_or_create_profile.return_value = StripeBillingProfileModel(
        user_id=1, stripe_customer_id="cus_1"
    )
    mock_stripe_client.checkout.sessions.create.side_effect = stripe.StripeError("Stripe fail")

    with pytest.raises(StripeCheckoutServiceError) as excinfo:
        StripeCheckoutService.create_checkout_session(
            db, user_id=1, user_email="t@e.c", plan="basic", success_url="h", cancel_url="c"
        )
    assert excinfo.value.code == "stripe_api_error"
