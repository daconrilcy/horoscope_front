from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.ai_engine.exceptions import UpstreamError, UpstreamRateLimitError, UpstreamTimeoutError
from app.llm_orchestration.providers.responses_client import ResponsesClient


@pytest.mark.asyncio
async def test_rate_limit_error_raises_upstream_rate_limit():
    client = ResponsesClient()
    # RateLimitError(message, response, body)
    mock_response = MagicMock()
    mock_error = RateLimitError("Rate limit", response=mock_response, body={})
    mock_func = AsyncMock(side_effect=mock_error)

    with pytest.raises(UpstreamRateLimitError):
        await client._execute_with_retry("test", mock_func, timeout_seconds=1)


@pytest.mark.asyncio
async def test_api_timeout_raises_upstream_timeout():
    client = ResponsesClient()
    mock_request = MagicMock()
    mock_error = APITimeoutError(request=mock_request)
    mock_func = AsyncMock(side_effect=mock_error)

    with pytest.raises(UpstreamTimeoutError) as excinfo:
        await client._execute_with_retry("test", mock_func, timeout_seconds=5)
    assert "5s" in str(excinfo.value)


@pytest.mark.asyncio
async def test_api_connection_error_raises_upstream_error():
    client = ResponsesClient()
    mock_request = MagicMock()
    mock_error = APIConnectionError(request=mock_request)
    mock_func = AsyncMock(side_effect=mock_error)

    with pytest.raises(UpstreamError) as excinfo:
        await client._execute_with_retry("test", mock_func, timeout_seconds=1)
    assert excinfo.value.details.get("kind") == "connection_error"
