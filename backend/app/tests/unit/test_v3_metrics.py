from datetime import UTC, datetime

import pytest

from app.prediction.aggregator import V3ThemeAggregator
from app.prediction.schemas import V3SignalLayer, V3ThemeSignal


def test_metrics_neutral_day():
    aggregator = V3ThemeAggregator()
    
    # Flat timeline at baseline 1.0
    timeline = {
        datetime(2026, 3, 11, i, 0, tzinfo=UTC): V3SignalLayer(
            baseline=1.0, transit=0.0, aspect=0.0, event=0.0, composite=1.0
        )
        for i in range(24)
    }
    signal = V3ThemeSignal(theme_code="work", timeline=timeline)
    
    metrics = aggregator.aggregate_theme(signal)
    
    assert metrics.score_20 == pytest.approx(10.0)
    assert metrics.intensity_20 == 0.0
    assert metrics.rarity_percentile == 0.0
    assert metrics.confidence_20 > 15.0 # High confidence if flat

def test_metrics_strong_positive_day():
    aggregator = V3ThemeAggregator()
    
    # Signal at 2.0 (avg)
    timeline = {
        datetime(2026, 3, 11, i, 0, tzinfo=UTC): V3SignalLayer(
            baseline=1.0, transit=1.0, aspect=0.0, event=0.0, composite=2.0
        )
        for i in range(24)
    }
    signal = V3ThemeSignal(theme_code="love", timeline=timeline)
    
    metrics = aggregator.aggregate_theme(signal)
    
    # score: 10 + (2.0 - 1.0) * 5 = 15
    assert metrics.score_20 == pytest.approx(15.0)
    assert metrics.intensity_20 > 10.0
    assert metrics.rarity_percentile > 5.0

def test_metrics_volatile_low_confidence():
    aggregator = V3ThemeAggregator()
    
    # Extreme volatility
    timeline = {}
    for i in range(24):
        val = 1.0 + (3.0 if i % 2 == 0 else -3.0)
        timeline[datetime(2026, 3, 11, i, 0, tzinfo=UTC)] = V3SignalLayer(
            baseline=1.0, transit=val-1.0, aspect=0.0, event=0.0, composite=val
        )
    
    signal = V3ThemeSignal(theme_code="health", timeline=timeline)
    metrics = aggregator.aggregate_theme(signal)
    
    # Confidence should be low due to high volatility
    assert metrics.confidence_20 < 10.0
    assert metrics.intensity_20 > 15.0
    assert metrics.rarity_percentile == 20.0 # Extreme peaks
