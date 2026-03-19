from datetime import datetime
from unittest.mock import MagicMock

from app.prediction.public_projection import PublicDayClimatePolicy
from app.prediction.schemas import V3EvidencePack, V3EvidenceTheme


def test_day_climate_build_basic():
    policy = PublicDayClimatePolicy()
    snapshot = MagicMock()
    snapshot.overall_tone = "positive"
    
    domain_ranking = [
        {"key": "pro_ambition", "score_10": 8.5},
        {"key": "relations_echanges", "score_10": 7.0},
        {"key": "energie_bienetre", "score_10": 4.0},
    ]
    
    decision_windows = [
        {
            "start_local": "2026-03-18T10:00:00",
            "end_local": "2026-03-18T12:00:00",
            "window_type": "favorable",
            "score": 18.0,
            "confidence": 0.9
        }
    ]
    
    result = policy.build(snapshot, domain_ranking, decision_windows)
    
    assert result["tone"] == "positive"
    assert result["top_domains"] == ["pro_ambition", "relations_echanges"]
    assert result["watchout"] == "energie_bienetre"
    assert result["best_window_ref"] == "10:00–12:00"
    assert "intensity" in result
    assert "stability" in result
    assert "label" in result
    assert "summary" in result

def test_day_climate_build_no_watchout():
    policy = PublicDayClimatePolicy()
    snapshot = MagicMock()
    snapshot.overall_tone = "neutral"
    
    domain_ranking = [
        {"key": "pro_ambition", "score_10": 8.5},
        {"key": "relations_echanges", "score_10": 6.0},
    ]
    
    result = policy.build(snapshot, domain_ranking, None)
    assert result["watchout"] is None

def test_day_climate_uses_evidence():
    policy = PublicDayClimatePolicy()
    snapshot = MagicMock()
    snapshot.overall_tone = "neutral"
    
    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={"overall_tone": "mixed", "avg_intensity": 16.0, "avg_stability": 10.0},
        themes={
            "t1": V3EvidenceTheme("t1", 15.0, 1.0, 16.0, 5.0, 10.0, 10.0, True)
        },
        time_windows=[],
        turning_points=[]
    )
    
    result = policy.build(snapshot, [], None, evidence=evidence)
    
    assert result["tone"] == "mixed"
    assert result["intensity"] == 8.0 # 16/2
    assert result["stability"] == 5.0 # 10/2
