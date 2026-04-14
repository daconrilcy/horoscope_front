from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import (
    RetryBudgetExhaustedError,
)
from app.llm_orchestration.providers.provider_runtime_manager import ProviderRuntimeManager
from app.llm_orchestration.providers.responses_client import ResponsesClient


@pytest.mark.asyncio
async def test_rate_limit_error_raises_upstream_rate_limit(monkeypatch: pytest.MonkeyPatch):
    client = ResponsesClient()
    monkeypatch.setattr(ai_engine_settings, "max_retries", 0)
    # RateLimitError(message, response, body)
    mock_response = MagicMock()
    mock_error = RateLimitError("Rate limit", response=mock_response, body={})
    client.execute = AsyncMock(side_effect=mock_error)
    manager = ProviderRuntimeManager(responses_client=client)

    with pytest.raises(RetryBudgetExhaustedError) as excinfo:
        await manager.execute_with_resilience(messages=[], model="gpt-4o-mini")
    assert excinfo.value.details.get("attempts") == "1"


@pytest.mark.asyncio
async def test_api_timeout_raises_upstream_timeout(monkeypatch: pytest.MonkeyPatch):
    client = ResponsesClient()
    monkeypatch.setattr(ai_engine_settings, "max_retries", 0)
    mock_request = MagicMock()
    mock_error = APITimeoutError(request=mock_request)
    client.execute = AsyncMock(side_effect=mock_error)
    manager = ProviderRuntimeManager(responses_client=client)

    with pytest.raises(RetryBudgetExhaustedError) as excinfo:
        await manager.execute_with_resilience(messages=[], model="gpt-4o-mini", family="chat")
    assert excinfo.value.details.get("attempts") == "1"


@pytest.mark.asyncio
async def test_api_connection_error_raises_upstream_error(monkeypatch: pytest.MonkeyPatch):
    client = ResponsesClient()
    monkeypatch.setattr(ai_engine_settings, "max_retries", 0)
    mock_request = MagicMock()
    mock_error = APIConnectionError(request=mock_request)
    client.execute = AsyncMock(side_effect=mock_error)
    manager = ProviderRuntimeManager(responses_client=client)

    with pytest.raises(RetryBudgetExhaustedError) as excinfo:
        await manager.execute_with_resilience(messages=[], model="gpt-4o-mini")
    assert excinfo.value.details.get("attempts") == "1"
