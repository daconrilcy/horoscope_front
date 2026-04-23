from unittest.mock import MagicMock

import pytest

from app.domain.llm.runtime.provider_runtime_manager import ProviderRuntimeManager
from app.domain.llm.runtime.simulation_context import simulation_error as simulation_error_ctx
from app.infra.providers.llm.circuit_breaker import get_circuit_breaker


@pytest.fixture(autouse=True)
def reset_breaker():
    breaker = get_circuit_breaker("openai", "global", failure_threshold=5, recovery_timeout_sec=60)
    breaker._state = "closed"
    breaker._failure_count = 0
    breaker._last_failure_time = 0
    yield


@pytest.mark.asyncio
async def test_simulate_rate_limit():
    manager = ProviderRuntimeManager(responses_client=MagicMock())
    token = simulation_error_ctx.set("rate_limit")
    try:
        with pytest.raises(Exception) as excinfo:
            await manager.execute_with_resilience(messages=[], model="gpt-4o")
        assert (
            "rate_limit" in str(excinfo.value).lower() or "rate limit" in str(excinfo.value).lower()
        )
    finally:
        simulation_error_ctx.reset(token)


@pytest.mark.asyncio
async def test_simulate_timeout():
    manager = ProviderRuntimeManager(responses_client=MagicMock())
    token = simulation_error_ctx.set("timeout")
    # Set a short timeout for the test
    manager._get_timeout = lambda family: 1
    try:
        with pytest.raises(Exception) as excinfo:
            await manager.execute_with_resilience(messages=[], model="gpt-4o")
        assert "timeout" in str(excinfo.value).lower()
    finally:
        simulation_error_ctx.reset(token)


@pytest.mark.asyncio
async def test_simulate_server_error():
    manager = ProviderRuntimeManager(responses_client=MagicMock())
    token = simulation_error_ctx.set("server_error")
    try:
        with pytest.raises(Exception) as excinfo:
            await manager.execute_with_resilience(messages=[], model="gpt-4o")
        assert (
            "server error" in str(excinfo.value).lower()
            or "upstream_error" in str(excinfo.value).lower()
        )
    finally:
        simulation_error_ctx.reset(token)
