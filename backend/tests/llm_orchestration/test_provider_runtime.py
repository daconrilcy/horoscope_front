from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APITimeoutError, RateLimitError

from app.ai_engine.exceptions import (
    RetryBudgetExhaustedError,
    UpstreamCircuitOpenError,
    UpstreamRateLimitError,
)
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.provider_runtime_manager import ProviderRuntimeManager
from app.infrastructure.providers.llm.circuit_breaker import _breakers


@pytest.fixture(autouse=True)
def clear_breakers():
    _breakers.clear()
    yield


@pytest.mark.asyncio
async def test_runtime_manager_retry_on_timeout():
    # Arrange
    mock_client = MagicMock()

    # First attempt: Timeout
    # Second attempt: Success
    mock_result = GatewayResult(
        use_case="test",
        request_id="r1",
        trace_id="t1",
        raw_output="ok",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="m1"),
    )

    mock_client.execute = AsyncMock(
        side_effect=[APITimeoutError(request=MagicMock()), (mock_result, {"x-request-id": "r1"})]
    )

    manager = ProviderRuntimeManager(mock_client)

    # Act
    result = await manager.execute_with_resilience(
        messages=[{"role": "user", "content": "hi"}], model="m1", family="chat"
    )

    # Assert
    assert result.raw_output == "ok"
    assert result.meta.attempt_count == 2
    assert mock_client.execute.call_count == 2


@pytest.mark.asyncio
async def test_runtime_manager_terminal_on_quota():
    # Arrange
    mock_client = MagicMock()

    err = RateLimitError(
        message="Quota exceeded",
        response=MagicMock(),
        body={"error": {"message": "Quota exceeded", "code": "insufficient_quota"}},
    )
    # err.code is often set by the SDK from the body

    mock_client.execute = AsyncMock(side_effect=err)

    manager = ProviderRuntimeManager(mock_client)

    # Act & Assert
    with patch.object(err, "code", "insufficient_quota"):
        with pytest.raises(UpstreamRateLimitError) as excinfo:
            await manager.execute_with_resilience(messages=[], model="m")

    assert excinfo.value.error_type == "UPSTREAM_QUOTA_EXHAUSTED"
    assert mock_client.execute.call_count == 1  # Terminal


@pytest.mark.asyncio
async def test_runtime_manager_circuit_breaker_opens():
    # Arrange
    mock_client = MagicMock()

    def _raise_timeout(*args, **kwargs):
        raise APITimeoutError(request=MagicMock())

    mock_client.execute = AsyncMock(side_effect=_raise_timeout)

    # failure_threshold=5 by default
    manager = ProviderRuntimeManager(mock_client)

    # Act: 5 calls total. Each call records exactly 1 failure (last attempt).
    # Total 5 failures == threshold 5.
    for _ in range(5):
        with pytest.raises(RetryBudgetExhaustedError):
            await manager.execute_with_resilience(messages=[], model="m", family="chat")

    assert mock_client.execute.call_count == 15  # 5 calls * 3 attempts

    # Act: Breaker should now be open
    with pytest.raises(UpstreamCircuitOpenError):
        await manager.execute_with_resilience(messages=[], model="m", family="chat")

    # Still 15 because it didn't call the client again
    assert mock_client.execute.call_count == 15


@pytest.mark.asyncio
async def test_runtime_manager_recovers_headers_on_failure():
    # Arrange
    mock_client = MagicMock()
    err = RateLimitError(message="Rate limit", response=MagicMock(), body={})
    # Finding High: simulate headers extracted by ResponsesClient
    err._provider_headers = {"retry-after": "5", "x-request-id": "req-fail-1"}

    mock_client.execute = AsyncMock(side_effect=err)
    manager = ProviderRuntimeManager(mock_client)

    # Act
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(RetryBudgetExhaustedError):
            await manager.execute_with_resilience(messages=[], model="m")

        # Assert: delay should be 5000ms (5s * 1000)
        mock_sleep.assert_any_call(5.0)


@pytest.mark.asyncio
async def test_circuit_breaker_sliding_window():
    # Arrange
    from app.infrastructure.providers.llm.circuit_breaker import CircuitBreaker

    # Threshold 2, window 1s
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=10, window_sec=1)

    with patch("time.monotonic") as mock_time:
        mock_time.return_value = 100.0

        # Act: 1 failure at T=100
        breaker.record_failure()
        assert breaker.allow_request() is True

        # Move to T=101.1 (> 1s window)
        mock_time.return_value = 101.1
        breaker._clean_old_failures()
        assert len(breaker.failure_timestamps) == 0
        assert breaker.allow_request() is True

        # 2 failures within window
        mock_time.return_value = 102.0
        breaker.record_failure()  # 1st at T=102
        mock_time.return_value = 102.1
        breaker.record_failure()  # 2nd at T=102.1 (within 1s)

        assert breaker.allow_request() is False
        assert breaker.state == "open"
