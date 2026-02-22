"""Tests for /v1/ai/chat endpoint."""

from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ai_engine.exceptions import UpstreamError
from app.ai_engine.providers.base import ProviderResult
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.main import app


def _mock_authenticated_user() -> AuthenticatedUser:
    """Return a mock authenticated user for tests."""
    return AuthenticatedUser(id=1, role="user")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client with mocked authentication."""
    app.dependency_overrides[require_authenticated_user] = _mock_authenticated_user
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestChatEndpointAuth:
    """Tests for authentication on POST /v1/ai/chat."""

    def test_chat_returns_401_without_auth_token(self) -> None:
        """Chat returns 401 when no auth token provided."""
        unauthenticated_client = TestClient(app)
        response = unauthenticated_client.post(
            "/v1/ai/chat",
            json={
                "locale": "fr-FR",
                "messages": [{"role": "user", "content": "Hello"}],
                "output": {"stream": False},
            },
        )
        assert response.status_code == 401


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


class TestChatStreamingEndpoint:
    """Tests for POST /v1/ai/chat endpoint with streaming."""

    def test_chat_streaming_returns_sse_events(self, client: TestClient) -> None:
        """Chat streaming returns SSE-formatted response."""

        async def mock_stream_generator():
            yield "Hello"
            yield " world"
            yield "!"

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_stream_generator())
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": True},
                },
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "X-Request-Id" in response.headers
        assert "X-Trace-Id" in response.headers

    def test_chat_streaming_includes_cache_control_headers(
        self, client: TestClient
    ) -> None:
        """Chat streaming response has proper cache headers."""

        async def mock_stream_generator():
            yield "chunk"

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_stream_generator())
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": True},
                },
            )

        assert response.status_code == 200
        assert response.headers.get("cache-control") == "no-cache"
        assert response.headers.get("connection") == "keep-alive"

    def test_chat_streaming_emits_delta_and_done_events(
        self, client: TestClient
    ) -> None:
        """Chat streaming emits delta events and done event."""
        import json as json_module

        async def mock_stream_generator():
            yield "Part1"
            yield "Part2"

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_stream_generator())
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Test"}],
                    "output": {"stream": True},
                },
            )

        assert response.status_code == 200
        content = response.text
        lines = [line for line in content.split("\n") if line.startswith("data: ")]

        events = []
        for line in lines:
            data = json_module.loads(line[6:])
            events.append(data)

        assert len(events) >= 2
        delta_events = [e for e in events if "delta" in e]
        done_events = [e for e in events if e.get("done") is True]
        assert len(delta_events) >= 1
        assert len(done_events) == 1
        assert "Part1" in done_events[0]["text"] and "Part2" in done_events[0]["text"]
