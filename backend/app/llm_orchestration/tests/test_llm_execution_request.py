import pytest
from pydantic import ValidationError

from app.llm_orchestration.gateway import LLMGateway
from app.llm_orchestration.models import (
    ExecutionContext,
    ExecutionMessage,
    ExecutionOverrides,
    ExecutionUserInput,
    GatewayMeta,
    GatewayResult,
    LLMExecutionRequest,
    UsageInfo,
)


def test_execution_message_frozen():
    msg = ExecutionMessage(role="user", content="hello")
    with pytest.raises(ValidationError):
        msg.content = "world"


def test_llm_execution_request_serialization():
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="chat", message="hello"),
        request_id="req-123",
        trace_id="trace-456",
    )
    dump = request.model_dump()
    assert dump["user_input"]["use_case"] == "chat"
    assert dump["request_id"] == "req-123"
    assert "db" not in dump


def test_legacy_dicts_to_request_chat():
    use_case = "chat"
    user_input = {"message": "hello", "locale": "en-US"}
    context = {
        "history": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
        "conversation_id": "conv-1",
        "some_extra": "value",
    }

    request = LLMGateway._legacy_dicts_to_request(
        use_case=use_case, user_input=user_input, context=context, request_id="r1", trace_id="t1"
    )

    assert request.user_input.use_case == "chat"
    assert request.user_input.locale == "en-US"
    assert request.user_input.message == "hello"
    assert len(request.context.history) == 2
    assert request.context.history[0].role == "user"
    assert request.user_input.conversation_id == "conv-1"
    assert request.context.extra_context["some_extra"] == "value"


def test_legacy_dicts_to_request_visited_migration():
    context = {"_visited_use_cases": ["uc1", "uc2"]}
    request = LLMGateway._legacy_dicts_to_request(
        use_case="test", user_input={}, context=context, request_id="r1", trace_id="t1"
    )
    assert request.flags.visited_use_cases == ["uc1", "uc2"]


def test_execution_overrides_validation():
    # Test valid overrides
    overrides = ExecutionOverrides(interaction_mode="chat", user_question_policy="required")
    assert overrides.interaction_mode == "chat"

    # Test invalid values (Pydantic Literal validation)
    with pytest.raises(ValidationError):
        ExecutionOverrides(interaction_mode="invalid_mode")


@pytest.mark.asyncio
async def test_execute_request_basic(db):
    # This test uses the 'db' fixture from conftest.py
    gateway = LLMGateway()
    request = LLMExecutionRequest(
        user_input=ExecutionUserInput(use_case="test_natal", locale="fr-FR"),
        context=ExecutionContext(chart_json='{"planets": []}'),
        request_id="test-req",
        trace_id="test-trace",
        flags={"test_fallback_active": True},
    )

    # Mock result
    mock_res = GatewayResult(
        use_case="test_natal",
        request_id="test-req",
        trace_id="test-trace",
        raw_output='{"title": "test", "summary": "test", "accordion_titles": ["a"]}',
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
    )

    from unittest.mock import AsyncMock

    gateway.client.execute = AsyncMock(return_value=(mock_res, {}))

    result = await gateway.execute_request(request, db=db)
    assert result.use_case == "test_natal"
    gateway.client.execute.assert_called_once()


def test_extra_context_exclusion():
    context = {
        "history": [],
        "natal_data": {},
        "extra_field": "should_be_in_extra",
        "locale": "fr-FR",
    }
    request = LLMGateway._legacy_dicts_to_request("uc", {}, context, "r", "t")
    assert "extra_field" in request.context.extra_context
    assert "history" not in request.context.extra_context
    assert "natal_data" not in request.context.extra_context
    assert "locale" not in request.context.extra_context


def test_execution_message_content_blocks():
    # Content blocks for GPT-5 preparation
    blocks = [{"type": "text", "text": "hello"}]
    msg = ExecutionMessage(role="user", content="hello", content_blocks=blocks)
    assert msg.content_blocks == blocks
