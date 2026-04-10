from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo


@pytest.mark.asyncio
async def test_gateway_composes_4_layers():
    """Vérifie que les 4 couches de prompt sont bien composées."""
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case="natal_interpretation_short",
            request_id="r1",
            trace_id="t1",
            raw_output='{"message": "ok"}',
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=1, model="m"),
        )
    )

    gateway = LLMGateway(responses_client=mock_client)

    await gateway.execute(
        use_case="natal_interpretation_short",
        user_input={"locale": "fr"},
        context={"chart_json": "{}"},
        request_id="r1",
        trace_id="t1",
    )

    # Assert
    mock_client.execute.assert_called_once()
    args = mock_client.execute.call_args.kwargs
    messages = args["messages"]

    # Layer 1: System core
    assert messages[0]["role"] == "system"
    # Layer 2: Developer prompt
    assert messages[1]["role"] == "developer"
    # Layer 4: User payload (Layer 3 Persona is optional)
    assert any(m["role"] == "user" for m in messages)


@pytest.mark.asyncio
async def test_gateway_context_overrides_user_input():
    """Vérifie que context a la priorité sur user_input pour les variables de rendu."""
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case="guidance_contextual",
            request_id="r1",
            trace_id="t1",
            raw_output='{"summary": "ok", "key_points": ["p1"], "advice": "go"}',
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=1, model="m"),
        )
    )
    gateway = LLMGateway(responses_client=mock_client)

    await gateway.execute(
        use_case="guidance_contextual",
        user_input={"situation": "from_input", "locale": "fr", "question": "test?"},
        context={"situation": "from_context"},
        request_id="r1",
        trace_id="t1",
    )

    # In _resolve_plan, render_vars = {**user_input, **context} -> context has priority
    args = mock_client.execute.call_args.kwargs
    dev_prompt = args["messages"][1]["content"]
    assert "from_context" in dev_prompt


@pytest.mark.asyncio
async def test_gateway_filters_extra_variables():
    """Vérifie que seules les variables autorisées sont injectées dans le prompt."""
    mock_client = MagicMock()
    mock_client.execute = AsyncMock(
        return_value=GatewayResult(
            use_case="guidance_daily",
            request_id="r1",
            trace_id="t1",
            raw_output='{"summary": "ok", "key_points": ["p1"], "advice": "go"}',
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=1, model="m"),
        )
    )
    gateway = LLMGateway(responses_client=mock_client)

    await gateway.execute(
        use_case="guidance_daily",
        user_input={"situation": "ok", "evil_var": "HACK", "locale": "fr"},
        context={},
        request_id="r1",
        trace_id="t1",
    )

    args = mock_client.execute.call_args.kwargs
    dev_prompt = args["messages"][1]["content"]
    assert "HACK" not in dev_prompt
