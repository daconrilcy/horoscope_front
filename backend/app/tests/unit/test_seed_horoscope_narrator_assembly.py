from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.domain.llm.prompting.narrator_contract import NARRATOR_OUTPUT_SCHEMA
from app.infra.db.models.llm_prompt import PromptStatus
from app.ops.llm.bootstrap.seed_horoscope_narrator_assembly import (
    _keep_latest_published_and_archive_rest,
)


@dataclass
class _FakePublishedRow:
    id: str
    published_at: datetime
    created_at: datetime
    status: PromptStatus = PromptStatus.PUBLISHED


def test_keep_latest_published_and_archive_rest_keeps_newest_row() -> None:
    db = MagicMock()
    oldest = _FakePublishedRow(
        id="old",
        created_at=datetime.now(UTC) - timedelta(days=2),
        published_at=datetime.now(UTC) - timedelta(days=2),
    )
    newest = _FakePublishedRow(
        id="new",
        created_at=datetime.now(UTC) - timedelta(days=1),
        published_at=datetime.now(UTC) - timedelta(days=1),
    )

    winner = _keep_latest_published_and_archive_rest(
        db,
        [oldest, newest],
        label="prompt:horoscope_daily",
    )

    assert winner is newest
    assert newest.status == PromptStatus.PUBLISHED
    assert oldest.status == PromptStatus.ARCHIVED
    db.flush.assert_called_once()


def test_narrator_output_schema_is_strictly_openai_compatible() -> None:
    time_windows = NARRATOR_OUTPUT_SCHEMA["properties"]["time_window_narratives"]
    assert time_windows["required"] == ["nuit", "matin", "apres_midi", "soiree"]
    assert set(time_windows["properties"]) == {"nuit", "matin", "apres_midi", "soiree"}
    assert time_windows["additionalProperties"] is False

    daily_advice = NARRATOR_OUTPUT_SCHEMA["properties"]["daily_advice"]
    assert daily_advice["type"] == "object"
    assert daily_advice["required"] == ["advice", "emphasis"]

    assert NARRATOR_OUTPUT_SCHEMA["properties"]["main_turning_point_narrative"]["type"] == "string"
