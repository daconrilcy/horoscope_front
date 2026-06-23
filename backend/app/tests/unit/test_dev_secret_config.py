# Commentaire global: couvre les secrets implicites stables reserves au dev local.
"""Tests de configuration des secrets locaux de developpement."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def _set_minimal_env_without_runtime_secrets(monkeypatch) -> None:
    """Prepare une configuration minimale sans secrets runtime explicites."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("API_CREDENTIALS_SECRET_KEY", raising=False)


def test_development_implicit_jwt_secret_is_stable(monkeypatch) -> None:
    """Evite d'invalider les sessions locales a chaque redemarrage backend."""
    _set_minimal_env_without_runtime_secrets(monkeypatch)

    first = Settings()
    second = Settings()

    assert first.jwt_secret_key == second.jwt_secret_key
    assert first.jwt_secret_key.startswith("dev-jwt_secret_key-")


def test_development_implicit_api_credentials_secret_is_stable(monkeypatch) -> None:
    """Stabilise aussi les secrets API locaux derives hors production."""
    _set_minimal_env_without_runtime_secrets(monkeypatch)

    first = Settings()
    second = Settings()

    assert first.api_credentials_secret_key == second.api_credentials_secret_key
    assert first.api_credentials_secret_key.startswith("dev-api_credentials_secret_key-")


def test_production_still_requires_explicit_jwt_secret(monkeypatch) -> None:
    """Ne permet pas de secret JWT implicite en production."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        Settings()
