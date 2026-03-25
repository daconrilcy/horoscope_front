from unittest.mock import patch

from app.integrations import stripe_client as sc


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
