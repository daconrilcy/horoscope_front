from dataclasses import asdict
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.prediction.llm_narrator import NarratorResult
from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
    PersistedTimeBlock,
)
from app.prediction.public_projection import PublicPredictionAssembler
from app.prediction.schemas import (
    V3EvidencePack,
    V3EvidenceTheme,
    V3EvidenceTurningPoint,
    V3EvidenceWindow,
)


def _json_ready(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value


@pytest.mark.asyncio
async def test_assemble_uses_evidence_pack():
    # Setup mock evidence pack
    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={
            "tone": "positive",
            "avg_intensity": 15.0,
            "overall_summary": "Summary from evidence",
        },
        themes={
            "love": V3EvidenceTheme(
                code="love",
                score_20=18.0,
                level=1.5,
                intensity=18.0,
                dominance=10.0,
                stability=15.0,
                rarity=12.0,
                is_major=True,
            )
        },
        time_windows=[
            V3EvidenceWindow(
                start_local=datetime(2026, 3, 7, 10, 0),
                end_local=datetime(2026, 3, 7, 12, 0),
                type="favorable",
                score=18.0,
                intensity=15.0,
                confidence=0.9,
                themes=["love"],
            )
        ],
        turning_points=[
            V3EvidenceTurningPoint(
                local_time=datetime(2026, 3, 7, 10, 0),
                reason="regime_change",
                amplitude=5.0,
                confidence=0.8,
                themes=["love"],
                drivers=["Venus-trine-Mars"],
            )
        ],
    )

    v3_output = MagicMock()
    v3_output.v3_core = MagicMock()
    v3_output.v3_core.evidence_pack = evidence_pack
    v3_output.core = MagicMock()

    # Mock snapshot
    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.local_date = date(2026, 3, 7)
    snapshot.timezone = "UTC"
    snapshot.computed_at = datetime.now(UTC)
    snapshot.is_provisional_calibration = False
    snapshot.calibration_label = "final"
    snapshot.category_scores = []
    snapshot.time_blocks = []
    snapshot.house_system_effective = "placidus"
    snapshot.reference_version_id = 1
    snapshot.ruleset_id = 1
    snapshot.user_id = 42
    snapshot.relative_scores = {}
    snapshot.overall_tone = "neutral"
    snapshot.overall_summary = "Old summary"

    assembler = PublicPredictionAssembler()
    cat_id_to_code = {1: "love"}

    result = await assembler.assemble(
        snapshot,
        cat_id_to_code,
        engine_output=v3_output,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    # Check that summary comes from evidence pack
    assert result["summary"]["overall_summary"] == "Summary from evidence"

    # Check category derived from evidence
    love_cat = next(c for c in result["categories"] if c["code"] == "love")
    assert love_cat["score_20"] == 18.0

    # This test exercises the public assembler path only.


@pytest.mark.asyncio
async def test_assemble_uses_persisted_evidence_pack_snapshot():
    evidence_pack = V3EvidencePack(
        version="3.1.0",
        generated_at=datetime(2026, 3, 7, 6, 0, tzinfo=UTC),
        day_profile={"overall_tone": "positive", "overall_summary": "Persisted evidence summary"},
        themes={
            "work": V3EvidenceTheme(
                code="work",
                score_20=16.0,
                level=0.8,
                intensity=14.0,
                dominance=6.0,
                stability=15.0,
                rarity=8.0,
                is_major=True,
            )
        },
        time_windows=[
            V3EvidenceWindow(
                start_local=datetime(2026, 3, 7, 9, 0),
                end_local=datetime(2026, 3, 7, 11, 0),
                type="favorable",
                score=16.0,
                intensity=14.0,
                confidence=0.85,
                themes=["work"],
            )
        ],
        turning_points=[],
    )

    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=42,
        local_date=date(2026, 3, 7),
        timezone="UTC",
        computed_at=datetime(2026, 3, 7, 7, 0, tzinfo=UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="final",
        overall_summary="legacy summary",
        overall_tone="neutral",
        v3_metrics={"evidence_pack": _json_ready(asdict(evidence_pack))},
        category_scores=[
            PersistedCategoryScore(
                category_id=1,
                category_code="work",
                note_20=16,
                raw_score=0.8,
                power=0.7,
                volatility=0.25,
                rank=1,
                is_provisional=False,
                summary=None,
            )
        ],
    )

    result = await PublicPredictionAssembler().assemble(
        snapshot,
        {1: "work"},
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    assert result["summary"]["overall_summary"] == "Persisted evidence summary"
    assert result["decision_windows"][0]["window_type"] == "favorable"
    assert result["categories"][0]["code"] == "work"


@pytest.mark.asyncio
async def test_assemble_reuses_persisted_llm_narrative_without_regeneration():
    snapshot = PersistedPredictionSnapshot(
        run_id=7,
        user_id=42,
        local_date=date(2026, 3, 7),
        timezone="UTC",
        computed_at=datetime(2026, 3, 7, 7, 0, tzinfo=UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="final",
        overall_summary="legacy summary",
        overall_tone="neutral",
        llm_narrative={
            "daily_synthesis": "Synthèse persistée",
            "astro_events_intro": "Intro persistée",
            "time_window_narratives": {"matin": "Narration matin persistée"},
            "turning_point_narratives": ["Turning point persistant"],
            "main_turning_point_narrative": "Narration pivot principal persistée",
            "daily_advice": {"advice": "Conseil persistant", "emphasis": "Emphase persistée"},
        },
        category_scores=[
            PersistedCategoryScore(
                category_id=1,
                category_code="work",
                note_20=16,
                raw_score=0.8,
                power=0.7,
                volatility=0.25,
                rank=1,
                is_provisional=False,
                summary=None,
            )
        ],
        turning_points=[],
        time_blocks=[],
    )

    prompt_context = MagicMock()

    with patch(
        "app.application.llm.ai_engine_adapter.AIEngineAdapter.generate_horoscope_narration",
        new_callable=AsyncMock,
    ) as mock_gen:
        result = await PublicPredictionAssembler().assemble(
            snapshot,
            {1: "work"},
            reference_version="2.0.0",
            ruleset_version="2.0.0",
            prompt_context=prompt_context,
        )

    mock_gen.assert_not_awaited()
    assert result["has_llm_narrative"] is True
    assert result["daily_synthesis"] == "Synthèse persistée"
    assert result["astro_events_intro"] == "Intro persistée"
    assert result["daily_advice"]["advice"] == "Conseil persistant"


@pytest.mark.asyncio
async def test_assemble_regenerates_when_persisted_free_narrative_is_too_short():
    snapshot = PersistedPredictionSnapshot(
        run_id=8,
        user_id=42,
        local_date=date(2026, 3, 7),
        timezone="UTC",
        computed_at=datetime(2026, 3, 7, 7, 0, tzinfo=UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="final",
        overall_summary="legacy summary",
        overall_tone="neutral",
        llm_narrative={
            "daily_synthesis": "Journée calme et sereine, focus sur relations et échanges.",
            "astro_events_intro": "Intro persistée",
        },
        category_scores=[
            PersistedCategoryScore(
                category_id=1,
                category_code="work",
                note_20=16,
                raw_score=0.8,
                power=0.7,
                volatility=0.25,
                rank=1,
                is_provisional=False,
                summary=None,
            )
        ],
        turning_points=[],
        time_blocks=[],
    )

    prompt_context = MagicMock()
    regenerated = NarratorResult(
        daily_synthesis="Phrase 1. Phrase 2. Phrase 3. Phrase 4. Phrase 5. Phrase 6. Phrase 7.",
        astro_events_intro="Nouvelle intro",
        time_window_narratives={},
        turning_point_narratives=[],
    )

    with (
        patch(
            "app.application.llm.ai_engine_adapter.AIEngineAdapter.generate_horoscope_narration",
            new_callable=AsyncMock,
            return_value=regenerated,
        ) as mock_gen,
        patch("app.prediction.public_projection.settings") as mock_settings,
    ):
        mock_settings.llm_narrator_enabled = True
        result = await PublicPredictionAssembler().assemble(
            snapshot,
            {1: "work"},
            reference_version="2.0.0",
            ruleset_version="2.0.0",
            prompt_context=prompt_context,
            variant_code="summary_only",
        )

    mock_gen.assert_awaited_once()
    assert result["has_llm_narrative"] is True
    assert result["daily_synthesis"] == regenerated.daily_synthesis
    assert result["astro_events_intro"] == "Nouvelle intro"


@pytest.mark.asyncio
async def test_assemble_includes_enriched_turning_points():
    from app.prediction.schemas import V3PrimaryDriver

    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={"tone": "neutral"},
        themes={"love": V3EvidenceTheme("love", 15.0, 1.0, 10.0, 5.0, 15.0, 10.0, True)},
        time_windows=[],
        turning_points=[
            V3EvidenceTurningPoint(
                local_time=datetime(2026, 3, 7, 10, 0),
                reason="regime_change",
                amplitude=5.0,
                confidence=0.8,
                themes=["love"],
                drivers=["Sun-conjunction-Moon"],
                change_type="emergence",
                previous_categories=["work"],
                next_categories=["love"],
                primary_driver=V3PrimaryDriver(
                    "aspect_exact_to_personal",
                    "Sun",
                    "Moon",
                    "conjunction",
                    0.12,
                    "applying",
                    68,
                    1.5,
                    {"house": 5},
                ),
            )
        ],
    )

    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.local_date = date(2026, 3, 7)
    snapshot.timezone = "UTC"
    snapshot.computed_at = datetime.now(UTC)
    snapshot.is_provisional_calibration = False
    snapshot.calibration_label = "final"
    snapshot.house_system_effective = "placidus"
    snapshot.category_scores = []
    snapshot.time_blocks = []
    snapshot.relative_scores = {}
    snapshot.overall_tone = "neutral"
    snapshot.overall_summary = "Summary"
    snapshot.v3_metrics = {"evidence_pack": _json_ready(asdict(evidence_pack))}

    assembler = PublicPredictionAssembler()
    result = await assembler.assemble(
        snapshot,
        {1: "love"},
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    tp = result["turning_points"][0]
    assert tp["change_type"] == "emergence"
    assert tp["previous_categories"] == ["work"]
    assert tp["next_categories"] == ["love"]
    assert tp["primary_driver"]["event_type"] == "aspect_exact_to_personal"
    assert tp["primary_driver"]["orb_deg"] == 0.12
    assert tp["primary_driver"]["phase"] == "applying"
    assert tp["primary_driver"]["metadata"]["house"] == 5


@pytest.mark.asyncio
async def test_assemble_includes_movement_indicators():
    from app.prediction.schemas import V3CategoryDelta, V3Movement

    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={"tone": "neutral"},
        themes={"love": V3EvidenceTheme("love", 15.0, 1.0, 10.0, 5.0, 15.0, 10.0, True)},
        time_windows=[],
        turning_points=[
            V3EvidenceTurningPoint(
                local_time=datetime(2026, 3, 7, 10, 0),
                reason="regime_change",
                amplitude=5.0,
                confidence=0.8,
                themes=["love"],
                drivers=["Sun-conjunction-Moon"],
                movement=V3Movement(
                    strength=7.5,
                    previous_composite=5.0,
                    next_composite=12.5,
                    delta_composite=7.5,
                    direction="rising",
                ),
                category_deltas=[
                    V3CategoryDelta(
                        code="love",
                        direction="up",
                        delta_score=2.0,
                        delta_intensity=5.0,
                        delta_rank=1,
                    )
                ],
            )
        ],
    )

    snapshot = MagicMock(spec=PersistedPredictionSnapshot)
    snapshot.local_date = date(2026, 3, 7)
    snapshot.timezone = "UTC"
    snapshot.computed_at = datetime.now(UTC)
    snapshot.is_provisional_calibration = False
    snapshot.calibration_label = "final"
    snapshot.house_system_effective = "placidus"
    snapshot.category_scores = []
    snapshot.time_blocks = []
    snapshot.relative_scores = {}
    snapshot.overall_tone = "neutral"
    snapshot.overall_summary = "Summary"
    snapshot.v3_metrics = {"evidence_pack": _json_ready(asdict(evidence_pack))}

    assembler = PublicPredictionAssembler()
    result = await assembler.assemble(
        snapshot,
        {1: "love"},
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    tp = result["turning_points"][0]
    assert tp["movement"]["strength"] == 7.5
    assert tp["movement"]["direction"] == "rising"
    assert tp["category_deltas"][0]["code"] == "love"
    assert tp["category_deltas"][0]["direction"] == "up"
    assert tp["category_deltas"][0]["delta_score"] == 2.0


@pytest.mark.asyncio
async def test_assemble_keeps_evidence_turning_points_even_on_flat_day():
    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={"tone": "neutral"},
        themes={
            "health": V3EvidenceTheme("health", 12.0, 0.2, 2.0, 4.0, 15.0, 3.0, False),
            "work": V3EvidenceTheme("work", 11.5, 0.1, 1.8, 3.0, 15.0, 2.5, False),
        },
        time_windows=[],
        turning_points=[
            V3EvidenceTurningPoint(
                local_time=datetime(2026, 3, 12, 8, 45),
                reason="regime_change",
                amplitude=3.2,
                confidence=0.75,
                themes=["health", "work"],
                drivers=["Moon-sextile-Mars"],
            )
        ],
    )

    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=42,
        local_date=date(2026, 3, 12),
        timezone="Europe/Paris",
        computed_at=datetime.now(UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=True,
        calibration_label="provisional",
        overall_summary="Calm day",
        overall_tone="neutral",
        v3_metrics={"evidence_pack": _json_ready(asdict(evidence_pack))},
        category_scores=[
            PersistedCategoryScore(1, "health", 12, 0.0, 0.0, 0.0, 1, True, None),
            PersistedCategoryScore(2, "work", 11, 0.0, 0.0, 0.0, 2, True, None),
        ],
        time_blocks=[
            PersistedTimeBlock(
                block_index=0,
                start_at_local=datetime(2026, 3, 12, 0, 0),
                end_at_local=datetime(2026, 3, 12, 23, 45),
                tone_code="neutral",
                dominant_categories=["health", "work"],
                summary=None,
            )
        ],
    )

    result = await PublicPredictionAssembler().assemble(
        snapshot,
        {1: "health", 2: "work"},
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    assert result["summary"]["flat_day"] is True
    assert len(result["turning_points"]) == 1
    assert result["turning_points"][0]["drivers"][0]["label"] == "Moon-sextile-Mars"
