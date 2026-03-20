import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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

        res = await narrator.narrate([], [], MagicMock(), "standard", "fr")

        assert res is not None
        assert res.daily_synthesis == "Synth"
        assert res.time_window_narratives["matin"] == "Matin text"


@pytest.mark.asyncio
async def test_narrate_failure_returns_none():
    narrator = LLMNarrator()

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI error"))

        res = await narrator.narrate([], [], MagicMock(), "standard", "fr")
        assert res is None
