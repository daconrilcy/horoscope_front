import pytest

from app.core.config import Settings


def test_settings_requires_seed_token_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError):
        Settings()


def test_settings_requires_seed_token_in_staging(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("LLM_ANONYMIZATION_SALT", raising=False)

    with pytest.raises(RuntimeError):
        Settings()


def test_settings_requires_api_credentials_secret_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-prod-token")
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError):
        Settings()


def test_settings_allows_default_seed_token_in_non_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", "1")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("LLM_ANONYMIZATION_SALT", raising=False)

    settings = Settings()
    assert settings.reference_seed_admin_token.startswith("dev-seed-")
    assert len(settings.api_credentials_secret_key) >= 32
    assert len(settings.jwt_secret_key) >= 32
    assert len(settings.llm_anonymization_salt) >= 32


def test_settings_parses_previous_rotation_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("JWT_PREVIOUS_SECRET_KEYS", "jwt-prev-1, jwt-prev-2")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("API_CREDENTIALS_PREVIOUS_SECRET_KEYS", "api-prev-1,api-prev-2")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")

    settings = Settings()
    assert settings.jwt_previous_secret_keys == ["jwt-prev-1", "jwt-prev-2"]
    assert settings.api_credentials_previous_secret_keys == ["api-prev-1", "api-prev-2"]
    assert settings.jwt_verification_secret_keys == ["jwt-current", "jwt-prev-1", "jwt-prev-2"]


def test_non_production_seed_token_is_stable_without_env_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./stable-dev.db")
    monkeypatch.setenv("ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", "1")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)

    first = Settings().reference_seed_admin_token
    second = Settings().reference_seed_admin_token

    assert first == second
    assert first.startswith("dev-seed-")


def test_settings_requires_seed_token_when_non_local_database_in_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db:5432/horoscope")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("LLM_ANONYMIZATION_SALT", raising=False)

    with pytest.raises(RuntimeError):
        Settings()


def test_settings_disables_seed_token_fallback_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.delenv("ENABLE_REFERENCE_SEED_ADMIN_FALLBACK", raising=False)
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("LLM_ANONYMIZATION_SALT", raising=False)

    settings = Settings()
    assert settings.enable_reference_seed_admin_fallback is False
    assert settings.reference_seed_admin_token
    assert not settings.reference_seed_admin_token.startswith("dev-seed-")


def test_settings_pricing_experiment_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    monkeypatch.delenv("PRICING_EXPERIMENT_ENABLED", raising=False)
    monkeypatch.delenv("PRICING_EXPERIMENT_MIN_SAMPLE_SIZE", raising=False)

    settings = Settings()

    assert settings.pricing_experiment_enabled is True
    assert settings.pricing_experiment_min_sample_size == 50


def test_settings_pricing_experiment_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    monkeypatch.setenv("PRICING_EXPERIMENT_ENABLED", "false")
    monkeypatch.setenv("PRICING_EXPERIMENT_MIN_SAMPLE_SIZE", "120")

    settings = Settings()

    assert settings.pricing_experiment_enabled is False
    assert settings.pricing_experiment_min_sample_size == 120


def test_settings_pricing_experiment_min_sample_size_is_hardened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    monkeypatch.setenv("PRICING_EXPERIMENT_MIN_SAMPLE_SIZE", "not-an-int")
    assert Settings().pricing_experiment_min_sample_size == 50

    monkeypatch.setenv("PRICING_EXPERIMENT_MIN_SAMPLE_SIZE", "0")
    assert Settings().pricing_experiment_min_sample_size == 1


def test_settings_natal_engine_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")
    monkeypatch.setenv("NATAL_ENGINE_DEFAULT", "swisseph")
    monkeypatch.setenv("NATAL_ENGINE_SIMPLIFIED_ENABLED", "true")
    monkeypatch.setenv("NATAL_ENGINE_COMPARE_ENABLED", "1")

    settings = Settings()

    assert settings.natal_engine_default == "swisseph"
    assert settings.natal_engine_simplified_enabled is True
    assert settings.natal_engine_compare_enabled is True
