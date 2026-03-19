from datetime import UTC, date, datetime

from app.prediction.persisted_snapshot import PersistedCategoryScore, PersistedPredictionSnapshot
from app.prediction.public_projection import PublicPredictionAssembler


def _build_base_snapshot():
    return {
        "run_id": 1,
        "user_id": 1,
        "local_date": date(2026, 3, 18),
        "timezone": "UTC",
        "computed_at": datetime.now(UTC),
        "input_hash": "hash",
        "reference_version_id": 1,
        "ruleset_id": 1,
        "house_system_effective": "placidus",
        "is_provisional_calibration": False,
        "calibration_label": None,
        "overall_summary": "Base Summary",
        "overall_tone": "neutral",
        "category_scores": [],
        "turning_points": [],
        "time_blocks": [],
    }


def test_scenario_flat_day():
    assembler = PublicPredictionAssembler()
    data = _build_base_snapshot()
    # All scores around 10
    data["category_scores"] = [
        PersistedCategoryScore(i, code, 10, 0.5, 0.5, 0.0, i, False, "Summary")
        for i, code in enumerate(["work", "love", "energy", "money", "communication"], 1)
    ]
    data["overall_tone"] = "neutral"

    snapshot = PersistedPredictionSnapshot(**data)
    cat_id_to_code = {s.category_id: s.category_code for s in snapshot.category_scores}

    result = assembler.assemble(
        snapshot, cat_id_to_code, reference_version="1", ruleset_version="1"
    )

    assert result["day_climate"]["intensity"] < 6.0
    assert result["turning_point"] is None
    for d in result["domain_ranking"]:
        assert d["level"] in ("stable", "mitigé")


def test_scenario_polarized_day():
    assembler = PublicPredictionAssembler()
    data = _build_base_snapshot()
    # One high, one low. Use score_20 as build() uses it.
    data["category_scores"] = [
        PersistedCategoryScore(
            category_id=1,
            category_code="work",
            note_20=18,
            raw_score=1.0,
            power=1.0,
            volatility=0.0,
            rank=1,
            is_provisional=False,
            summary="H",
            score_20=18.0,
        ),
        PersistedCategoryScore(
            category_id=2,
            category_code="energy",
            note_20=4,
            raw_score=0.1,
            power=0.1,
            volatility=0.0,
            rank=2,
            is_provisional=False,
            summary="L",
            score_20=4.0,
        ),
    ]
    data["overall_tone"] = "mixed"

    snapshot = PersistedPredictionSnapshot(**data)
    cat_id_to_code = {s.category_id: s.category_code for s in snapshot.category_scores}

    result = assembler.assemble(
        snapshot, cat_id_to_code, reference_version="1", ruleset_version="1"
    )

    assert any(d["score_10"] >= 8.5 for d in result["domain_ranking"])
    assert any(d["score_10"] <= 3.5 for d in result["domain_ranking"])
    assert result["day_climate"]["watchout"] is not None


def test_scenario_turning_point():
    assembler = PublicPredictionAssembler()
    data = _build_base_snapshot()
    data["category_scores"] = [
        PersistedCategoryScore(1, "work", 12, 0.5, 0.5, 0.0, 1, False, "S", score_20=12.0)
    ]

    from unittest.mock import MagicMock

    from app.prediction.schemas import V3EvidencePack, V3EvidenceTurningPoint

    tp = V3EvidenceTurningPoint(
        local_time=datetime(2026, 3, 18, 10, 0),
        reason="regime_change",
        amplitude=8.0,  # V3Evidence uses 0-20 scale usually
        confidence=0.9,
        themes=["work"],
        drivers=["Mars"],
        change_type="emergence",
    )

    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(UTC),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[tp],
    )

    mock_bundle = MagicMock()
    mock_bundle.v3_core.evidence_pack = evidence

    snapshot = PersistedPredictionSnapshot(**data)
    cat_id_to_code = {1: "work"}

    result = assembler.assemble(
        snapshot,
        cat_id_to_code,
        reference_version="1",
        ruleset_version="1",
        engine_output=mock_bundle,
    )

    assert result["turning_point"] is not None
    assert result["turning_point"]["change_type"] == "emergence"
    assert result["turning_point"]["do"] != ""


def test_scenario_low_events():
    assembler = PublicPredictionAssembler()
    data = _build_base_snapshot()
    snapshot = PersistedPredictionSnapshot(**data)

    result = assembler.assemble(snapshot, {}, reference_version="1", ruleset_version="1")

    assert result["astro_foundation"] is None
    assert len(result["time_windows"]) == 4
    assert result["time_windows"][0]["period_key"] == "nuit"
