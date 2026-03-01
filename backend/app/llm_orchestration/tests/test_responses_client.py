from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai_engine.exceptions import UpstreamRateLimitError
from app.llm_orchestration.providers.responses_client import ResponsesClient


@pytest.fixture(autouse=True)
def mock_settings():
    with patch("app.ai_engine.config.ai_engine_settings.openai_api_key", "sk-test"):
        yield


@pytest.mark.asyncio
async def test_responses_client_execute_success():
    # Arrange
    mock_response = MagicMock()
    mock_response.model = "gpt-4o-mini"

    # Mock output items
    mock_item = MagicMock()
    mock_item.type = "message"
    mock_part = MagicMock()
    mock_part.type = "text"
    mock_part.text = "Hello from Responses API"
    mock_item.content = [mock_part]
    mock_response.output = [mock_item]

    mock_response.usage.input_tokens = 5
    mock_response.usage.output_tokens = 10
    mock_response.usage.total_tokens = 15

    with patch("openai.AsyncOpenAI") as mock_openai_class:
        mock_client_instance = mock_openai_class.return_value
        mock_client_instance.responses.create = AsyncMock(return_value=mock_response)

        client = ResponsesClient()

        # Act
        result = await client.execute(
            messages=[{"role": "user", "content": "hi"}],
            model="gpt-4o-mini",
            request_id="req-1",
            trace_id="trace-1",
            use_case="test",
        )

        # Assert
        assert result.raw_output == "Hello from Responses API"
        assert result.usage.total_tokens == 15
        assert result.meta.model == "gpt-4o-mini"
        mock_client_instance.responses.create.assert_called_once()


@pytest.mark.asyncio
async def test_responses_client_raises_rate_limit_immediately():
    # Arrange
    with patch("openai.AsyncOpenAI") as mock_openai_class:
        mock_client_instance = mock_openai_class.return_value
        # Fail with rate limit
        mock_client_instance.responses.create = AsyncMock(side_effect=Exception("Rate limit 429"))

        client = ResponsesClient()
        with pytest.raises(UpstreamRateLimitError):
            await client.execute(messages=[], model="m")

        assert mock_client_instance.responses.create.call_count == 1
