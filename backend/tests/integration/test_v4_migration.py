from datetime import UTC, date, datetime

from app.prediction.persisted_snapshot import PersistedCategoryScore, PersistedPredictionSnapshot
from app.prediction.public_projection import PublicPredictionAssembler


def test_v4_payload_contains_v3_fields():
    assembler = PublicPredictionAssembler()

    # Mock snapshot
    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=1,
        local_date=date(2026, 3, 18),
        timezone="UTC",
        computed_at=datetime.now(UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label=None,
        overall_summary="Summary",
        overall_tone="positive",
        category_scores=[
            PersistedCategoryScore(
                category_id=1,
                category_code="work",
                note_20=15,
                raw_score=1.0,
                power=1.0,
                volatility=0.0,
                rank=1,
                is_provisional=False,
                summary="Work summary",
            )
        ],
        turning_points=[],
        time_blocks=[],
    )

    cat_id_to_code = {1: "work"}

    result = assembler.assemble(
        snapshot=snapshot,
        cat_id_to_code=cat_id_to_code,
        reference_version="1.0.0",
        ruleset_version="2.0.0",
    )

    # V4 fields
    assert result["meta"]["payload_version"] == "v4"
    assert "day_climate" in result
    assert "domain_ranking" in result

    # V3 fields (Retrocompat)
    assert "summary" in result
    assert "categories" in result
    assert "timeline" in result
    assert "turning_points" in result
    assert "categories_internal" in result


def test_v4_payload_compatibility_with_v3_client():
    assembler = PublicPredictionAssembler()
    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=1,
        local_date=date(2026, 3, 18),
        timezone="UTC",
        computed_at=datetime.now(UTC),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective=None,
        is_provisional_calibration=False,
        calibration_label=None,
        overall_summary=None,
        overall_tone=None,
        category_scores=[],
        turning_points=[],
        time_blocks=[],
    )

    result = assembler.assemble(
        snapshot=snapshot, cat_id_to_code={}, reference_version="1.0.0", ruleset_version="2.0.0"
    )

    assert isinstance(result["categories"], list)
    assert isinstance(result["summary"], dict)
