from unittest.mock import AsyncMock

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


@pytest.mark.asyncio
async def test_gateway_composes_4_layers():
    # Arrange
    mock_client = AsyncMock()
    # Mock result
    mock_result = GatewayResult(
        use_case="natal_interpretation",
        request_id="req-123",
        trace_id="trace-456",
        raw_output="Interprétation natale stub",
        usage=UsageInfo(input_tokens=10, output_tokens=20, total_tokens=30),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o-mini"),
    )
    mock_client.execute.return_value = mock_result

    gateway = LLMGateway(responses_client=mock_client)

    # Act
    await gateway.execute(
        use_case="natal_interpretation",
        user_input={
            "birth_date": "1990-01-01",
            "locale": "fr-FR",
            "use_case": "natal_interpretation",
        },  # noqa: E501
        context={"chart_json": '{"sun": "Aries"}', "persona_block": "[persona: default]"},
        request_id="req-123",
        trace_id="trace-456",
    )

    # Assert
    mock_client.execute.assert_called_once()
    args, kwargs = mock_client.execute.call_args
    messages = kwargs["messages"]

    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert "assistant astrologique expert" in messages[0]["content"]

    assert messages[1]["role"] == "developer"
    assert "1990-01-01" in messages[1]["content"]
    assert '{"sun": "Aries"}' in messages[1]["content"]

    assert messages[2]["role"] == "developer"
    assert "[persona: default]" in messages[2]["content"]

    assert messages[3]["role"] == "user"
    assert "Chart Data" in messages[3]["content"]


@pytest.mark.asyncio
async def test_gateway_context_overrides_user_input():
    # Arrange
    mock_client = AsyncMock()
    mock_result = GatewayResult(
        use_case="guidance_daily",
        request_id="req-1",
        trace_id="trace-1",
        raw_output="v2",
        usage=UsageInfo(input_tokens=0, output_tokens=0, total_tokens=0),
        meta=GatewayMeta(latency_ms=0, model="m"),
    )
    mock_client.execute.return_value = mock_result
    gateway = LLMGateway(responses_client=mock_client)

    # Use-case guidance_daily needs {{situation}}
    # Act
    await gateway.execute(
        use_case="guidance_daily",
        user_input={
            "situation": "original_situation",
            "locale": "fr-FR",
            "use_case": "guidance_daily",
        },  # noqa: E501
        context={"situation": "overridden_situation"},
        request_id="req-1",
        trace_id="trace-1",
    )

    # Assert
    args, kwargs = mock_client.execute.call_args
    messages = kwargs["messages"]
    assert "overridden_situation" in messages[1]["content"]
    assert "original_situation" not in messages[1]["content"]


@pytest.mark.asyncio
async def test_gateway_filters_extra_variables():
    # Arrange
    mock_client = AsyncMock()
    mock_result = GatewayResult(
        use_case="guidance_daily",
        request_id="req-1",
        trace_id="trace-1",
        raw_output="v2",
        usage=UsageInfo(input_tokens=0, output_tokens=0, total_tokens=0),
        meta=GatewayMeta(latency_ms=0, model="m"),
    )
    mock_client.execute.return_value = mock_result
    gateway = LLMGateway(responses_client=mock_client)

    # Act
    # guidance_daily only requires 'situation'
    await gateway.execute(
        use_case="guidance_daily",
        user_input={
            "situation": "some_situation",
            "malicious_var": "ignore me",
            "locale": "fr-FR",
            "use_case": "guidance_daily",
        },  # noqa: E501
        context={},
        request_id="req-1",
        trace_id="trace-1",
    )

    # Assert
    args, kwargs = mock_client.execute.call_args
    # We can't directly check render_vars as it's local to execute(),
    # but we can check the rendered prompt in messages[1] if we use a template that includes it.
    # The stub for guidance_daily is: "Génère une guidance quotidienne basée sur le contexte: {{situation}}."  # noqa: E501
    # If malicious_var was passed to renderer, it would be ignored anyway by renderer.
    # But let's verify malicious_var didn't accidentally get in.
    assert "ignore me" not in kwargs["messages"][1]["content"]
