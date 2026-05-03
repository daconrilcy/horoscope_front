"""Tests du client Stripe infra et gardes anti-retour du chemin legacy."""

import ast
import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.infra.stripe import client as sc

STRIPE_API_VERSION = "2026-04-22.dahlia"
STRIPE_TIMEOUT_SECONDS = 10
STRIPE_MAX_NETWORK_RETRIES = 2


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
        mock_settings.stripe_timeout_seconds = STRIPE_TIMEOUT_SECONDS
        mock_settings.stripe_max_network_retries = STRIPE_MAX_NETWORK_RETRIES
        result = sc.get_stripe_client()
    assert result is None


def test_get_stripe_client_returns_client_when_secret_present():
    """Vérifie que le client Stripe reçoit la politique réseau configurée."""
    expected_client = object()
    with (
        patch.object(sc, "settings") as mock_settings,
        patch.object(sc.stripe, "StripeClient", return_value=expected_client) as mock_client_class,
        patch.object(sc.stripe, "RequestsClient") as mock_http_client_class,
    ):
        expected_http_client = mock_http_client_class.return_value
        mock_settings.stripe_secret_key = "sk_test_123"
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        mock_settings.stripe_timeout_seconds = STRIPE_TIMEOUT_SECONDS
        mock_settings.stripe_max_network_retries = STRIPE_MAX_NETWORK_RETRIES
        client = sc.get_stripe_client()

    assert client is expected_client
    mock_client_class.assert_called_once_with(
        api_key="sk_test_123",
        stripe_version=STRIPE_API_VERSION,
        max_network_retries=STRIPE_MAX_NETWORK_RETRIES,
        http_client=expected_http_client,
    )
    mock_http_client_class.assert_called_once_with(timeout=STRIPE_TIMEOUT_SECONDS)


def test_get_stripe_client_uses_supported_stripe_sdk_constructor():
    """Vérifie l'intégration réelle avec le constructeur Stripe installé."""
    with patch.object(sc, "settings") as mock_settings:
        mock_settings.stripe_secret_key = "sk_test_123"
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        mock_settings.stripe_timeout_seconds = STRIPE_TIMEOUT_SECONDS
        mock_settings.stripe_max_network_retries = STRIPE_MAX_NETWORK_RETRIES

        client = sc.get_stripe_client()

    assert isinstance(client, sc.stripe.StripeClient)


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
        mock_settings.stripe_timeout_seconds = STRIPE_TIMEOUT_SECONDS
        mock_settings.stripe_max_network_retries = STRIPE_MAX_NETWORK_RETRIES
        mock_settings.stripe_secret_key = "sk_test_first"
        assert sc.get_stripe_client() is first_client
        assert sc.get_stripe_client() is first_client

        mock_settings.stripe_secret_key = "sk_test_second"
        assert sc.get_stripe_client() is second_client

    assert mock_client_class.call_count == 2


def test_stripe_client_cache_is_keyed_by_network_policy():
    """Vérifie que le cache suit les changements de politique réseau Stripe."""
    first_client = object()
    second_client = object()
    with (
        patch.object(sc, "settings") as mock_settings,
        patch(
            "app.infra.stripe.client.stripe.StripeClient",
            side_effect=[first_client, second_client],
        ) as mock_client_class,
    ):
        mock_settings.stripe_secret_key = "sk_test_123"
        mock_settings.stripe_api_version = STRIPE_API_VERSION
        mock_settings.stripe_timeout_seconds = 10
        mock_settings.stripe_max_network_retries = 2
        assert sc.get_stripe_client() is first_client

        mock_settings.stripe_timeout_seconds = 20
        assert sc.get_stripe_client() is second_client

    assert mock_client_class.call_count == 2


def test_stripe_network_policy_settings_have_operator_defaults(
    monkeypatch: pytest.MonkeyPatch,
):
    """Vérifie les valeurs opérables par défaut de la politique réseau Stripe."""
    monkeypatch.delenv("STRIPE_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("STRIPE_MAX_NETWORK_RETRIES", raising=False)

    parsed_settings = Settings()

    assert parsed_settings.stripe_timeout_seconds == 10
    assert parsed_settings.stripe_max_network_retries == 2


def test_stripe_network_policy_settings_are_loaded_from_env(
    monkeypatch: pytest.MonkeyPatch,
):
    """Vérifie que les opérateurs peuvent ajuster timeout et retries Stripe."""
    monkeypatch.setenv("STRIPE_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("STRIPE_MAX_NETWORK_RETRIES", "1")

    parsed_settings = Settings()

    assert parsed_settings.stripe_timeout_seconds == 15
    assert parsed_settings.stripe_max_network_retries == 1


@pytest.mark.parametrize(
    ("env_name", "env_value", "expected_message"),
    [
        ("STRIPE_TIMEOUT_SECONDS", "0", "STRIPE_TIMEOUT_SECONDS must be greater"),
        ("STRIPE_MAX_NETWORK_RETRIES", "-1", "STRIPE_MAX_NETWORK_RETRIES must be greater"),
        ("STRIPE_TIMEOUT_SECONDS", "slow", "STRIPE_TIMEOUT_SECONDS must be an integer"),
    ],
)
def test_stripe_network_policy_settings_reject_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
    env_name: str,
    env_value: str,
    expected_message: str,
):
    """Vérifie qu'une politique réseau Stripe invalide échoue explicitement."""
    monkeypatch.setenv(env_name, env_value)

    with pytest.raises(RuntimeError, match=expected_message):
        Settings()


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


def test_stripe_network_policy_is_owned_by_config_and_infra_client():
    """Empêche des réglages timeout/retry Stripe concurrents hors allowlist."""
    repo_root = Path(__file__).resolve().parents[3]
    allowed = {
        repo_root / "app" / "core" / "config.py",
        repo_root / "app" / "infra" / "stripe" / "client.py",
    }
    forbidden_hits: list[str] = []

    for path in [
        *(repo_root / "app" / "services" / "billing").rglob("*.py"),
        *(repo_root / "app" / "api" / "v1" / "routers").rglob("*.py"),
        *(repo_root / "app" / "startup").rglob("*.py"),
        *(repo_root / "app" / "infra" / "stripe").rglob("*.py"),
        repo_root / "app" / "core" / "config.py",
    ]:
        if path in allowed:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg in {
                "timeout",
                "max_network_retries",
            }:
                forbidden_hits.append(f"{path.relative_to(repo_root)}:{node.lineno}:{node.arg}")
            if isinstance(node, ast.Attribute) and node.attr in {
                "stripe_timeout_seconds",
                "stripe_max_network_retries",
            }:
                forbidden_hits.append(f"{path.relative_to(repo_root)}:{node.lineno}:{node.attr}")

    assert forbidden_hits == []
