from datetime import date, datetime, UTC
from unittest.mock import MagicMock
from app.prediction.public_projection import PublicPredictionAssembler
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.prediction.schemas import (
    V3EvidencePack, V3EvidenceTheme, V3EvidenceWindow, V3EvidenceTurningPoint,
    V3EngineOutput
)

def test_assemble_uses_evidence_pack():
    # Setup mock evidence pack
    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={"tone": "positive", "avg_intensity": 15.0, "overall_summary": "Summary from evidence"},
        themes={
            "love": V3EvidenceTheme(
                code="love", score_20=18.0, level=1.5, intensity=18.0, 
                dominance=10.0, stability=15.0, rarity=12.0, is_major=True
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
                themes=["love"]
            )
        ],
        turning_points=[
            V3EvidenceTurningPoint(
                local_time=datetime(2026, 3, 7, 10, 0),
                reason="regime_change",
                amplitude=5.0,
                confidence=0.8,
                themes=["love"],
                drivers=["Venus-trine-Mars"]
            )
        ]
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
        ruleset_version="2.0.0"
    )
    
    # Check that summary comes from evidence pack
    assert result["summary"]["overall_summary"] == "Summary from evidence"
    
    # Check category derived from evidence
    love_cat = next(c for c in result["categories"] if c["code"] == "love")
    assert love_cat["score_20"] == 18.0
    
    # Check that editorial bundle also uses evidence (indirectly via engine_output mock setup if real service called)
    # In this test we called assembler.assemble which uses evidence.
    # To truly test EditorialService, we'd need another test.
