from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import RateLimitError

from app.infra.providers.llm.openai_responses_client import ResponsesClient


@pytest.fixture(autouse=True)
def mock_settings():
    with patch(
        "app.infra.providers.llm.openai_responses_client.ai_engine_settings.openai_api_key",
        "sk-test",
    ):
        yield


@pytest.mark.asyncio
async def test_responses_client_execute_success():
    # Arrange
    mock_response = MagicMock()
    mock_response.model = "gpt-4o-mini"
    mock_response.output_text = "Hello from Responses API"
    mock_response.usage.input_tokens = 5
    mock_response.usage.output_tokens = 10
    mock_response.usage.total_tokens = 15

    mock_raw_response = MagicMock()
    mock_raw_response.parse.return_value = mock_response
    mock_raw_response.headers = {"x-request-id": "req-1"}

    with patch(
        "app.infra.providers.llm.openai_responses_client.AsyncOpenAI"
    ) as mock_openai_class:
        mock_client_instance = mock_openai_class.return_value
        # Mock with_raw_response chain
        mock_with_raw = MagicMock()
        mock_client_instance.with_raw_response = mock_with_raw
        mock_with_raw.responses = MagicMock()
        mock_with_raw.responses.create = AsyncMock(return_value=mock_raw_response)

        client = ResponsesClient()

        # Act
        result, headers = await client.execute(
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
        assert headers["x-request-id"] == "req-1"
        mock_with_raw.responses.create.assert_called_once()


@pytest.mark.asyncio
async def test_responses_client_passes_through_rate_limit():
    # Arrange
    with patch(
        "app.infra.providers.llm.openai_responses_client.AsyncOpenAI"
    ) as mock_openai_class:
        mock_client_instance = mock_openai_class.return_value
        mock_with_raw = MagicMock()
        mock_client_instance.with_raw_response = mock_with_raw
        mock_with_raw.responses = MagicMock()

        err = RateLimitError(
            message="Rate limit reached",
            response=MagicMock(),
            body={"error": {"message": "Rate limit reached", "code": "rate_limit_exceeded"}},
        )

        mock_with_raw.responses.create = AsyncMock(side_effect=err)

        client = ResponsesClient()
        with pytest.raises(RateLimitError):
            await client.execute(messages=[{"role": "user", "content": "hi"}], model="m")
