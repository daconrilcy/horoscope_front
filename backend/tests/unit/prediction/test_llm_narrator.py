import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import settings
from app.domain.llm.prompting.catalog import get_max_tokens
from app.domain.llm.prompting.context import PromptCommonContext
from app.prediction.llm_narrator import LLMNarrator


def _make_common_context() -> PromptCommonContext:
    return PromptCommonContext(
        precision_level="précision complète",
        astrologer_profile={"tonality": "bienveillant"},
        period_covered="journée",
        today_date="samedi 21 mars 2026",
        use_case_name="daily-prediction-narrator-v1",
        use_case_key="daily_prediction",
        natal_interpretation="Vous avancez mieux quand un cap clair se dégage.",
    )


@pytest.fixture(autouse=True)
def _mock_legacy_governance():
    with patch(
        "app.domain.llm.runtime.fallback_governance.FallbackGovernanceRegistry.track_fallback"
    ):
        yield


@pytest.mark.asyncio
async def test_narrate_success():
    narrator = LLMNarrator()

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

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(content)))]

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is not None
        assert res.daily_synthesis == "Synth"
        assert res.time_window_narratives["matin"] == "Matin text"
        assert res.main_turning_point_narrative == "Le pivot devient lisible."
        assert res.daily_advice is not None
        assert res.daily_advice.emphasis == "Le bon mot au bon moment."
        assert mock_client.chat.completions.create.await_args.kwargs["response_format"] == {
            "type": "json_object"
        }
        assert mock_client.chat.completions.create.await_args.kwargs[
            "max_completion_tokens"
        ] == get_max_tokens("horoscope_daily")


@pytest.mark.asyncio
async def test_narrate_failure_returns_none():
    narrator = LLMNarrator()

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI error"))

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is None


@pytest.mark.asyncio
async def test_narrate_timeout_returns_none():
    narrator = LLMNarrator()

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError())

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is None


@pytest.mark.asyncio
async def test_narrate_ignores_invalid_daily_advice_shape():
    narrator = LLMNarrator()

    content = {
        "daily_synthesis": "Synth",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"soiree": "Soiree"},
        "turning_point_narratives": [],
        "daily_advice": "not-an-object",
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(content)))]

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is not None
        assert res.daily_advice is None


@pytest.mark.asyncio
async def test_narrate_returns_none_on_truncated_json(caplog: pytest.LogCaptureFixture):
    narrator = LLMNarrator()

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            finish_reason="length",
            message=MagicMock(content='{"daily_synthesis":"Texte tronque'),
        )
    ]

    with (
        patch("openai.AsyncOpenAI") as mock_openai,
        patch("app.prediction.llm_narrator.logger.warning") as mock_warning,
    ):
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is None
        warning_message = mock_warning.call_args[0][0]
        assert "llm_narrator.invalid_json" in warning_message


@pytest.mark.asyncio
async def test_narrate_disabled_when_flag_off():
    """has_llm_narrative must be False when llm_narrator_enabled=False (assembler level)."""
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
async def test_narrate_retries_when_daily_synthesis_is_too_short():
    narrator = LLMNarrator()

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

    first_response = MagicMock()
    first_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(short_content)), finish_reason="stop")
    ]
    second_response = MagicMock()
    second_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(long_content)), finish_reason="stop")
    ]

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[first_response, second_response]
        )

        res = await narrator.narrate(time_windows=[], common_context=_make_common_context())

        assert res is not None
        assert narrator._count_sentences(res.daily_synthesis) == 10
        assert mock_client.chat.completions.create.await_count == 2


@pytest.mark.asyncio
async def test_narrate_summary_only_uses_shorter_target_and_free_token_budget():
    narrator = LLMNarrator()

    short_free_content = {
        "daily_synthesis": ("Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5. Phrase 6."),
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

    first_response = MagicMock()
    first_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(short_free_content)), finish_reason="stop")
    ]
    second_response = MagicMock()
    second_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(valid_free_content)), finish_reason="stop")
    ]

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[first_response, second_response]
        )

        res = await narrator.narrate(
            time_windows=[],
            common_context=_make_common_context(),
            variant_code="summary_only",
        )

        assert res is not None
        assert narrator._count_sentences(res.daily_synthesis) == 7
        assert mock_client.chat.completions.create.await_count == 2
        second_messages = mock_client.chat.completions.create.await_args_list[1].kwargs["messages"]
        second_prompt = second_messages[1]["content"]
        assert "7 à 8 phrases" in second_prompt
        assert (
            mock_client.chat.completions.create.await_args_list[0].kwargs["max_completion_tokens"]
            == 3000
        )
