from datetime import datetime, UTC
import pytest
from app.prediction.daily_prediction_evidence_builder import DailyPredictionEvidenceBuilder
from app.prediction.schemas import (
    V3EngineOutput, V3DailyMetrics, V3TimeBlock, V3TurningPoint, AstroEvent,
    DecisionWindow
)

def test_build_evidence_pack_minimal():
    builder = DailyPredictionEvidenceBuilder()
    
    # Setup V3EngineOutput
    theme_code = "work"
    metrics = V3DailyMetrics(
        score_20=15.0, level_day=1.5, intensity_day=10.0, dominance_day=0.5, 
        stability_day=15.0, rarity_percentile=5.0,
        avg_score=1.5, max_score=2.0, min_score=1.0, volatility=0.2
    )
    
    # Mock TurningPoint with a driver
    driver = AstroEvent(
        event_type="aspect_exact_to_personal",
        ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC),
        body="Sun", target="Moon", aspect="conjunction", 
        orb_deg=0.0, priority=80, base_weight=1.0
    )
    
    v3_output = V3EngineOutput(
        engine_version="v3.0.0-test",
        snapshot_version="1.0",
        evidence_pack_version="1.0-test",
        daily_metrics={theme_code: metrics},
        time_blocks=[V3TimeBlock(0, datetime(2026, 3, 11, 0, 0, tzinfo=UTC), datetime(2026, 3, 11, 2, 0, tzinfo=UTC), "rising", 10.0, 0.8, [theme_code])],
        turning_points=[V3TurningPoint(datetime(2026, 3, 11, 12, 0, tzinfo=UTC), "regime_change", 5.0, 60, 0.8, [theme_code], [driver])],
        decision_windows=[DecisionWindow(datetime(2026, 3, 11, 12, 0, tzinfo=UTC), datetime(2026, 3, 11, 14, 0, tzinfo=UTC), "favorable", 15.0, 0.8, [theme_code], "rising", 10.0)],
        run_metadata={
            "v3_natal_structural": {"work": {"total": 5.0}},
            "v3_transit_signal": {"work": 1.0},
            "v3_intraday_activation": {"work": 0.5},
            "v3_impulse_signal": {"work": 2.0}
        },
        computed_at=datetime.now(UTC)
    )
    
    evidence = builder.build(v3_output)
    
    # AC1: Check top level structure
    assert evidence.version == "1.0-test"
    assert "avg_score" in evidence.day_profile
    assert theme_code in evidence.themes
    assert len(evidence.time_windows) == 1
    assert len(evidence.turning_points) == 1
    
    # AC2: Check themes mapping
    t_work = evidence.themes[theme_code]
    assert t_work.score_20 == 15.0
    assert t_work.level == 1.5
    assert t_work.is_major is True
    
    # Story 42.15: Check rich diagnostics mapping
    assert evidence.v3_natal_structural["work"]["total"] == 5.0
    assert evidence.v3_layer_diagnostics["transit"]["work"] == 1.0
    assert evidence.v3_layer_diagnostics["aspect"]["work"] == 0.5
    assert evidence.v3_layer_diagnostics["event"]["work"] == 2.0

    # AC4: Check drivers formatting
    tp = evidence.turning_points[0]
    assert "Sun-conjunction-Moon" in tp.drivers
