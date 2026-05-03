"""Tests du client Stripe infra et garde anti-retour du chemin legacy."""

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

from app.infra.stripe import client as sc

STRIPE_API_VERSION = "2026-04-22.dahlia"


@pytest.fixture(autouse=True)
def clear_stripe_client_cache():
    """Isole le cache du client Stripe entre les tests unitaires."""
    sc._client_cache.clear()
    yield
    sc._client_cache.clear()


def test_get_stripe_client_returns_none_when_secret_missing():
    """Vérifie que get_stripe_client retourne None si la clé secrète est absente."""
    with patch.object(sc, "settings") as mock_settings:
        mock_settings.stripe_secret_key = None
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        result = sc.get_stripe_client()
    assert result is None


def test_get_stripe_client_returns_client_when_secret_present():
    """Vérifie que le client Stripe reçoit la version API configurée."""
    expected_client = object()
    with (
        patch.object(sc, "settings") as mock_settings,
        patch.object(sc.stripe, "StripeClient", return_value=expected_client) as mock_client_class,
    ):
        mock_settings.stripe_secret_key = "sk_test_123"
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        client = sc.get_stripe_client()

    assert client is expected_client
    mock_client_class.assert_called_once_with(
        api_key="sk_test_123",
        stripe_version=STRIPE_API_VERSION,
    )


def test_stripe_client_cache_is_keyed_by_secret_key():
    """Vérifie que le cache ne masque pas une rotation de clé Stripe."""
    first_client = object()
    second_client = object()
    with (
        patch.object(sc, "settings") as mock_settings,
        patch.object(
            sc.stripe,
            "StripeClient",
            side_effect=[first_client, second_client],
        ) as mock_client_class,
    ):
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        mock_settings.stripe_secret_key = "sk_test_first"
        assert sc.get_stripe_client() is first_client
        assert sc.get_stripe_client() is first_client

        mock_settings.stripe_secret_key = "sk_test_second"
        assert sc.get_stripe_client() is second_client

    assert mock_client_class.call_count == 2


def test_legacy_integrations_stripe_client_module_is_absent():
    """Empêche le retour d'une façade legacy hors de la couche infra."""
    legacy_module = ".".join(["app", "integrations", "stripe_client"])
    with pytest.raises(ModuleNotFoundError):
        importlib.util.find_spec(legacy_module)


def test_infra_stripe_client_is_the_only_stripe_client_constructor():
    """Empêche un second propriétaire runtime du client SDK Stripe."""
    repo_root = Path(__file__).resolve().parents[3]
    current_test = Path(__file__).resolve()
    matches = [
        path
        for path in (repo_root / "app").rglob("*.py")
        if path.resolve() != current_test
        and "stripe.StripeClient(" in path.read_text(encoding="utf-8")
    ]

    assert matches == [repo_root / "app" / "infra" / "stripe" / "client.py"]
