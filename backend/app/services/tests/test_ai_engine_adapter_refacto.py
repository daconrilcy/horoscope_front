from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.llm.ai_engine_adapter import AIEngineAdapter, AIEngineAdapterError
from app.llm_orchestration.models import (
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    OutputValidationError,
    UsageInfo,
)


@pytest.mark.asyncio
async def test_generate_chat_reply_canonical_request():
    messages = [{"role": "user", "content": "hello"}]
    context = {"conversation_id": "conv-123"}

    mock_res = GatewayResult(
        use_case="chat_astrologer",
        request_id="req-1",
        trace_id="tr-1",
        raw_output="hi",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = mock_res

        result = await AIEngineAdapter.generate_chat_reply(
            messages=messages, context=context, user_id=1, request_id="req-1", trace_id="tr-1"
        )

        assert result == mock_res
        mock_exec.assert_called_once()
        request = mock_exec.call_args.kwargs["request"]
        assert isinstance(request, LLMExecutionRequest)
        assert request.user_input.use_case == "chat_astrologer"
        assert request.user_input.message == "hello"
        assert request.user_input.conversation_id == "conv-123"


@pytest.mark.asyncio
async def test_generate_guidance_daily_canonical():
    context = {"situation": "test situation"}

    mock_res = GatewayResult(
        use_case="guidance_daily",
        request_id="req-2",
        trace_id="tr-2",
        raw_output="guidance",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = mock_res

        result = await AIEngineAdapter.generate_guidance(
            use_case="guidance_daily",
            context=context,
            user_id=1,
            request_id="req-2",
            trace_id="tr-2",
        )

        assert result == mock_res
        request = mock_exec.call_args.kwargs["request"]
        assert request.user_input.use_case == "guidance_daily"
        assert request.user_input.situation == "test situation"


@pytest.mark.asyncio
async def test_generate_guidance_contextual_extra_context():
    context = {"objective": "win", "time_horizon": "soon"}

    mock_res = GatewayResult(
        use_case="guidance_contextual",
        request_id="req-3",
        trace_id="tr-3",
        raw_output="guidance",
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=10, model="m"),
    )

    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = mock_res

        await AIEngineAdapter.generate_guidance(
            use_case="guidance_contextual",
            context=context,
            user_id=1,
            request_id="req-3",
            trace_id="tr-3",
        )

        request = mock_exec.call_args.kwargs["request"]
        assert request.context.extra_context["objective"] == "win"
        assert request.context.extra_context["time_horizon"] == "soon"


@pytest.mark.asyncio
async def test_error_mapping_output_validation():
    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.side_effect = OutputValidationError("invalid output")

        with pytest.raises(AIEngineAdapterError) as exc_info:
            await AIEngineAdapter.generate_chat_reply(
                messages=[{"role": "user", "content": "h"}],
                context={},
                user_id=1,
                request_id="r",
                trace_id="t",
            )

        assert exc_info.value.status_code == 422
        assert exc_info.value.code == "invalid_chat_output"


@pytest.mark.asyncio
async def test_chat_opening_stage_extra_context():
    messages = [{"role": "user", "content": "hi"}]
    context = {"chat_turn_stage": "opening"}

    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = MagicMock(spec=GatewayResult, usage=MagicMock(output_tokens=10))

        await AIEngineAdapter.generate_chat_reply(
            messages=messages, context=context, user_id=1, request_id="r", trace_id="t"
        )

        request = mock_exec.call_args.kwargs["request"]
        assert request.context.extra_context["chat_turn_stage"] == "opening"
        assert "user_data_block" in request.context.extra_context
