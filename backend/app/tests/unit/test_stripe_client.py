"""Tests du client Stripe infra et garde anti-retour du chemin legacy."""

import importlib.util
from unittest.mock import patch

import pytest

from app.infra.stripe import client as sc


def test_get_stripe_client_returns_none_when_secret_missing():
    """Vérifie que get_stripe_client retourne None si la clé secrète est absente."""
    with patch.object(sc, "settings") as mock_settings:
        mock_settings.stripe_secret_key = None
        mock_settings.stripe_api_version = "2024-12-18.acacia"
        result = sc.get_stripe_client()
    assert result is None


def test_get_stripe_client_returns_client_when_secret_present():
    """Vérifie que get_stripe_client retourne un client si la clé est présente."""
    with patch.object(sc, "settings") as mock_settings:
        mock_settings.stripe_secret_key = "sk_test_123"
        mock_settings.stripe_api_version = "2024-12-18.acacia"
        client = sc.get_stripe_client()
    assert client is not None


def test_legacy_integrations_stripe_client_module_is_absent():
    """Empêche le retour d'une façade legacy hors de la couche infra."""
    legacy_module = ".".join(["app", "integrations", "stripe_client"])
    with pytest.raises(ModuleNotFoundError):
        importlib.util.find_spec(legacy_module)
