"""Tests for /v1/ai/generate endpoint."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.ai_engine.exceptions import UpstreamTimeoutError
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


class TestGenerateEndpointAuth:
    """Tests for authentication on POST /v1/ai/generate."""

    def test_generate_returns_401_without_auth_token(self) -> None:
        """Generate returns 401 when no auth token provided."""
        unauthenticated_client = TestClient(app)
        response = unauthenticated_client.post(
            "/v1/ai/generate",
            json={"use_case": "chat", "locale": "fr-FR"},
        )
        assert response.status_code == 401


class TestGenerateEndpointValidation:
    """Tests for Pydantic validation on POST /v1/ai/generate."""

    def test_generate_returns_422_for_invalid_provider(
        self, client: TestClient
    ) -> None:
        """Generate returns 422 for invalid provider name (Pydantic Literal validation)."""
        response = client.post(
            "/v1/ai/generate",
            json={
                "use_case": "chat",
                "locale": "fr-FR",
                "provider": {"name": "anthropic", "model": "AUTO"},
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "invalid_request_payload"


class TestGenerateEndpoint:
    """Tests for POST /v1/ai/generate endpoint."""

    def test_generate_returns_validation_error_for_unknown_use_case(
        self, client: TestClient
    ) -> None:
        """Generate returns 400 for unknown use_case."""
        response = client.post(
            "/v1/ai/generate",
            json={
                "use_case": "unknown_case",
                "locale": "fr-FR",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["type"] == "VALIDATION_ERROR"
        assert "unknown_case" in data["error"]["message"]

    def test_generate_returns_success_with_valid_request(
        self, client: TestClient
    ) -> None:
        """Generate returns 200 with valid request."""
        mock_result = ProviderResult(
            text="Generated astrological insight",
            input_tokens=100,
            output_tokens=50,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={
                    "use_case": "natal_chart_interpretation",
                    "locale": "fr-FR",
                    "input": {
                        "question": "Que dit mon thème sur ma carrière ?",
                        "tone": "warm",
                    },
                    "context": {
                        "natal_chart_summary": "Soleil en Bélier",
                    },
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Generated astrological insight"
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4o-mini"
        assert "request_id" in data
        assert "trace_id" in data
        assert data["usage"]["input_tokens"] == 100
        assert data["usage"]["output_tokens"] == 50
        assert data["usage"]["total_tokens"] == 150

    def test_generate_includes_trace_id_from_header(
        self, client: TestClient
    ) -> None:
        """Generate uses trace_id from header when provided."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={"use_case": "chat", "locale": "fr-FR"},
                headers={"X-Trace-Id": "custom-trace-123"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == "custom-trace-123"

    def test_generate_includes_trace_id_from_body(
        self, client: TestClient
    ) -> None:
        """Generate uses trace_id from body when provided."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={
                    "use_case": "chat",
                    "locale": "fr-FR",
                    "trace_id": "body-trace-456",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["trace_id"] == "body-trace-456"

    def test_generate_returns_timeout_error(self, client: TestClient) -> None:
        """Generate returns 504 on upstream timeout."""
        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(
                side_effect=UpstreamTimeoutError(30)
            )
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={"use_case": "chat", "locale": "fr-FR"},
            )

        assert response.status_code == 504
        data = response.json()
        assert data["error"]["type"] == "UPSTREAM_TIMEOUT"

    def test_generate_calculates_estimated_cost(self, client: TestClient) -> None:
        """Generate calculates estimated cost in USD."""
        mock_result = ProviderResult(
            text="Response",
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={"use_case": "chat", "locale": "fr-FR"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["usage"]["estimated_cost_usd"] > 0

    def test_generate_returns_error_for_excessively_large_context(
        self, client: TestClient
    ) -> None:
        """Generate returns 400 when context exceeds hard limit (AC6)."""
        large_context = "x" * 100000

        response = client.post(
            "/v1/ai/generate",
            json={
                "use_case": "natal_chart_interpretation",
                "locale": "fr-FR",
                "context": {"natal_chart_summary": large_context},
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["type"] == "VALIDATION_ERROR"
        assert "context exceeds maximum tokens" in data["error"]["message"]
        assert "token_count" in data["error"]["details"]
        assert "max_tokens" in data["error"]["details"]

    def test_generate_truncates_moderately_large_context(
        self, client: TestClient
    ) -> None:
        """Generate truncates context that exceeds soft limit but not hard limit."""
        moderate_context = "a" * 20000
        mock_result = ProviderResult(
            text="Generated response",
            input_tokens=500,
            output_tokens=100,
            model="gpt-4o-mini",
        )

        with patch(
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={
                    "use_case": "natal_chart_interpretation",
                    "locale": "fr-FR",
                    "context": {"natal_chart_summary": moderate_context},
                },
            )

        assert response.status_code == 200
        call_args = mock_client.generate_text.call_args
        rendered_prompt = call_args[0][0]
        assert "[...contexte tronqué" in rendered_prompt or len(rendered_prompt) < len(
            moderate_context
        )


class TestGenerateEndpointRateLimiting:
    """Tests for rate limiting on POST /v1/ai/generate."""

    def test_generate_returns_429_when_rate_limit_exceeded(
        self, client: TestClient
    ) -> None:
        """Generate returns 429 with RATE_LIMIT_EXCEEDED when limit is exceeded."""
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
                "/v1/ai/generate",
                json={"use_case": "chat", "locale": "fr-FR"},
            )

        assert response.status_code == 429
        data = response.json()
        assert data["error"]["type"] == "RATE_LIMIT_EXCEEDED"
        assert "retry_after_ms" in data["error"]
        assert data["error"]["retry_after_ms"] == 45000
        assert "request_id" in data["error"]
        assert "trace_id" in data["error"]

    def test_generate_continues_when_rate_limit_not_exceeded(
        self, client: TestClient
    ) -> None:
        """Generate proceeds normally when rate limit is not exceeded."""
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
            "app.ai_engine.services.generate_service.get_provider_client"
        ) as mock_provider:
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = RateLimitResult(
                allowed=True,
                current_count=5,
                limit=30,
            )
            mock_get_instance.return_value = mock_limiter

            mock_client = AsyncMock()
            mock_client.generate_text = AsyncMock(return_value=mock_result)
            mock_client.provider_name = "openai"
            mock_provider.return_value = mock_client

            response = client.post(
                "/v1/ai/generate",
                json={"use_case": "chat", "locale": "fr-FR"},
            )

        assert response.status_code == 200
        mock_limiter.check_rate_limit.assert_called_once_with(1)
