# Commentaire global: couvre la configuration locale de la facade Astral.
"""Tests de configuration de la facade Astral."""

from __future__ import annotations

from app.core.config import Settings


def _set_required_settings_env(monkeypatch) -> None:
    """Prepare les variables minimales requises par Settings en test."""
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./horoscope.db")
    monkeypatch.setenv("REFERENCE_SEED_ADMIN_TOKEN", "seed-token")
    monkeypatch.setenv("API_CREDENTIALS_SECRET_KEY", "api-current")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-current")
    monkeypatch.setenv("LLM_ANONYMIZATION_SALT", "llm-salt")


def test_astral_api_key_uses_canonical_env_first(monkeypatch) -> None:
    """Priorise la variable canonique ASTRAL_API_KEY quand elle est renseignee."""
    _set_required_settings_env(monkeypatch)
    monkeypatch.setenv("ASTRAL_API_KEY", "canonical-key")
    monkeypatch.setenv("ASTRAL_LLM_API_KEY", "legacy-key")

    settings = Settings()

    assert settings.astral_api_key == "canonical-key"


def test_astral_api_key_falls_back_to_llm_env_alias(monkeypatch) -> None:
    """Accepte l'alias local ASTRAL_LLM_API_KEY quand la cle canonique manque."""
    _set_required_settings_env(monkeypatch)
    monkeypatch.delenv("ASTRAL_API_KEY", raising=False)
    monkeypatch.setenv("ASTRAL_LLM_API_KEY", "legacy-key")

    settings = Settings()

    assert settings.astral_api_key == "legacy-key"


def test_astral_mercure_auth_token_uses_dedicated_env(monkeypatch) -> None:
    """Expose le jeton Mercure dedie sans le confondre avec la cle jobs Astral."""
    _set_required_settings_env(monkeypatch)
    monkeypatch.setenv("ASTRAL_API_KEY", "jobs-key")
    monkeypatch.setenv("ASTRAL_MERCURE_AUTH_TOKEN", "mercure-token")

    settings = Settings()

    assert settings.astral_api_key == "jobs-key"
    assert settings.astral_mercure_auth_token == "mercure-token"
