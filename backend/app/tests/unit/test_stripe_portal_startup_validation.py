from types import SimpleNamespace

import pytest

from app.startup.stripe_portal_validation import run_stripe_portal_startup_validation


def test_startup_validation_fails_when_portal_configuration_missing_in_runtime(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = SimpleNamespace(
        stripe_secret_key="sk_test_123",
        stripe_portal_configuration_id=None,
        stripe_portal_endpoints_enabled=True,
        app_env="development",
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
    )

    with caplog.at_level("INFO", logger="app.startup.stripe_portal_validation"):
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
    )

    with caplog.at_level("INFO", logger="app.startup.stripe_portal_validation"):
        run_stripe_portal_startup_validation(settings)

    assert "stripe_portal_startup_validation_disabled" in caplog.text
