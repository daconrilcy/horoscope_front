import pytest
from datetime import datetime
from unittest.mock import MagicMock
from app.prediction.public_projection import PublicTimeWindowPolicy
from app.prediction.schemas import V3TimeBlock

def test_time_window_resolve_regime_progression():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 14, 0)
    end = datetime(2026, 3, 18, 18, 0)
    
    regime = policy._resolve_regime(start, end, "rising", [])
    assert regime == "progression"

def test_time_window_resolve_regime_pivot():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 14, 0)
    end = datetime(2026, 3, 18, 18, 0)
    turning_points = [{"occurred_at_local": "2026-03-18T15:30:00"}]
    
    regime = policy._resolve_regime(start, end, "rising", turning_points)
    assert regime == "pivot"

def test_time_window_resolve_regime_recovery_night():
    policy = PublicTimeWindowPolicy()
    start = datetime(2026, 3, 18, 2, 0)
    end = datetime(2026, 3, 18, 6, 0)
    
    regime = policy._resolve_regime(start, end, "stable", [])
    assert regime == "récupération"

def test_time_window_map_domains():
    policy = PublicTimeWindowPolicy()
    # work, career -> pro_ambition
    # love -> relations_echanges
    internal = ["work", "career", "love"]
    public = policy._map_domains(internal)
    assert public == ["pro_ambition", "relations_echanges"]

def test_time_window_build_basic():
    policy = PublicTimeWindowPolicy()
    snapshot = MagicMock()
    
    # Use a real object or a more specific mock
    class MockBlock:
        def __init__(self):
            self.start_local = datetime(2026, 3, 18, 10, 0)
            self.end_local = datetime(2026, 3, 18, 12, 0)
            self.orientation = "stable"
            self.themes = ["energy"]
    
    block = MockBlock()
    
    evidence = MagicMock()
    evidence.time_windows = [block]
    
    result = policy.build(snapshot, [], evidence=evidence)
    
    assert len(result) == 1
    assert result[0]["time_range"] == "10:00–12:00"
    assert result[0]["regime"] == "fluidité"
    assert result[0]["top_domains"] == ["energie_bienetre"]
    assert "label" in result[0]
    assert "action_hint" in result[0]
