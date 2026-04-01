from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.startup.stripe_portal_validation import run_stripe_portal_startup_validation


def _mock_portal_configuration(*, enabled: bool = True, prices: list[str] | None = None):
    features = SimpleNamespace(
        subscription_update=SimpleNamespace(
            enabled=enabled,
            products=[SimpleNamespace(prices=prices or [])],
        )
    )
    return SimpleNamespace(features=features)


def test_startup_validation_fails_when_portal_configuration_missing_in_runtime(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id=None,
        stripe_portal_endpoints_enabled=True,
        app_env="development",
        stripe_portal_validation_mode="strict",
    )

    with caplog.at_level("ERROR", logger="app.startup.stripe_portal_validation"):
        with pytest.raises(
            RuntimeError,
            match="STRIPE_PORTAL_CONFIGURATION_ID is required when Stripe Customer Portal",
        ):
            run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_failed" in caplog.text


@pytest.mark.parametrize("app_env", ["test", "testing"])
def test_startup_validation_skips_missing_configuration_in_test_env(
    app_env: str, caplog: pytest.LogCaptureFixture
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id=None,
        stripe_portal_endpoints_enabled=True,
        app_env=app_env,
        stripe_portal_validation_mode="strict",
    )

    with caplog.at_level("WARNING", logger="app.startup.stripe_portal_validation"):
        run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_skipped" in caplog.text
    assert f"env={app_env}" in caplog.text


def test_startup_validation_passes_with_explicit_portal_configuration(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id="bpc_123",
        stripe_portal_endpoints_enabled=True,
        app_env="development",
        stripe_price_basic="price_basic",
        stripe_price_premium="price_premium",
        stripe_portal_validation_mode="strict",
    )

    mock_client = MagicMock()
    mock_client.billing_portal.configurations.retrieve.return_value = _mock_portal_configuration(
        prices=["price_basic", "price_premium"]
    )

    with (
        caplog.at_level("INFO", logger="app.startup.stripe_portal_validation"),
        patch("app.startup.stripe_portal_validation.get_stripe_client", return_value=mock_client),
    ):
        run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_ok" in caplog.text


def test_startup_validation_skips_when_portal_endpoints_are_disabled(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id=None,
        stripe_portal_endpoints_enabled=False,
        app_env="development",
        stripe_portal_validation_mode="strict",
    )

    with caplog.at_level("INFO", logger="app.startup.stripe_portal_validation"):
        run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_disabled" in caplog.text


def test_startup_validation_fails_when_subscription_update_prices_are_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id="bpc_123",
        stripe_portal_endpoints_enabled=True,
        app_env="development",
        stripe_price_basic="price_basic",
        stripe_price_premium="price_premium",
        stripe_portal_validation_mode="strict",
    )
    mock_client = MagicMock()
    mock_client.billing_portal.configurations.retrieve.return_value = _mock_portal_configuration(
        prices=["price_basic"]
    )

    with (
        caplog.at_level("ERROR", logger="app.startup.stripe_portal_validation"),
        patch("app.startup.stripe_portal_validation.get_stripe_client", return_value=mock_client),
    ):
        with pytest.raises(
            RuntimeError,
            match="missing subscription_update prices for configured plans: price_premium",
        ):
            run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_failed" in caplog.text


def test_startup_validation_warn_mode_does_not_block_runtime(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id="bpc_123",
        stripe_portal_endpoints_enabled=True,
        app_env="development",
        stripe_price_basic="price_basic",
        stripe_price_premium="price_premium",
        stripe_portal_validation_mode="warn",
    )
    mock_client = MagicMock()
    mock_client.billing_portal.configurations.retrieve.return_value = _mock_portal_configuration(
        prices=["price_basic"]
    )

    with (
        caplog.at_level("WARNING", logger="app.startup.stripe_portal_validation"),
        patch("app.startup.stripe_portal_validation.get_stripe_client", return_value=mock_client),
    ):
        run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_warn" in caplog.text
