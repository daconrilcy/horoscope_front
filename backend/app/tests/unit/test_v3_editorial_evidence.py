from datetime import UTC, date, datetime
from unittest.mock import MagicMock

from app.prediction.editorial_service import PredictionEditorialService
from app.prediction.schemas import (
    CoreEngineOutput,
    EffectiveContext,
    V3EvidencePack,
    V3EvidenceTheme,
)


def test_editorial_service_uses_evidence_pack():
    # Setup mock evidence pack
    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime.now(UTC),
        day_profile={"tone": "positive", "avg_intensity": 15.0},
        themes={
            "work": V3EvidenceTheme(
                code="work", score_20=18.0, level=1.5, intensity=18.0, 
                dominance=10.0, stability=15.0, rarity=12.0, is_major=True
            )
        },
        time_windows=[],
        turning_points=[]
    )
    
    # Mock CoreEngineOutput (legacy source)
    core_output = MagicMock(spec=CoreEngineOutput)
    core_output.effective_context = MagicMock(spec=EffectiveContext)
    core_output.effective_context.local_date = date(2026, 3, 11)
    core_output.category_scores = {"work": {"note_20": 10}} # Diff score
    core_output.explainability = MagicMock()
    core_output.time_blocks = []
    core_output.turning_points = []
    
    service = PredictionEditorialService()
    
    # Run bundle generation with evidence pack
    bundle = service.generate_bundle(core_output, evidence_pack=evidence_pack)
    
    # Data should come from evidence pack (score 18, not 10)
    assert bundle.data.top3_categories[0].code == "work"
    assert bundle.data.top3_categories[0].note_20 == 18


def test_editorial_service_uses_local_date_from_evidence_day_profile():
    evidence_pack = V3EvidencePack(
        version="3.0.0",
        generated_at=datetime(2026, 3, 10, 23, 0, tzinfo=UTC),
        day_profile={
            "tone": "positive",
            "avg_intensity": 15.0,
            "local_date": "2026-03-11",
        },
        themes={
            "work": V3EvidenceTheme(
                code="work",
                score_20=18.0,
                level=1.5,
                intensity=18.0,
                dominance=10.0,
                stability=15.0,
                rarity=12.0,
                is_major=True,
            )
        },
        time_windows=[],
        turning_points=[],
    )

    core_output = MagicMock(spec=CoreEngineOutput)
    core_output.effective_context = MagicMock(spec=EffectiveContext)
    core_output.effective_context.local_date = date(2026, 3, 11)
    core_output.category_scores = {"work": {"note_20": 10}}
    core_output.explainability = MagicMock()
    core_output.time_blocks = []
    core_output.turning_points = []

    bundle = PredictionEditorialService().generate_bundle(core_output, evidence_pack=evidence_pack)

    assert "2026-03-11" in bundle.text.intro
