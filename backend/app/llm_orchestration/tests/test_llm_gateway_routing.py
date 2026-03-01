from unittest.mock import AsyncMock, patch

import pytest

from app.ai_engine.config import ai_engine_settings
from app.services.ai_engine_adapter import AIEngineAdapter


@pytest.mark.asyncio
async def test_routing_v1_when_flag_false():
    # Arrange
    with patch("app.ai_engine.services.chat_service.chat") as mock_chat:
        mock_chat.return_value = AsyncMock(text="v1_response")

        # Act
        response = await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "hi"}],
            context={"persona_line": "friendly"},
            user_id=1,
            request_id="r1",
            trace_id="t1",
        )

        # Assert
        assert response == "v1_response"
        mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_routing_v2_when_flag_true():
    # Arrange
    # Need to set flag to true
    ai_engine_settings.llm_orchestration_v2 = True

    try:
        with patch("app.llm_orchestration.gateway.LLMGateway.execute") as mock_execute:
            mock_execute.return_value = AsyncMock(raw_output="v2_response")

            # Act
            response = await AIEngineAdapter.generate_chat_reply(
                messages=[{"role": "user", "content": "hi"}],
                context={"persona_line": "friendly"},
                user_id=1,
                request_id="r1",
                trace_id="t1",
            )

            # Assert
            assert response == "v2_response"
            mock_execute.assert_called_once()
            args, kwargs = mock_execute.call_args
            assert kwargs["use_case"] == "chat_astrologer"
            assert kwargs["user_input"]["last_user_msg"] == "hi"
    finally:
        # Restore flag
        ai_engine_settings.llm_orchestration_v2 = False
