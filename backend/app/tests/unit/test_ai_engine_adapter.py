import pytest

from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.services.ai_engine_adapter import AIEngineAdapter


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
