from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.public_projection import (
    PublicCategoryPolicy,
    PublicDecisionWindowPolicy,
    PublicPredictionAssembler,
    PublicTimelinePolicy,
    PublicTurningPointPolicy,
)


@pytest.fixture
def cat_map():
    return {1: "love", 2: "work", 3: "health"}


@pytest.fixture
def sample_full_run():
    return {
        "local_date": "2026-03-10",
        "timezone": "Europe/Paris",
        "computed_at": "2026-03-10T10:00:00",
        "category_scores": [
            {
                "category_id": 1,
                "note_20": 15.0,
                "rank": 1,
                "raw_score": 0.8,
                "power": 0.7,
                "volatility": 0.2,
                "summary": "Love is great",
            },
            {
                "category_id": 2,
                "note_20": 12.0,
                "rank": 2,
                "raw_score": 0.6,
                "power": 0.5,
                "volatility": 0.3,
                "summary": "Work is ok",
            },
        ],
        "time_blocks": [
            {
                "start_at_local": "2026-03-10T08:00:00",
                "end_at_local": "2026-03-10T10:00:00",
                "tone_code": "positive",
                "dominant_categories_json": json.dumps(["love"]),
            }
        ],
        "turning_points": [
            {
                "occurred_at_local": "2026-03-10T09:00:00",
                "severity": 0.9,
                "summary": "Major shift",
                "driver_json": json.dumps([{"code": "sun_trine_jupiter"}]),
            }
        ],
        "overall_tone": "positive",
        "overall_summary": "Great day ahead",
    }


def test_category_policy(cat_map, sample_full_run):
    policy = PublicCategoryPolicy()
    categories = policy.build(sample_full_run, cat_map)
    
    assert len(categories) == 2
    assert categories[0]["code"] == "love"
    assert categories[0]["note_20"] == 15.0
    assert categories[1]["code"] == "work"


def test_decision_window_policy_normalization(cat_map, sample_full_run):
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
        mp.setattr(policy, "_rebuild_from_persistence", mock_rebuild)
        
        windows = policy.build(sample_full_run, cat_map, category_notes)
        assert len(windows) == 1
        assert windows[0]["dominant_categories"] == ["love"]


def test_turning_point_policy_no_windows(sample_full_run):
    policy = PublicTurningPointPolicy()
    tps = policy.build(sample_full_run, decision_windows=[])
    
    assert len(tps) == 1
    assert tps[0]["severity"] == 0.9
    assert tps[0]["drivers"][0]["code"] == "sun_trine_jupiter"


def test_timeline_policy(sample_full_run):
    policy = PublicTimelinePolicy()
    cat_notes = {"love": 15.0}
    tp_times = [datetime.fromisoformat("2026-03-10T09:00:00")]
    
    timeline = policy.build(sample_full_run, cat_notes, tp_times)
    
    assert len(timeline) == 1
    assert timeline[0]["turning_point"] is True
    assert "tonalité très porteuse" in timeline[0]["summary"]


def test_assembler_integration(cat_map, sample_full_run):
    assembler = PublicPredictionAssembler()
    
    result = assembler.assemble(
        full_run=sample_full_run,
        cat_id_to_code=cat_map,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        run_date_local="2026-03-10",
        run_timezone="Europe/Paris",
        run_computed_at="2026-03-10T10:00:00",
        run_is_provisional=False,
        run_calibration_label="v1",
    )
    
    assert result["meta"]["date_local"] == "2026-03-10"
    assert result["meta"]["calibration_label"] == "v1"
    assert "summary" in result
    assert len(result["categories"]) == 2
    assert len(result["turning_points"]) >= 1


def test_assembler_falls_back_to_engine_output_house_system(cat_map, sample_full_run):
    assembler = PublicPredictionAssembler()
    engine_output = MagicMock()
    engine_output.effective_context.house_system_effective = "placidus"

    result = assembler.assemble(
        full_run=sample_full_run,
        cat_id_to_code=cat_map,
        engine_output=engine_output,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        run_date_local="2026-03-10",
        run_timezone="Europe/Paris",
        run_computed_at="2026-03-10T10:00:00",
        run_is_provisional=False,
        run_calibration_label="v1",
    )

    assert result["meta"]["house_system_effective"] == "placidus"


def test_assembler_summary_uses_provisional_flag(
    cat_map,
    sample_full_run,
):
    assembler = PublicPredictionAssembler()
    full_run = dict(sample_full_run)
    full_run.pop("is_provisional_calibration", None)

    result = assembler.assemble(
        full_run=full_run,
        cat_id_to_code=cat_map,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        run_date_local="2026-03-10",
        run_timezone="Europe/Paris",
        run_computed_at="2026-03-10T10:00:00",
        run_is_provisional=True,
        run_calibration_label="v1",
    )

    assert result["meta"]["is_provisional_calibration"] is True
    assert result["summary"]["calibration_note"] is not None
