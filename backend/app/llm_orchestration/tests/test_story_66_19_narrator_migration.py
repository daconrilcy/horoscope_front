from unittest.mock import AsyncMock, patch

import pytest

from app.llm_orchestration.models import GatewayMeta, GatewayResult, UsageInfo
from app.prediction.llm_narrator import NarratorResult
from app.prompts.common_context import PromptCommonContext
from app.services.ai_engine_adapter import AIEngineAdapter


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
        use_case_key="daily_prediction"
    )

@pytest.mark.asyncio
async def test_generate_horoscope_narration_routing_free(db):
    """Test AC2: variant_code='summary_only' -> horoscope_daily/free."""
    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", 
        new_callable=AsyncMock
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
                "daily_advice": {"advice": "a", "emphasis": "e"}
            },
            usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20),
            meta=GatewayMeta(latency_ms=100, model="gpt-4o")
        )

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only",
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-1",
            trace_id="tr-1",
            db=db
        )

        assert res is not None
        assert res.daily_synthesis.startswith("Phrase 1")
        
        # Verify call arguments
        args, kwargs = mock_exec.call_args
        request = kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.plan == "free"

@pytest.mark.asyncio
async def test_generate_horoscope_narration_routing_premium(db):
    """Test AC3: variant_code='full' -> horoscope_daily/premium."""
    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", 
        new_callable=AsyncMock
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
                "daily_advice": {"advice": "a", "emphasis": "e"}
            },
            usage=UsageInfo(),
            meta=GatewayMeta(latency_ms=0, model="test")
        )

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="full",
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-2",
            trace_id="tr-2",
            db=db
        )

        assert res is not None
        args, kwargs = mock_exec.call_args
        request = kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.plan == "premium"

@pytest.mark.asyncio
async def test_generate_horoscope_narration_retry_on_length(db):
    """Test AC8: daily_synthesis too short -> retry."""
    with patch(
        "app.llm_orchestration.gateway.LLMGateway.execute_request", 
        new_callable=AsyncMock
    ) as mock_exec:
        # First call: too short (3 sentences)
        # Second call: long enough (7 sentences)
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
                    "daily_advice": {"advice": "a", "emphasis": "e"}
                },
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test")
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
                    "daily_advice": {"advice": "a", "emphasis": "e"}
                },
                usage=UsageInfo(),
                meta=GatewayMeta(latency_ms=0, model="test")
            )
        ]

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only", # plan free -> 7 sentences
            time_windows=[],
            common_context=_make_dummy_context(),
            user_id=1,
            request_id="req-3",
            trace_id="tr-3",
            db=db
        )

        assert res is not None
        assert mock_exec.call_count == 2
        
        # Verify second call had correction instruction
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
            "daily_advice": {"advice": "Advice", "emphasis": "Strong"}
        },
        usage=UsageInfo(),
        meta=GatewayMeta(latency_ms=0, model="test")
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
        meta=GatewayMeta(latency_ms=0, model="test")
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
        meta=GatewayMeta(latency_ms=0, model="test")
    )
    res2 = AIEngineAdapter._map_gateway_result_to_narrator_result(result2)
    assert res2 is None
