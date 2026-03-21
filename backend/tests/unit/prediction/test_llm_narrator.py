import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import settings
from app.prediction.llm_narrator import LLMNarrator


@pytest.mark.asyncio
async def test_narrate_success():
    narrator = LLMNarrator()

    content = {
        "daily_synthesis": "Synth",
        "astro_events_intro": "Intro",
        "time_window_narratives": {"matin": "Matin text"},
        "turning_point_narratives": ["TP1"],
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(content)))]

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        res = await narrator.narrate(time_windows=[], common_context=MagicMock())

        assert res is not None
        assert res.daily_synthesis == "Synth"
        assert res.time_window_narratives["matin"] == "Matin text"


@pytest.mark.asyncio
async def test_narrate_failure_returns_none():
    narrator = LLMNarrator()

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI error"))

        res = await narrator.narrate(time_windows=[], common_context=MagicMock())
        assert res is None


@pytest.mark.asyncio
async def test_narrate_timeout_returns_none():
    narrator = LLMNarrator()

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError())

        res = await narrator.narrate(time_windows=[], common_context=MagicMock())
        assert res is None


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
