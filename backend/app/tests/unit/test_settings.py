import pytest

from app.core.config import Settings


def test_settings_requires_seed_token_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)

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
    monkeypatch.delenv("REFERENCE_SEED_ADMIN_TOKEN", raising=False)

    first = Settings().reference_seed_admin_token
    second = Settings().reference_seed_admin_token

    assert first == second
    assert first.startswith("dev-seed-")
