from __future__ import annotations

import json
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.persisted_snapshot import (
    PersistedPredictionSnapshot,
    PersistedCategoryScore,
    PersistedTimeBlock,
    PersistedTurningPoint,
)
from app.prediction.public_projection import (
    PublicPredictionAssembler,
    PublicCategoryPolicy,
    PublicDecisionWindowPolicy,
    PublicTurningPointPolicy,
    PublicTimelinePolicy,
    PublicSummaryPolicy,
)


@pytest.fixture
def cat_map():
    return {1: "love", 2: "work", 3: "health"}


@pytest.fixture
def sample_snapshot():
    return PersistedPredictionSnapshot(
        run_id=1,
        user_id=1,
        local_date=date(2026, 3, 10),
        timezone="Europe/Paris",
        computed_at=datetime(2026, 3, 10, 10, 0),
        input_hash="hash123",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="v1",
        overall_summary="Great day ahead",
        overall_tone="positive",
        category_scores=[
            PersistedCategoryScore(
                category_id=1,
                category_code="love",
                note_20=15,
                raw_score=0.8,
                power=0.7,
                volatility=0.2,
                rank=1,
                is_provisional=False,
                summary="Love is great",
            ),
            PersistedCategoryScore(
                category_id=2,
                category_code="work",
                note_20=12,
                raw_score=0.6,
                power=0.5,
                volatility=0.3,
                rank=2,
                is_provisional=False,
                summary="Work is ok",
            ),
        ],
        time_blocks=[
            PersistedTimeBlock(
                block_index=0,
                start_at_local=datetime(2026, 3, 10, 8, 0),
                end_at_local=datetime(2026, 3, 10, 10, 0),
                tone_code="positive",
                dominant_categories=["love"],
                summary=None,
            )
        ],
        turning_points=[
            PersistedTurningPoint(
                occurred_at_local=datetime(2026, 3, 10, 9, 0),
                severity=0.9,
                summary="Major shift",
                drivers=[{"code": "sun_trine_jupiter"}],
            )
        ],
    )


def test_category_policy(cat_map, sample_snapshot):
    policy = PublicCategoryPolicy()
    categories = policy.build(sample_snapshot, cat_map)
    
    assert len(categories) == 2
    assert categories[0]["code"] == "love"
    assert categories[0]["note_20"] == 15
    assert categories[1]["code"] == "work"


def test_decision_window_policy_normalization(cat_map, sample_snapshot):
    policy = PublicDecisionWindowPolicy()
    category_notes = {"love": 15.0, "work": 12.0}
    
    # Simulate rebuild return
    with pytest.MonkeyPatch.context() as mp:
        mock_rebuild = MagicMock(return_value=[
            {
                "start_local": "2026-03-10T08:00:00",
                "end_local": "2026-03-10T10:00:00",
                "window_type": "favorable",
                "score": 0.8,
                "confidence": 0.9,
                "dominant_categories": ["love"],
            }
        ])
        # Note: In the refactored code, the method name is _rebuild_from_snapshot
        mp.setattr(policy, "_rebuild_from_snapshot", mock_rebuild)
        
        windows = policy.build(sample_snapshot, cat_map, category_notes)
        assert len(windows) == 1
        assert windows[0]["dominant_categories"] == ["love"]


def test_turning_point_policy_no_windows(sample_snapshot):
    policy = PublicTurningPointPolicy()
    tps = policy.build(sample_snapshot, decision_windows=[])
    
    assert len(tps) == 1
    assert tps[0]["severity"] == 0.9
    assert tps[0]["drivers"][0]["code"] == "sun_trine_jupiter"


def test_timeline_policy(sample_snapshot):
    policy = PublicTimelinePolicy()
    cat_notes = {"love": 15.0}
    tp_times = [datetime(2026, 3, 10, 9, 0)]
    
    timeline = policy.build(sample_snapshot, cat_notes, tp_times)
    
    assert len(timeline) == 1
    assert timeline[0]["turning_point"] is True
    assert "tonalité très porteuse" in timeline[0]["summary"]


def test_assembler_integration(cat_map, sample_snapshot):
    assembler = PublicPredictionAssembler()
    
    result = assembler.assemble(
        snapshot=sample_snapshot,
        cat_id_to_code=cat_map,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        was_reused=False,
    )
    
    assert result["meta"]["date_local"] == "2026-03-10"
    assert result["meta"]["calibration_label"] == "v1"
    assert "summary" in result
    assert len(result["categories"]) == 2
    assert len(result["turning_points"]) >= 1


def test_assembler_falls_back_to_engine_output_house_system(cat_map, sample_snapshot):
    assembler = PublicPredictionAssembler()
    
    # Snapshot without house system
    snapshot_no_house = PersistedPredictionSnapshot(
        **{**sample_snapshot.__dict__, "house_system_effective": None}
    )
    
    engine_output = MagicMock()
    engine_output.core.effective_context.house_system_effective = "placidus"

    result = assembler.assemble(
        snapshot=snapshot_no_house,
        cat_id_to_code=cat_map,
        engine_output=engine_output,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        was_reused=False,
    )
    
    assert result["meta"]["house_system_effective"] == "placidus"


def test_assembler_summary_uses_provisional_flag(cat_map, sample_snapshot):
    assembler = PublicPredictionAssembler()
    
    snapshot_prov = PersistedPredictionSnapshot(
        **{**sample_snapshot.__dict__, "is_provisional_calibration": True}
    )

    result = assembler.assemble(
        snapshot=snapshot_prov,
        cat_id_to_code=cat_map,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        was_reused=False,
    )
    
    assert "scores sont calculés sans données historiques" in result["summary"]["calibration_note"]
