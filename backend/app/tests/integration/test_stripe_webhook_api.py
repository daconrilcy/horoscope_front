from __future__ import annotations

import hashlib
import hmac
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def _sign_payload(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.".encode() + payload
    signature = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    payload = b'{"id": "evt_123", "type": "checkout.session.completed"}'
    headers = {"stripe-signature": "invalid"}
    
    with patch("app.core.config.settings.stripe_webhook_secret", "whsec_test"):
        response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)
        
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_signature"


@pytest.mark.asyncio
async def test_webhook_no_secret_configured():
    payload = b'{"id": "evt_123"}'
    headers = {"stripe-signature": "any"}
    
    with patch("app.core.config.settings.stripe_webhook_secret", None):
        response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)
        
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "webhook_secret_not_configured"


@pytest.mark.asyncio
async def test_webhook_success_flow():
    payload = b'{"id": "evt_123", "type": "checkout.session.completed", "data": {"object": {"client_reference_id": "42"}}}'
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}
    
    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        # On mock le service pour éviter de toucher à la DB réelle dans ce test d'intégration
        # On veut surtout tester le routing et la validation de signature ici.
        with patch("app.services.stripe_webhook_service.StripeWebhookService.handle_event") as mock_handle:
            mock_handle.return_value = "processed"
            
            response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)
            
            assert response.status_code == 200
            assert response.json() == {"status": "processed"}
            mock_handle.assert_called_once()


@pytest.mark.asyncio
async def test_webhook_app_error_returns_200():
    """AC3: Erreur applicative interne après signature valide -> 200"""
    payload = b'{"id": "evt_123", "type": "checkout.session.completed"}'
    secret = "whsec_test"
    headers = {"stripe-signature": _sign_payload(payload, secret)}
    
    with patch("app.core.config.settings.stripe_webhook_secret", secret):
        with patch("app.services.stripe_webhook_service.StripeWebhookService.handle_event") as mock_handle:
            mock_handle.side_effect = Exception("Internal error")
            
            response = client.post("/v1/billing/stripe-webhook", content=payload, headers=headers)
            
            assert response.status_code == 200
            assert response.json() == {"status": "failed_internal"}
