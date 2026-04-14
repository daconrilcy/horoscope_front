import pytest

from app.ai_engine.exceptions import RetryBudgetExhaustedError, UpstreamCircuitOpenError
from app.llm_orchestration.models import GatewayMeta, GatewayResult, NatalExecutionInput, UsageInfo
from app.services.ai_engine_adapter import AIEngineAdapter, AIEngineAdapterError


@pytest.mark.asyncio
async def test_generate_chat_reply_v2_omits_none_conversation_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGateway:
        async def execute_request(self, request, db=None):
            return GatewayResult(
                use_case=request.user_input.use_case,
                request_id=request.request_id,
                trace_id=request.trace_id,
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "bonjour"}],
        context={"conversation_id": None},
        user_id=1,
        request_id="req-chat-none",
        trace_id="trace-chat-none",
    )

    assert result.raw_output == "ok"


@pytest.mark.asyncio
async def test_generate_chat_reply_v2_converts_conversation_id_to_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGateway:
        async def execute_request(self, request, db=None):
            return GatewayResult(
                use_case=request.user_input.use_case,
                request_id=request.request_id,
                trace_id=request.trace_id,
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_chat_reply(
        messages=[{"role": "user", "content": "bonjour"}],
        context={"conversation_id": 42},
        user_id=1,
        request_id="req-chat-id",
        trace_id="trace-chat-id",
    )

    assert result.raw_output == "ok"


@pytest.mark.asyncio
async def test_generate_chat_reply_opening_turn_builds_minimal_user_data_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGateway:
        async def execute_request(self, request, db=None):
            return GatewayResult(
                use_case=request.user_input.use_case,
                request_id=request.request_id,
                trace_id=request.trace_id,
                raw_output="ok",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

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


@pytest.mark.asyncio
async def test_generate_chat_reply_maps_circuit_open_to_structured_adapter_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGateway:
        async def execute_request(self, request, db=None):
            raise UpstreamCircuitOpenError(provider="openai", family="chat")

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

    with pytest.raises(AIEngineAdapterError) as exc_info:
        await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "bonjour"}],
            context={},
            user_id=1,
            request_id="req-chat-circuit-open",
            trace_id="trace-chat-circuit-open",
        )

    assert exc_info.value.code == "upstream_circuit_open"
    assert exc_info.value.status_code == 503
    assert exc_info.value.details == {"provider": "openai", "family": "chat"}


@pytest.mark.asyncio
async def test_generate_chat_reply_maps_retry_budget_exhausted_to_structured_adapter_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGateway:
        async def execute_request(self, request, db=None):
            raise RetryBudgetExhaustedError(attempts=3, last_error="UPSTREAM_TIMEOUT")

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

    with pytest.raises(AIEngineAdapterError) as exc_info:
        await AIEngineAdapter.generate_chat_reply(
            messages=[{"role": "user", "content": "bonjour"}],
            context={},
            user_id=1,
            request_id="req-chat-budget-exhausted",
            trace_id="trace-chat-budget-exhausted",
        )

    assert exc_info.value.code == "retry_budget_exhausted"
    assert exc_info.value.status_code == 502
    assert exc_info.value.details == {"attempts": "3", "last_error": "UPSTREAM_TIMEOUT"}


@pytest.mark.asyncio
async def test_generate_natal_interpretation_maps_free_legacy_use_case_to_canonical_subfeature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_request = None

    class FakeGateway:
        async def execute_request(self, request, db=None):
            nonlocal captured_request
            captured_request = request
            return GatewayResult(
                use_case=request.user_input.use_case,
                request_id=request.request_id,
                trace_id=request.trace_id,
                raw_output="{}",
                usage=UsageInfo(input_tokens=10, output_tokens=10),
                meta=GatewayMeta(latency_ms=100, model="test-model"),
            )

    monkeypatch.setattr("app.services.ai_engine_adapter.LLMGateway", FakeGateway)

    result = await AIEngineAdapter.generate_natal_interpretation(
        NatalExecutionInput(
            use_case_key="natal_long_free",
            locale="fr-FR",
            level="complete",
            chart_json='{"meta": {"chart_json_version": "1"}}',
            natal_data={"meta": {"chart_json_version": "1"}},
            evidence_catalog=[],
            plan="free",
            validation_strict=False,
            user_id=1,
            request_id="req-natal-free",
            trace_id="trace-natal-free",
            variant_code="free_short",
        )
    )

    assert result.raw_output == "{}"
    assert captured_request is not None
    assert captured_request.user_input.use_case == "natal_long_free"
    assert captured_request.user_input.feature == "natal"
    assert captured_request.user_input.subfeature == "interpretation"
