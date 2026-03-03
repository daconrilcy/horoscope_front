from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import RateLimitError

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
    # raw_output in GatewayResult expects a string.
    # ResponsesClient uses response.output_text if it has it.
    mock_response.output_text = "Hello from Responses API"

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

        # Create a proper RateLimitError
        # Parameters: message, response (HTTPResponse), body
        err = RateLimitError(
            message="Rate limit reached",
            response=MagicMock(),
            body={"error": {"message": "Rate limit reached", "code": "rate_limit_exceeded"}},
        )

        # Fail with rate limit
        mock_client_instance.responses.create = AsyncMock(side_effect=err)

        client = ResponsesClient()
        with pytest.raises(UpstreamRateLimitError):
            await client.execute(messages=[{"role": "user", "content": "hi"}], model="m")

        # RateLimitError is non-retryable in our implementation (direct raise)
        assert mock_client_instance.responses.create.call_count == 1
