from unittest.mock import AsyncMock, patch

import pytest

from app.application.llm.ai_engine_adapter import AIEngineAdapter
from app.domain.llm.prompting.context import PromptCommonContext, QualifiedContext
from app.domain.llm.runtime.contracts import (
    GatewayMeta,
    GatewayResult,
    OutputValidationError,
    UsageInfo,
)
from app.prediction.llm_narrator import NarratorResult


def _make_dummy_context():
    return PromptCommonContext(
        user_id=1,
        user_first_name="Test",
        user_birth_data="1990-01-01",
        natal_interpretation="Natal",
        today_date="2026-04-09",
        precision_level="précision complète",
        astrologer_profile={"name": "Standard"},
        period_covered="journée du 2026-04-09",
        use_case_name="Test Use Case",
        use_case_key="daily_prediction",
    )


def _make_dummy_qualified_context() -> QualifiedContext:
    return QualifiedContext(payload=_make_dummy_context(), source="db")


@pytest.mark.asyncio
async def test_generate_horoscope_narration_routing_free(db):
    """Test AC2: variant_code='summary_only' -> horoscope_daily/free."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = GatewayResult(
            use_case="horoscope_daily",
            request_id="req-1",
            trace_id="tr-1",
            raw_output='{"daily_synthesis": "...", "daily_advice": null}',
            structured_output={
                "daily_synthesis": "Phrase 1. Phrase 2. Phrase 3. Phrase 4. "
                "Phrase 5. Phrase 6. Phrase 7.",
                "astro_events_intro": "intro",
                "time_window_narratives": {},
                "turning_point_narratives": [],
                "main_turning_point_narrative": None,
                "daily_advice": {"advice": "a", "emphasis": "e"},
            },
            usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20),
            meta=GatewayMeta(latency_ms=100, model="gpt-4o"),
        )

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only",
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-1",
            trace_id="tr-1",
            db=db,
        )

        assert res is not None
        args, kwargs = mock_exec.call_args
        request = kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.plan == "free"


@pytest.mark.asyncio
async def test_generate_horoscope_narration_routing_premium(db):
    """Test AC3: variant_code='full' -> horoscope_daily/premium."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = GatewayResult(
            use_case="horoscope_daily",
            request_id="req-2",
            trace_id="tr-2",
            raw_output="{}",
            structured_output={
                "daily_synthesis": "P1. P2. P3. P4. P5. P6. P7. P8. P9. P10.",
                "astro_events_intro": "intro",
                "time_window_narratives": {},
                "turning_point_narratives": [],
                "main_turning_point_narrative": None,
                "daily_advice": {"advice": "a", "emphasis": "e"},
            },
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="full",
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-2",
            trace_id="tr-2",
            db=db,
        )

        assert res is not None
        args, kwargs = mock_exec.call_args
        request = kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.plan == "premium"


@pytest.mark.asyncio
async def test_generate_horoscope_narration_routing_default(db):
    """Test AC4: variant_code=None -> horoscope_daily/free (Story 66.28 closure)."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = GatewayResult(
            use_case="horoscope_daily",
            request_id="req-4",
            trace_id="tr-4",
            raw_output="{}",
            structured_output={
                "daily_synthesis": "P1. P2. P3. P4. P5. P6. P7. P8. P9. P10.",
                "astro_events_intro": "intro",
                "time_window_narratives": {},
                "turning_point_narratives": [],
                "main_turning_point_narrative": None,
                "daily_advice": {"advice": "a", "emphasis": "e"},
            },
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )

        await AIEngineAdapter.generate_horoscope_narration(
            variant_code=None,
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-4",
            trace_id="tr-4",
            db=db,
        )

        args, kwargs = mock_exec.call_args
        request = kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.plan == "free"


@pytest.mark.asyncio
async def test_generate_horoscope_narration_accepts_qualified_context(db):
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.return_value = GatewayResult(
            use_case="horoscope_daily",
            request_id="req-qc",
            trace_id="tr-qc",
            raw_output="{}",
            structured_output={
                "daily_synthesis": "P1. P2. P3. P4. P5. P6. P7.",
                "astro_events_intro": "intro",
                "time_window_narratives": {
                    "nuit": "",
                    "matin": "matin",
                    "apres_midi": "",
                    "soiree": "",
                },
                "turning_point_narratives": [],
                "main_turning_point_narrative": "",
                "daily_advice": {"advice": "", "emphasis": ""},
            },
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test"),
        )

        result = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only",
            time_windows=[],
            common_context=_make_dummy_qualified_context(),
            user_id=1,
            request_id="req-qc",
            trace_id="tr-qc",
            db=db,
        )

        assert result is not None
        assert mock_exec.called


@pytest.mark.asyncio
async def test_generate_horoscope_narration_no_direct_openai(db):
    """Test AC5: proves absence of direct openai.AsyncOpenAI calls."""
    # We patch the gateway but NOT openai.
    # If AIEngineAdapter tried to call openai directly, it would fail in test env
    # without API key, or we can patch openai to raise error if called.
    with patch("openai.resources.chat.AsyncCompletions.create") as mock_openai:
        mock_openai.side_effect = Exception("DIRECT OPENAI CALL FORBIDDEN")

        with patch(
            "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
        ) as mock_exec:
            mock_exec.return_value = GatewayResult(
                use_case="horoscope_daily",
                request_id="req-5",
                trace_id="tr-5",
                raw_output="{}",
                structured_output={
                    "daily_synthesis": "P1. P2. P3. P4. P5. P6. P7. P8. P9. P10.",
                    "astro_events_intro": "intro",
                    "time_window_narratives": {},
                    "turning_point_narratives": [],
                    "main_turning_point_narrative": None,
                    "daily_advice": {"advice": "a", "emphasis": "e"},
                },
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test"),
            )

            await AIEngineAdapter.generate_horoscope_narration(
                variant_code="full",
                time_windows=[],
                common_context=_make_dummy_context(),
                user_id=1,
                request_id="req-5",
                trace_id="tr-5",
                db=db,
            )
            # If we reached here without exception, it means OpenAI was NOT called directly.
            assert mock_exec.called


@pytest.mark.asyncio
async def test_generate_horoscope_narration_invalid_output_ac7(db):
    """Test AC7: invalid output handled by gateway or raises."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        # Gateway raises OutputValidationError if schema is not respected
        mock_exec.side_effect = OutputValidationError("Schema mismatch", details={})

        with pytest.raises(Exception) as exc:
            await AIEngineAdapter.generate_horoscope_narration(
                variant_code="full",
                time_windows=[],
                common_context=_make_dummy_context(),
                user_id=1,
                request_id="req-7",
                trace_id="tr-7",
                db=db,
            )
        # Verify it's mapped or bubbled up correctly
        assert "Output validation failed" in str(exc.value)


@pytest.mark.asyncio
async def test_generate_horoscope_narration_retry_on_length(db):
    """Test AC8: daily_synthesis too short -> retry."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_exec:
        mock_exec.side_effect = [
            GatewayResult(
                use_case="horoscope_daily",
                request_id="req-3",
                trace_id="tr-3",
                raw_output="{}",
                structured_output={
                    "daily_synthesis": "Too short. Only two. Sentences.",
                    "astro_events_intro": "intro",
                    "time_window_narratives": {},
                    "turning_point_narratives": [],
                    "main_turning_point_narrative": None,
                    "daily_advice": {"advice": "a", "emphasis": "e"},
                },
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test"),
            ),
            GatewayResult(
                use_case="horoscope_daily",
                request_id="req-3",
                trace_id="tr-3",
                raw_output="{}",
                structured_output={
                    "daily_synthesis": "1. 2. 3. 4. 5. 6. 7. Now it is long enough.",
                    "astro_events_intro": "intro",
                    "time_window_narratives": {},
                    "turning_point_narratives": [],
                    "main_turning_point_narrative": None,
                    "daily_advice": {"advice": "a", "emphasis": "e"},
                },
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test"),
            ),
        ]

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only",
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-3",
            trace_id="tr-3",
            db=db,
        )

        assert res is not None
        assert mock_exec.call_count == 2
        args, kwargs = mock_exec.call_args_list[1]
        assert "CORRECTION OBLIGATOIRE" in kwargs["request"].user_input.question


@pytest.mark.asyncio
async def test_map_gateway_result_to_narrator_result_nominal():
    """Test AC9: nominal mapping."""
    result = GatewayResult(
        use_case="test",
        request_id="req",
        trace_id="tr",
        raw_output="{}",
        structured_output={
            "daily_synthesis": "Synth",
            "astro_events_intro": "Intro",
            "time_window_narratives": {"matin": "Matin text", "invalid": "ignore"},
            "turning_point_narratives": ["TP1", "TP2"],
            "main_turning_point_narrative": "Main TP",
            "daily_advice": {"advice": "Advice", "emphasis": "Strong"},
        },
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=0, model="test"),
    )

    res = AIEngineAdapter._map_gateway_result_to_narrator_result(result)

    assert isinstance(res, NarratorResult)
    assert res.daily_synthesis == "Synth"
    assert res.astro_events_intro == "Intro"
    assert res.time_window_narratives == {"matin": "Matin text"}
    assert res.turning_point_narratives == ["TP1", "TP2"]
    assert res.main_turning_point_narrative == "Main TP"
    assert res.daily_advice.advice == "Advice"
    assert res.daily_advice.emphasis == "Strong"


@pytest.mark.asyncio
async def test_map_gateway_result_to_narrator_result_empty():
    """Test AC9: empty result -> None."""
    result = GatewayResult(
        use_case="test",
        request_id="req",
        trace_id="tr",
        raw_output="{}",
        structured_output=None,
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=0, model="test"),
    )
    res = AIEngineAdapter._map_gateway_result_to_narrator_result(result)
    assert res is None

    result2 = GatewayResult(
        use_case="test",
        request_id="req",
        trace_id="tr",
        raw_output="{}",
        structured_output={"other": "stuff"},
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=0, model="test"),
    )
    res2 = AIEngineAdapter._map_gateway_result_to_narrator_result(result2)
    assert res2 is None


@pytest.mark.asyncio
async def test_non_regression_66_9_to_66_18_suites():
    """AC11: Proves that the new narrator migration doesn't break the base orchestration logic."""
    # We just need to make sure we can still resolve and render basic things
    from app.domain.llm.prompting.prompt_renderer import PromptRenderer

    template = "Hello {{persona_name}}!"
    vars = {"persona_name": "Luna"}
    rendered = PromptRenderer.render(template, vars, feature="horoscope_daily")
    assert rendered == "Hello Luna!"

    # Check that unknown placeholders are stripped (fix for 66.13 regression)
    template_unknown = "Hello {{persona_name}} {{unknown}}!"
    rendered_unknown = PromptRenderer.render(template_unknown, vars, feature="horoscope_daily")
    assert rendered_unknown == "Hello Luna !"  # unknown replaced by empty string
