"""Tests for /v1/ai/chat endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ai_engine.exceptions import UpstreamError
from app.ai_engine.providers.base import ProviderResult
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestChatEndpoint:
    """Tests for POST /v1/ai/chat endpoint."""

    def test_chat_returns_success_with_valid_request(
        self, client: TestClient
    ) -> None:
        """Chat returns 200 with valid request."""
        mock_result = ProviderResult(
            text="Bonjour ! Je vois dans votre thème natal...",
            input_tokens=150,
            output_tokens=75,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [
                        {"role": "user", "content": "Bonjour, peux-tu lire mon thème ?"}
                    ],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "thème natal" in data["text"]
        assert data["provider"] == "openai"
        assert data["usage"]["input_tokens"] == 150
        assert data["usage"]["output_tokens"] == 75

    def test_chat_adds_system_prompt_when_missing(
        self, client: TestClient
    ) -> None:
        """Chat adds system prompt when not provided."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=100,
            output_tokens=50,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 200
        call_args = mock_client.chat.call_args
        messages = call_args[0][0]
        assert messages[0].role == "system"
        assert "bienveillant" in messages[0].content.lower()

    def test_chat_preserves_existing_system_prompt(
        self, client: TestClient
    ) -> None:
        """Chat preserves existing system prompt."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=100,
            output_tokens=50,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [
                        {"role": "system", "content": "Custom system prompt"},
                        {"role": "user", "content": "Hello"},
                    ],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 200
        call_args = mock_client.chat.call_args
        messages = call_args[0][0]
        assert len([m for m in messages if m.role == "system"]) == 1
        assert messages[0].content == "Custom system prompt"

    def test_chat_returns_error_on_upstream_failure(
        self, client: TestClient
    ) -> None:
        """Chat returns 502 on upstream error."""
        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(
                side_effect=UpstreamError("Provider unavailable")
            )
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 502
        data = response.json()
        assert data["error"]["type"] == "UPSTREAM_ERROR"

    def test_chat_includes_context_in_system_prompt(
        self, client: TestClient
    ) -> None:
        """Chat includes natal chart context in system prompt."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=100,
            output_tokens=50,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "context": {
                        "natal_chart_summary": "Soleil en Bélier, Lune en Cancer"
                    },
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 200
        call_args = mock_client.chat.call_args
        messages = call_args[0][0]
        system_content = messages[0].content
        assert "Soleil en Bélier" in system_content
