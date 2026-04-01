from unittest.mock import patch

import pytest

from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.services.ai_engine_adapter import AIEngineAdapter


@pytest.mark.asyncio
async def test_routing_v2_always_uses_gateway():
    # Arrange
    with patch("app.llm_orchestration.gateway.LLMGateway.execute") as mock_execute:
        mock_execute.return_value = GatewayResult(
            use_case="chat_astrologer",
            request_id="r1",
            trace_id="t1",
            raw_output="v2_response",
            usage=UsageInfo(input_tokens=3, output_tokens=2, total_tokens=5),
            meta=GatewayMeta(latency_ms=1, model="test-model"),
        )

        # Act
        response = await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "hi"}],
            context={"persona_line": "friendly"},
            user_id=1,
            request_id="r1",
            trace_id="t1",
        )

        # Assert
        assert response.raw_output == "v2_response"
        mock_execute.assert_called_once()
        _, kwargs = mock_execute.call_args
        assert kwargs["use_case"] == "chat_astrologer"
        assert kwargs["user_input"]["last_user_msg"] == "hi"
