"""Tests for /v1/ai/chat endpoint."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
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


class TestChatEndpointValidation:
    """Tests for Pydantic validation on POST /v1/ai/chat."""

    def test_chat_returns_422_for_invalid_provider(self, client: TestClient) -> None:
        """Chat returns 422 for invalid provider name (Pydantic Literal validation)."""
        response = client.post(
            "/v1/ai/chat",
            json={
                "locale": "fr-FR",
                "messages": [{"role": "user", "content": "Hello"}],
                "output": {"stream": False},
                "provider": {"name": "mistral", "model": "AUTO"},
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "invalid_request_payload"

    def test_chat_returns_422_for_invalid_message_role(
        self, client: TestClient
    ) -> None:
        """Chat returns 422 for invalid message role (Pydantic Literal validation)."""
        response = client.post(
            "/v1/ai/chat",
            json={
                "locale": "fr-FR",
                "messages": [{"role": "bot", "content": "Hello"}],
                "output": {"stream": False},
            },
        )
        assert response.status_code == 422


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

    def test_chat_returns_429_on_rate_limit(self, client: TestClient) -> None:
        """Chat returns 429 on upstream rate limit (AC5)."""
        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(side_effect=UpstreamRateLimitError())
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 429
        data = response.json()
        assert data["error"]["type"] == "UPSTREAM_RATE_LIMIT"
        assert "retry_after_ms" in data["error"]

    def test_chat_returns_504_on_timeout(self, client: TestClient) -> None:
        """Chat returns 504 on upstream timeout (AC5)."""
        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(side_effect=UpstreamTimeoutError(30))
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 504
        data = response.json()
        assert data["error"]["type"] == "UPSTREAM_TIMEOUT"
        assert "timeout_seconds" in data["error"]["details"]

    def test_chat_returns_500_when_provider_not_configured(
        self, client: TestClient
    ) -> None:
        """Chat returns 500 when provider is not configured (no API key)."""
        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_provider.side_effect = ProviderNotConfiguredError("openai")

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["type"] == "PROVIDER_NOT_CONFIGURED"
        assert "openai" in data["error"]["message"]

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

        usage = done_events[0].get("usage")
        assert usage is not None, "done event should include usage info"
        assert usage.get("is_estimate") is True
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert "total_tokens" in usage
        assert "estimated_cost_usd" in usage

    def test_chat_streaming_emits_error_event_on_failure(
        self, client: TestClient
    ) -> None:
        """Chat streaming emits error event when provider fails mid-stream (AC5)."""
        import json as json_module

        async def mock_failing_stream():
            yield "Starting"
            raise RuntimeError("Connection lost mid-stream")

        with patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_failing_stream())
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

        content = response.text
        lines = [line for line in content.split("\n") if line.startswith("data: ")]

        events = []
        for line in lines:
            data = json_module.loads(line[6:])
            events.append(data)

        error_events = [e for e in events if "error" in e]
        assert len(error_events) >= 1, "stream should emit error event on failure"
        assert error_events[0]["error"]["type"] == "RuntimeError"
        assert "Connection lost" in error_events[0]["error"]["message"]


class TestChatEndpointRateLimiting:
    """Tests for rate limiting on POST /v1/ai/chat."""

    def test_chat_returns_429_when_rate_limit_exceeded(
        self, client: TestClient
    ) -> None:
        """Chat returns 429 with RATE_LIMIT_EXCEEDED when limit is exceeded."""
        from app.ai_engine.services.rate_limiter import RateLimiter, RateLimitResult

        with patch.object(
            RateLimiter, "get_instance"
        ) as mock_get_instance:
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = RateLimitResult(
                allowed=False,
                current_count=30,
                limit=30,
                retry_after_ms=45000,
            )
            mock_get_instance.return_value = mock_limiter

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 429
        data = response.json()
        assert data["error"]["type"] == "RATE_LIMIT_EXCEEDED"
        assert "retry_after_ms" in data["error"]
        assert data["error"]["retry_after_ms"] == 45000
        assert "request_id" in data["error"]
        assert "trace_id" in data["error"]

    def test_chat_continues_when_rate_limit_not_exceeded(
        self, client: TestClient
    ) -> None:
        """Chat proceeds normally when rate limit is not exceeded."""
        from app.ai_engine.providers.base import ProviderResult
        from app.ai_engine.services.rate_limiter import RateLimiter, RateLimitResult

        mock_result = ProviderResult(
            text="Response",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o-mini",
        )

        with patch.object(
            RateLimiter, "get_instance"
        ) as mock_get_instance, patch(
            "app.ai_engine.services.chat_service.get_provider_client"
        ) as mock_provider:
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = RateLimitResult(
                allowed=True,
                current_count=5,
                limit=30,
            )
            mock_get_instance.return_value = mock_limiter

            mock_client = AsyncMock()
            mock_client.chat = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/chat",
                json={
                    "locale": "fr-FR",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "output": {"stream": False},
                },
            )

        assert response.status_code == 200
        mock_limiter.check_rate_limit.assert_called_once_with(1)
