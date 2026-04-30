"""Couvre la narration LLM de prediction via l'adaptateur canonique."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import settings
from app.domain.llm.prompting.context import PromptCommonContext
from app.domain.llm.runtime.adapter import AIEngineAdapter
from app.domain.llm.runtime.adapter_errors import AIEngineAdapterError
from app.domain.llm.runtime.contracts import (
    GatewayError,
    GatewayMeta,
    GatewayResult,
    OutputValidationError,
    UsageInfo,
)


def _make_common_context() -> PromptCommonContext:
    """Construit un contexte minimal reutilisable pour la narration horoscope."""
    return PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="samedi 21 mars 2026",
        use_case_name="daily-prediction-narrator-v1",
        use_case_key="daily_prediction",
        natal_interpretation="Vous avancez mieux quand un cap clair se dégage.",
    )


def _gateway_result(payload: dict) -> GatewayResult:
    """Fabrique une reponse gateway structuree pour les tests d'adaptateur."""
    return GatewayResult(
        use_case="horoscope_daily",
        request_id="req-narration",
        trace_id="trace-narration",
        raw_output="{}",
        structured_output=payload,
        usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20),
        meta=GatewayMeta(latency_ms=1, model="test-model"),
    )


def _count_sentences(text: str) -> int:
    """Compte les phrases comme la couche de narration canonique."""
    if not text:
        return 0
    return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()])


@pytest.mark.asyncio
async def test_generate_horoscope_narration_success_maps_gateway_result():
    """La narration nominale passe par le gateway et mappe les champs attendus."""
    content = {
        "daily_synthesis": "Synth",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
        "main_turning_point_narrative": "Le pivot devient lisible.",
        "daily_advice": {
            "advice": "Profitez du matin pour clarifier un échange important.",
            "emphasis": "Le bon mot au bon moment.",
        },
    }

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = _gateway_result(content)

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code=None,
            time_windows=[],
            common_context=_make_common_context(),
            user_id=1,
            request_id="req-narration",
            trace_id="trace-narration",
            db=MagicMock(),
        )

        assert res is not None
        assert res.daily_synthesis == "Synth"
        assert res.time_window_narratives["matin"] == "Matin text"
        assert res.main_turning_point_narrative == "Le pivot devient lisible."
        assert res.daily_advice is not None
        assert res.daily_advice.emphasis == "Le bon mot au bon moment."
        request = mock_execute.await_args.kwargs["request"]
        assert request.user_input.feature == "horoscope_daily"
        assert request.user_input.subfeature == "narration"
        assert request.user_input.plan == "free"


@pytest.mark.asyncio
async def test_generate_horoscope_narration_gateway_failure_raises_stable_error():
    """Une erreur gateway ne retombe pas sur une facade legacy silencieuse."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = GatewayError("OpenAI error")

        with pytest.raises(ConnectionError, match="llm provider unavailable"):
            await AIEngineAdapter.generate_horoscope_narration(
                variant_code=None,
                time_windows=[],
                common_context=_make_common_context(),
                user_id=1,
                request_id="req-failure",
                trace_id="trace-failure",
                db=MagicMock(),
            )


@pytest.mark.asyncio
async def test_generate_horoscope_narration_timeout_maps_to_adapter_error():
    """Le timeout gateway est expose par l'erreur stable de l'adaptateur."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = GatewayError("timeout", details={"kind": "timeout"})

        with pytest.raises(AIEngineAdapterError) as exc:
            await AIEngineAdapter.generate_horoscope_narration(
                variant_code=None,
                time_windows=[],
                common_context=_make_common_context(),
                user_id=1,
                request_id="req-timeout",
                trace_id="trace-timeout",
                db=MagicMock(),
            )

        assert exc.value.code == "upstream_timeout"


@pytest.mark.asyncio
async def test_generate_horoscope_narration_ignores_invalid_daily_advice_shape():
    """Un conseil quotidien invalide ne casse pas le mapping narratif."""
    content = {
        "daily_synthesis": "Synth",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"soiree": "Soiree"},
        "turning_point_narratives": [],
        "daily_advice": "not-an-object",
    }

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.return_value = _gateway_result(content)

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code=None,
            time_windows=[],
            common_context=_make_common_context(),
            user_id=1,
            request_id="req-advice",
            trace_id="trace-advice",
            db=MagicMock(),
        )

        assert res is not None
        assert res.daily_advice is None


@pytest.mark.asyncio
async def test_generate_horoscope_narration_invalid_output_raises_adapter_error():
    """Une sortie invalide reste une erreur gateway classifiee."""
    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = OutputValidationError("Schema mismatch", details={})

        with pytest.raises(AIEngineAdapterError) as exc:
            await AIEngineAdapter.generate_horoscope_narration(
                variant_code=None,
                time_windows=[],
                common_context=_make_common_context(),
                user_id=1,
                request_id="req-invalid-json",
                trace_id="trace-invalid-json",
                db=MagicMock(),
            )

        assert exc.value.code == "invalid_horoscope_daily_output"


@pytest.mark.asyncio
async def test_narration_disabled_when_flag_off():
    """Le flag coupe toujours la narration au niveau assembleur."""
    from datetime import UTC, date, datetime

    from app.prediction.public_projection import PublicPredictionAssembler

    snapshot = MagicMock()
    snapshot.local_date = date(2026, 3, 20)
    snapshot.timezone = "Europe/Paris"
    snapshot.computed_at = datetime.now(UTC)
    snapshot.is_provisional_calibration = False
    snapshot.calibration_label = "final"
    snapshot.house_system_effective = "placidus"
    snapshot.category_scores = []
    snapshot.time_blocks = []
    snapshot.relative_scores = {}
    snapshot.overall_tone = "neutral"
    snapshot.overall_summary = "test"
    snapshot.v3_metrics = {}
    snapshot.reference_version_id = 1
    snapshot.ruleset_id = 1
    snapshot.user_id = 1

    original = settings.llm_narrator_enabled
    try:
        settings.llm_narrator_enabled = False
        result = await PublicPredictionAssembler().assemble(
            snapshot,
            {},
            reference_version="2.0.0",
            ruleset_version="2.0.0",
        )
        assert result["has_llm_narrative"] is False
    finally:
        settings.llm_narrator_enabled = original


@pytest.mark.asyncio
async def test_generate_horoscope_narration_retries_when_synthesis_is_too_short():
    """Une synthese trop courte declenche une seconde requete canonique."""
    short_content = {
        "daily_synthesis": "Première phrase. Deuxième phrase. Troisième phrase.",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
        "main_turning_point_narrative": "Pivot.",
        "daily_advice": {"advice": "Conseil", "emphasis": "Emphase"},
    }
    long_content = {
        "daily_synthesis": (
            "Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5. "
            "Phrase 6. Phrase 7. Phrase 8. Phrase 9. Phrase 10."
        ),
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
        "main_turning_point_narrative": "Pivot.",
        "daily_advice": {"advice": "Conseil", "emphasis": "Emphase"},
    }

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = [_gateway_result(short_content), _gateway_result(long_content)]

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="full",
            time_windows=[],
            common_context=_make_common_context(),
            user_id=1,
            request_id="req-retry",
            trace_id="trace-retry",
            db=MagicMock(),
        )

        assert res is not None
        assert _count_sentences(res.daily_synthesis) == 10
        assert mock_execute.await_count == 2
        second_question = mock_execute.await_args_list[1].kwargs["request"].user_input.question
        assert "au moins 10 phrases" in second_question


@pytest.mark.asyncio
async def test_generate_horoscope_narration_summary_only_uses_free_plan_and_shorter_target():
    """La variante courte utilise le plan free et le seuil de sept phrases."""
    short_free_content = {
        "daily_synthesis": "Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5. Phrase 6.",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
        "main_turning_point_narrative": "Pivot.",
        "daily_advice": {"advice": "Conseil", "emphasis": "Emphase"},
    }
    valid_free_content = {
        "daily_synthesis": (
            "Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5. Phrase 6. Phrase 7."
        ),
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
        "main_turning_point_narrative": "Pivot.",
        "daily_advice": {"advice": "Conseil", "emphasis": "Emphase"},
    }

    with patch(
        "app.domain.llm.runtime.gateway.LLMGateway.execute_request", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = [
            _gateway_result(short_free_content),
            _gateway_result(valid_free_content),
        ]

        res = await AIEngineAdapter.generate_horoscope_narration(
            variant_code="summary_only",
            time_windows=[],
            common_context=_make_common_context(),
            user_id=1,
            request_id="req-summary",
            trace_id="trace-summary",
            db=MagicMock(),
        )

        assert res is not None
        assert _count_sentences(res.daily_synthesis) == 7
        assert mock_execute.await_count == 2
        first_request = mock_execute.await_args_list[0].kwargs["request"]
        second_question = mock_execute.await_args_list[1].kwargs["request"].user_input.question
        assert first_request.user_input.plan == "free"
        assert "au moins 7 phrases" in second_question
