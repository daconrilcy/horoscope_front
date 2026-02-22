"""Tests for OpenAI Client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai_engine.exceptions import (
    ProviderNotConfiguredError,
    UpstreamRateLimitError,
)
from app.ai_engine.providers.openai_client import OpenAIClient
from app.ai_engine.schemas import ChatMessage


class TestOpenAIClient:
    """Tests for OpenAIClient class."""

    def test_provider_name_returns_openai(self) -> None:
        """Provider name returns 'openai'."""
        client = OpenAIClient()
        assert client.provider_name == "openai"

    @pytest.mark.asyncio
    async def test_generate_text_raises_when_not_configured(self) -> None:
        """Generate text raises when API key not configured."""
        with patch("app.ai_engine.providers.openai_client.ai_engine_settings") as mock_settings:
            mock_settings.is_openai_configured = False
            client = OpenAIClient()
            with pytest.raises(ProviderNotConfiguredError):
                await client.generate_text("test prompt")

    @pytest.mark.asyncio
    async def test_generate_text_success(self) -> None:
        """Generate text returns result on success."""
        with patch("app.ai_engine.providers.openai_client.ai_engine_settings") as mock_settings:
            mock_settings.is_openai_configured = True
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model_default = "gpt-4o-mini"
            mock_settings.max_retries = 2
            mock_settings.retry_base_delay_ms = 100
            mock_settings.retry_max_delay_ms = 1000

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Generated text"
            mock_response.usage = MagicMock()
            mock_response.usage.prompt_tokens = 10
            mock_response.usage.completion_tokens = 20
            mock_response.model = "gpt-4o-mini"

            with patch("openai.AsyncOpenAI") as mock_openai:
                mock_client_instance = AsyncMock()
                mock_client_instance.chat.completions.create = AsyncMock(
                    return_value=mock_response
                )
                mock_openai.return_value = mock_client_instance

                client = OpenAIClient()
                result = await client.generate_text("test prompt", timeout_seconds=30)

                assert result.text == "Generated text"
                assert result.input_tokens == 10
                assert result.output_tokens == 20
                assert result.model == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_chat_success(self) -> None:
        """Chat returns result on success."""
        with patch("app.ai_engine.providers.openai_client.ai_engine_settings") as mock_settings:
            mock_settings.is_openai_configured = True
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model_default = "gpt-4o-mini"
            mock_settings.max_retries = 2
            mock_settings.retry_base_delay_ms = 100
            mock_settings.retry_max_delay_ms = 1000

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Chat response"
            mock_response.usage = MagicMock()
            mock_response.usage.prompt_tokens = 15
            mock_response.usage.completion_tokens = 25
            mock_response.model = "gpt-4o-mini"

            with patch("openai.AsyncOpenAI") as mock_openai:
                mock_client_instance = AsyncMock()
                mock_client_instance.chat.completions.create = AsyncMock(
                    return_value=mock_response
                )
                mock_openai.return_value = mock_client_instance

                client = OpenAIClient()
                messages = [
                    ChatMessage(role="user", content="Hello"),
                ]
                result = await client.chat(messages, timeout_seconds=30)

                assert result.text == "Chat response"
                assert result.input_tokens == 15
                assert result.output_tokens == 25

    @pytest.mark.asyncio
    async def test_generate_text_handles_rate_limit(self) -> None:
        """Generate text raises UpstreamRateLimitError on rate limit."""
        with patch("app.ai_engine.providers.openai_client.ai_engine_settings") as mock_settings:
            mock_settings.is_openai_configured = True
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model_default = "gpt-4o-mini"
            mock_settings.max_retries = 0
            mock_settings.retry_base_delay_ms = 100
            mock_settings.retry_max_delay_ms = 1000

            with patch("openai.AsyncOpenAI") as mock_openai:
                mock_client_instance = AsyncMock()
                mock_client_instance.chat.completions.create = AsyncMock(
                    side_effect=Exception("rate_limit exceeded 429")
                )
                mock_openai.return_value = mock_client_instance

                client = OpenAIClient()
                with pytest.raises(UpstreamRateLimitError):
                    await client.generate_text("test prompt", timeout_seconds=30)

    @pytest.mark.asyncio
    async def test_get_model_resolves_auto(self) -> None:
        """Get model resolves AUTO to default model."""
        with patch("app.ai_engine.providers.openai_client.ai_engine_settings") as mock_settings:
            mock_settings.openai_model_default = "gpt-4o-mini"

            client = OpenAIClient()
            assert client._get_model(None) == "gpt-4o-mini"
            assert client._get_model("AUTO") == "gpt-4o-mini"
            assert client._get_model("gpt-4") == "gpt-4"
