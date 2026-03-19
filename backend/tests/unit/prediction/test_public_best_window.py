from unittest.mock import MagicMock

from app.prediction.public_projection import PublicBestWindowPolicy


def test_best_window_select_highest_score():
    policy = PublicBestWindowPolicy()
    
    dw1 = {
        "start_local": "2026-03-18T10:00:00",
        "end_local": "2026-03-18T12:00:00",
        "window_type": "favorable",
        "score": 15.0,
        "intensity": 12.0
    }
    dw2 = {
        "start_local": "2026-03-18T14:00:00",
        "end_local": "2026-03-18T16:00:00",
        "window_type": "favorable",
        "score": 18.0, # Best score
        "intensity": 15.0
    }
    
    result = policy.build(MagicMock(), decision_windows=[dw1, dw2], turning_points=[])
    assert result["time_range"] == "14:00–16:00"
    assert result["label"] == "Pic du jour" # intensity 15.0 >= 14.0

def test_best_window_no_favorable():
    policy = PublicBestWindowPolicy()
    dw1 = {"window_type": "prudence", "score": 5.0}
    result = policy.build(MagicMock(), decision_windows=[dw1], turning_points=[])
    assert result is None

def test_best_window_detect_pivot():
    policy = PublicBestWindowPolicy()
    dw1 = {
        "start_local": "2026-03-18T10:00:00",
        "end_local": "2026-03-18T12:00:00",
        "window_type": "favorable",
        "score": 15.0
    }
    # Turning point inside
    tps = [{"occurred_at_local": "2026-03-18T11:00:00"}]
    
    result = policy.build(MagicMock(), decision_windows=[dw1], turning_points=tps)
    assert result["is_pivot"] is True
