from dataclasses import asdict
from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
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


def test_assemble_uses_evidence_pack():
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

    result = assembler.assemble(
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


def test_assemble_uses_persisted_evidence_pack_snapshot():
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

    result = PublicPredictionAssembler().assemble(
        snapshot,
        {1: "work"},
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    assert result["summary"]["overall_summary"] == "Persisted evidence summary"
    assert result["decision_windows"][0]["window_type"] == "favorable"
    assert result["categories"][0]["code"] == "work"
