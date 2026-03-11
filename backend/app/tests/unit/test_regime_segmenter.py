from datetime import UTC, datetime, timedelta

import pytest

from app.prediction.regime_segmenter import RegimeSegmenter
from app.prediction.schemas import V3SignalLayer, V3ThemeSignal


def create_mock_signal(theme_code: str, values: list[float], start_time: datetime):
    timeline = {}
    for i, val in enumerate(values):
        t = start_time + timedelta(minutes=15 * i)
        timeline[t] = V3SignalLayer(
            baseline=1.0, transit=val-1.0, aspect=0.0, event=0.0, composite=val
        )
    return V3ThemeSignal(theme_code=theme_code, timeline=timeline)

def test_segment_quiet_day():
    segmenter = RegimeSegmenter()
    start = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    
    # 96 steps of flat signal 1.0
    signal = create_mock_signal("work", [1.0] * 96, start)
    
    blocks = segmenter.segment({"work": signal})
    
    # On a perfectly flat day, it might produce few segments or be merged
    assert len(blocks) >= 1
    assert len(blocks) <= 8
    for b in blocks:
        assert b.intensity == 0.0
        assert b.orientation == "stable"

def test_segment_contrasting_day():
    segmenter = RegimeSegmenter()
    start = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    
    # 48 steps rising (1.0 -> 2.0), 48 steps falling (2.0 -> 0.0)
    vals = [1.0 + i/48.0 for i in range(48)] + [2.0 - i/24.0 for i in range(48)]
    signal = create_mock_signal("love", vals, start)
    
    blocks = segmenter.segment({"love": signal})
    
    assert len(blocks) >= 4
    # At least one block should be rising, one falling
    orientations = [b.orientation for b in blocks]
    assert "rising" in orientations
    assert "falling" in orientations

def test_segment_merging_limit():
    segmenter = RegimeSegmenter()
    start = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    
    # Very noisy signal that would naturally create many segments
    import math
    vals = [1.0 + 0.5 * math.sin(i) for i in range(96)]
    signal = create_mock_signal("health", vals, start)
    
    blocks = segmenter.segment({"health": signal})
    
    # AC2: 4 to 8 segments max on an active day
    assert len(blocks) >= 4
    assert len(blocks) <= 8

def test_segment_determinism():
    segmenter = RegimeSegmenter()
    start = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    vals = [1.0 + 0.1 * (i % 5) for i in range(96)]
    signal_data = {"test": create_mock_signal("test", vals, start)}
    
    blocks1 = segmenter.segment(signal_data)
    blocks2 = segmenter.segment(signal_data)
    
    assert len(blocks1) == len(blocks2)
    for b1, b2 in zip(blocks1, blocks2):
        assert b1.start_local == b2.start_local
        assert b1.end_local == b2.end_local
        assert b1.orientation == b2.orientation
        assert b1.intensity == pytest.approx(b2.intensity)

def test_segment_volatile_day():
    segmenter = RegimeSegmenter()
    start = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    
    # Random-like but deterministic oscillation
    vals = [1.0 + (0.5 if i % 2 == 0 else -0.5) for i in range(96)]
    signal = create_mock_signal("chaos", vals, start)
    
    blocks = segmenter.segment({"chaos": signal})
    
    orientations = [b.orientation for b in blocks]
    assert "volatile" in orientations
