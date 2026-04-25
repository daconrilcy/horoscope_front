from unittest.mock import AsyncMock, patch

import pytest

from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.tests.helpers.llm_adapter_stub import reset_test_generators


@pytest.mark.asyncio
async def test_routing_v2_always_uses_gateway():
    # Ensure no test generators are interfering
    reset_test_generators()

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = GatewayResult(
            use_case="chat_astrologer",
            request_id="r1",
            trace_id="t1",
            raw_output="v2_response",
            usage=UsageInfo(input_tokens=3, output_tokens=2, total_tokens=5),
            meta=GatewayMeta(latency_ms=1, model="test-model"),
        )

        response = await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "hi"}],
            context={"persona_line": "friendly"},
            user_id=1,
            request_id="r1",
            trace_id="t1",
        )

        assert response.raw_output == "v2_response"
        mock_execute.assert_called_once()
