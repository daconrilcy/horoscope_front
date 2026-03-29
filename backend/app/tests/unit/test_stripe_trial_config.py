import pytest
from app.core.config import Settings

def test_settings_stripe_trial_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    
    monkeypatch.delenv("STRIPE_TRIAL_ENABLED", raising=False)
    monkeypatch.delenv("STRIPE_TRIAL_PERIOD_DAYS", raising=False)
    monkeypatch.delenv("STRIPE_PAYMENT_METHOD_COLLECTION", raising=False)
    monkeypatch.delenv("STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR", raising=False)

    settings = Settings()

    assert settings.stripe_trial_enabled is False
    assert settings.stripe_trial_period_days == 0
    assert settings.stripe_payment_method_collection == "always"
    assert settings.stripe_trial_missing_payment_method_behavior is None

def test_settings_stripe_trial_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    
    monkeypatch.setenv("STRIPE_TRIAL_ENABLED", "true")
    monkeypatch.setenv("STRIPE_TRIAL_PERIOD_DAYS", "14")
    monkeypatch.setenv("STRIPE_PAYMENT_METHOD_COLLECTION", "if_required")
    monkeypatch.setenv("STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR", "pause")

    settings = Settings()

    assert settings.stripe_trial_enabled is True
    assert settings.stripe_trial_period_days == 14
    assert settings.stripe_payment_method_collection == "if_required"
    assert settings.stripe_trial_missing_payment_method_behavior == "pause"

def test_settings_stripe_payment_method_collection_rejects_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    
    monkeypatch.setenv("STRIPE_PAYMENT_METHOD_COLLECTION", "invalid_value")

    with pytest.raises(ValueError, match="STRIPE_PAYMENT_METHOD_COLLECTION must be 'always' or 'if_required'"):
        Settings()

def test_settings_stripe_trial_missing_payment_method_behavior_rejects_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    
    monkeypatch.setenv("STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR", "invalid_value")

    with pytest.raises(ValueError, match="STRIPE_TRIAL_MISSING_PAYMENT_METHOD_BEHAVIOR must be 'pause' or 'cancel'"):
        Settings()
