"""Tests for the AI Engine Adapter."""

import pytest

from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.services.ai_engine_adapter import (
    AIEngineAdapter,
    AIEngineAdapterError,
    _build_opening_chat_user_data_block,
    assess_off_scope,
    get_test_generators_state,
    map_adapter_error_to_codes,
    reset_test_generators,
    set_test_chat_generator,
    set_test_guidance_generator,
)


@pytest.fixture(autouse=True)
def cleanup_generators() -> None:
    """Reset test generators after each test."""
    yield
    reset_test_generators()


def test_assess_off_scope_empty_response_is_off_scope() -> None:
    """Test that empty responses are detected as off-scope."""
    is_off_scope, score, reason = assess_off_scope("")
    assert is_off_scope is True
    assert score == 1.0
    assert reason == "empty_response"

    is_off_scope, score, reason = assess_off_scope("   ")
    assert is_off_scope is True
    assert score == 1.0


def test_assess_off_scope_explicit_marker_detected() -> None:
    """Test that [off_scope] marker is detected."""
    is_off_scope, score, reason = assess_off_scope("[off_scope] some response")
    assert is_off_scope is True
    assert score == 0.95
    assert reason == "explicit_marker"


def test_assess_off_scope_hors_scope_prefix_detected() -> None:
    """Test that hors_scope: prefix is detected."""
    is_off_scope, score, reason = assess_off_scope("hors_scope: some text")
    assert is_off_scope is True
    assert score == 0.9
    assert reason == "explicit_prefix"


def test_assess_off_scope_normal_response_not_flagged() -> None:
    """Test that normal responses are not flagged."""
    is_off_scope, score, reason = assess_off_scope("This is a normal response.")
    assert is_off_scope is False
    assert score == 0.0
    assert reason is None


@pytest.mark.asyncio
async def test_generate_chat_reply_uses_test_generator() -> None:
    """Test that test generator is used when set."""
    call_args: list[tuple] = []

    async def mock_generator(
        messages: list[dict[str, str]],
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str,
    ) -> str:
        call_args.append((messages, context, user_id, request_id, trace_id, locale))
        return "mocked response"

    set_test_chat_generator(mock_generator)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "Hello"}],
        context={"persona_line": "test persona"},
        user_id=123,
        request_id="req-1",
        trace_id="trace-1",
    )

    assert isinstance(result, GatewayResult)
    assert result.raw_output == "mocked response"
    assert len(call_args) == 1
    assert call_args[0][2] == 123
    assert call_args[0][3] == "req-1"


@pytest.mark.asyncio
async def test_generate_chat_reply_timeout_raises_timeout_error() -> None:
    """Test that TimeoutError is raised on timeout."""

    async def timeout_generator(*args, **kwargs) -> str:
        raise TimeoutError("test timeout")

    set_test_chat_generator(timeout_generator)

    with pytest.raises(TimeoutError):
        await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "Hello"}],
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )


@pytest.mark.asyncio
async def test_generate_chat_reply_connection_error_raises_connection_error() -> None:
    """Test that ConnectionError is raised on connection failure."""

    async def connection_error_generator(*args, **kwargs) -> str:
        raise ConnectionError("test connection error")

    set_test_chat_generator(connection_error_generator)

    with pytest.raises(ConnectionError):
        await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "Hello"}],
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )


@pytest.mark.asyncio
async def test_generate_guidance_uses_test_generator() -> None:
    """Test that test generator is used for guidance when set."""
    call_args: list[tuple] = []

    async def mock_generator(
        use_case: str,
        context: dict[str, str | None],
        user_id: int,
        request_id: str,
        trace_id: str,
        locale: str,
    ) -> str:
        call_args.append((use_case, context, user_id, request_id, trace_id, locale))
        return "mocked guidance"

    set_test_guidance_generator(mock_generator)

    result = await AIEngineAdapter.generate_guidance(
        use_case="guidance_daily",
        context={
            "birth_date": "1990-01-15",
            "birth_time": "14:30",
            "birth_timezone": "Europe/Paris",
        },
        user_id=456,
        request_id="req-2",
        trace_id="trace-2",
    )

    assert result.raw_output == "mocked guidance"
    assert len(call_args) == 1
    assert call_args[0][0] == "guidance_daily"
    assert call_args[0][2] == 456


@pytest.mark.asyncio
async def test_generate_guidance_timeout_raises_timeout_error() -> None:
    """Test that TimeoutError is raised on guidance timeout."""

    async def timeout_generator(*args, **kwargs) -> str:
        raise TimeoutError("test timeout")

    set_test_guidance_generator(timeout_generator)

    with pytest.raises(TimeoutError):
        await AIEngineAdapter.generate_guidance(
            use_case="guidance_weekly",
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )


@pytest.mark.asyncio
async def test_generate_guidance_adapter_error_rate_limit() -> None:
    """Test that AIEngineAdapterError is raised on rate limit error."""

    async def adapter_error_generator(*args, **kwargs) -> str:
        raise AIEngineAdapterError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after_ms": "60000"},
        )

    set_test_guidance_generator(adapter_error_generator)

    with pytest.raises(AIEngineAdapterError) as exc_info:
        await AIEngineAdapter.generate_guidance(
            use_case="guidance_contextual",
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )

    assert exc_info.value.code == "rate_limit_exceeded"


@pytest.mark.asyncio
async def test_generate_guidance_adapter_error_context_too_large() -> None:
    """Test that AIEngineAdapterError is raised on context too large error."""

    async def context_error_generator(*args, **kwargs) -> str:
        raise AIEngineAdapterError(
            code="context_too_large",
            message="context exceeds maximum tokens",
            details={"max_tokens": "4096", "actual_tokens": "8000"},
        )

    set_test_guidance_generator(context_error_generator)

    with pytest.raises(AIEngineAdapterError) as exc_info:
        await AIEngineAdapter.generate_guidance(
            use_case="guidance_daily",
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )

    assert exc_info.value.code == "context_too_large"
    assert "max_tokens" in exc_info.value.details


@pytest.mark.asyncio
async def test_generate_chat_adapter_error_validation() -> None:
    """Test that AIEngineAdapterError is raised on validation error."""

    async def validation_error_generator(*args, **kwargs) -> str:
        raise AIEngineAdapterError(
            code="invalid_chat_input",
            message="messages cannot be empty",
            details={"field": "messages"},
        )

    set_test_chat_generator(validation_error_generator)

    with pytest.raises(AIEngineAdapterError) as exc_info:
        await AIEngineAdapter.generate_chat_reply(
            messages=[],
            context={},
            user_id=123,
            request_id="req-1",
            trace_id="trace-1",
        )

    assert exc_info.value.code == "invalid_chat_input"
    assert exc_info.value.details.get("field") == "messages"


@pytest.mark.asyncio
async def test_reset_test_generators_clears_generators() -> None:
    """Test that reset_test_generators clears all generators."""

    async def mock_chat(*args, **kwargs) -> str:
        return "mock chat"

    async def mock_guidance(*args, **kwargs) -> str:
        return "mock guidance"

    set_test_chat_generator(mock_chat)
    set_test_guidance_generator(mock_guidance)

    result_chat = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "test"}],
        context={},
        user_id=1,
        request_id="r",
        trace_id="t",
    )
    assert result_chat.raw_output == "mock chat"

    result_guidance = await AIEngineAdapter.generate_guidance(
        use_case="guidance_daily",
        context={},
        user_id=1,
        request_id="r",
        trace_id="t",
    )
    assert result_guidance.raw_output == "mock guidance"

    chat_active, guidance_active = get_test_generators_state()
    assert chat_active is True
    assert guidance_active is True

    reset_test_generators()

    chat_active, guidance_active = get_test_generators_state()
    assert chat_active is False
    assert guidance_active is False


def test_map_adapter_error_to_codes_rate_limit() -> None:
    """Test mapping of rate_limit_exceeded error."""
    err = AIEngineAdapterError(
        code="rate_limit_exceeded",
        message="rate limit exceeded",
        details={"retry_after_ms": "60000"},
    )
    code, message = map_adapter_error_to_codes(err)
    assert code == "rate_limit_exceeded"
    assert message == "rate limit exceeded"


def test_map_adapter_error_to_codes_context_too_large() -> None:
    """Test mapping of context_too_large error."""
    err = AIEngineAdapterError(
        code="context_too_large",
        message="context exceeds maximum tokens",
        details={"max_tokens": "4096"},
    )
    code, message = map_adapter_error_to_codes(err)
    assert code == "context_too_large"
    assert message == "context too large"


def test_map_adapter_error_to_codes_timeout() -> None:
    """Test mapping of TimeoutError."""
    err = TimeoutError("provider timeout")
    code, message = map_adapter_error_to_codes(err)
    assert code == "llm_timeout"
    assert message == "llm provider timeout"


def test_map_adapter_error_to_codes_connection_error() -> None:
    """Test mapping of ConnectionError."""
    err = ConnectionError("connection failed")
    code, message = map_adapter_error_to_codes(err)
    assert code == "llm_unavailable"
    assert message == "llm provider is unavailable"


def test_map_adapter_error_to_codes_other_adapter_error() -> None:
    """Test mapping of other AIEngineAdapterError codes."""
    err = AIEngineAdapterError(
        code="invalid_chat_input",
        message="messages cannot be empty",
        details={"field": "messages"},
    )
    code, message = map_adapter_error_to_codes(err)
    assert code == "invalid_chat_input"
    assert message == "messages cannot be empty"


@pytest.mark.asyncio
async def test_generate_chat_reply_v2_omits_none_conversation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeGateway:
        async def execute(self, **kwargs):  # type: ignore[no-untyped-def]
            captured.update(kwargs)
            return GatewayResult(
                use_case="chat_astrologer",
                request_id="req-1",
                trace_id="trace-1",
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.llm_orchestration.gateway.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "bonjour"}],
        context={"conversation_id": None},
        user_id=1,
        request_id="req-chat-none",
        trace_id="trace-chat-none",
    )

    assert result.raw_output == "ok"
    user_input = captured["user_input"]
    assert isinstance(user_input, dict)
    assert "conversation_id" not in user_input


@pytest.mark.asyncio
async def test_generate_chat_reply_v2_converts_conversation_id_to_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeGateway:
        async def execute(self, **kwargs):  # type: ignore[no-untyped-def]
            captured.update(kwargs)
            return GatewayResult(
                use_case="chat_astrologer",
                request_id="req-1",
                trace_id="trace-1",
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.llm_orchestration.gateway.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "bonjour"}],
        context={"conversation_id": 42},
        user_id=1,
        request_id="req-chat-id",
        trace_id="trace-chat-id",
    )

    assert result.raw_output == "ok"
    user_input = captured["user_input"]
    assert isinstance(user_input, dict)
    assert user_input.get("conversation_id") == "42"


@pytest.mark.asyncio
async def test_generate_chat_reply_opening_turn_builds_minimal_user_data_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeGateway:
        async def execute(self, **kwargs):  # type: ignore[no-untyped-def]
            captured.update(kwargs)
            return GatewayResult(
                use_case="chat_astrologer",
                request_id="req-1",
                trace_id="trace-1",
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.llm_orchestration.gateway.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "Je me sens perdu aujourd'hui."}],
        context={
            "chat_turn_stage": "opening",
            "persona_name": "Mira",
            "persona_tone": "chaleureux",
            "persona_style_markers": "simple; intuitif",
            "today_date": "22 mars 2026",
            "user_profile_brief": "Nom: Daconrilcy | Email: daconrilcy@hotmail.com | Âge: 36 ans",
        },
        user_id=1,
        request_id="req-chat-opening",
        trace_id="trace-chat-opening",
    )

    assert result.raw_output == "ok"
    context = captured["context"]
    assert isinstance(context, dict)
    user_data_block = context.get("user_data_block")
    assert isinstance(user_data_block, str)
    assert "Je me sens perdu aujourd'hui." in user_data_block
    assert "22 mars 2026" in user_data_block
    assert "daconrilcy@hotmail.com" in user_data_block
    assert "N'ouvre pas spontanément une lecture complète du thème natal" in user_data_block


def test_map_adapter_error_to_codes_gateway_input_validation_passthrough() -> None:
    err = AIEngineAdapterError(
        code="invalid_chat_astrologer_input",
        message="Input validation failed for 'chat_astrologer'",
        status_code=422,
        details={"errors": ["[conversation_id] None is not of type 'string'"]},
    )
    code, message = map_adapter_error_to_codes(err)
    assert code == "invalid_chat_astrologer_input"
    assert message == "Input validation failed for 'chat_astrologer'"


def test_build_opening_chat_user_data_block_flags_unclear_first_message() -> None:
    payload = _build_opening_chat_user_data_block(
        last_user_msg="chch",
        context={
            "persona_name": "Mira",
            "persona_tone": "chaleureux",
            "persona_style_markers": "simple; intuitif",
            "today_date": "22 mars 2026",
            "user_profile_brief": "Nom: Daconrilcy | Email: daconrilcy@hotmail.com | Âge: 36 ans",
        },
    )

    assert "Le premier message semble vague ou incompréhensible." in payload
    assert "Ne réponds pas avec une formule robotique" in payload
