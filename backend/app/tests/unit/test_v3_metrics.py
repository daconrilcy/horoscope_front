from datetime import UTC, datetime

import pytest

from app.prediction.aggregator import V3ThemeAggregator
from app.prediction.schemas import V3SignalLayer, V3ThemeSignal


def _build_signal(
    theme_code: str,
    layers: list[V3SignalLayer],
) -> V3ThemeSignal:
    timeline = {
        datetime(2026, 3, 11, index, 0, tzinfo=UTC): layer
        for index, layer in enumerate(layers)
    }
    return V3ThemeSignal(theme_code=theme_code, timeline=timeline)


def test_metrics_neutral_day():
    aggregator = V3ThemeAggregator()
    signal = _build_signal(
        "work",
        [
            V3SignalLayer(baseline=1.0, transit=0.0, aspect=0.0, event=0.0, composite=1.0)
            for _ in range(24)
        ],
    )

    metrics = aggregator.aggregate_theme(signal)

    assert metrics.score_20 == pytest.approx(10.0)
    assert metrics.intensity_20 == 0.0
    assert metrics.rarity_percentile == 0.0
    assert metrics.confidence_20 > 15.0


def test_metrics_score_and_intensity_can_diverge():
    aggregator = V3ThemeAggregator()
    lightly_oriented = _build_signal(
        "love",
        [
            V3SignalLayer(baseline=1.0, transit=0.2, aspect=0.0, event=0.0, composite=1.2)
            for _ in range(24)
        ],
    )
    intensely_neutral = _build_signal(
        "love",
        [
            V3SignalLayer(
                baseline=1.0,
                transit=1.0 if hour % 2 == 0 else -1.0,
                aspect=0.0,
                event=0.0,
                composite=2.0 if hour % 2 == 0 else 0.0,
            )
            for hour in range(24)
        ],
    )

    lightly_oriented_metrics = aggregator.aggregate_theme(lightly_oriented)
    intensely_neutral_metrics = aggregator.aggregate_theme(intensely_neutral)

    assert lightly_oriented_metrics.score_20 > intensely_neutral_metrics.score_20
    assert intensely_neutral_metrics.intensity_20 > lightly_oriented_metrics.intensity_20


def test_metrics_confidence_drops_when_signal_is_poorly_explained():
    aggregator = V3ThemeAggregator()
    well_explained = _build_signal(
        "health",
        [
            V3SignalLayer(baseline=1.0, transit=0.8, aspect=0.0, event=0.0, composite=1.8)
            for _ in range(24)
        ],
    )
    noisy_cancellation = _build_signal(
        "health",
        [
            V3SignalLayer(
                baseline=1.0,
                transit=1.4 if hour % 2 == 0 else -1.4,
                aspect=-1.1 if hour % 2 == 0 else 1.1,
                event=0.0,
                composite=1.3 if hour % 2 == 0 else 0.7,
            )
            for hour in range(24)
        ],
    )

    explained_metrics = aggregator.aggregate_theme(well_explained)
    noisy_metrics = aggregator.aggregate_theme(noisy_cancellation)

    assert explained_metrics.confidence_20 > noisy_metrics.confidence_20


def test_metrics_confidence_drops_when_baseline_is_missing():
    aggregator = V3ThemeAggregator()
    with_baseline = _build_signal(
        "money",
        [
            V3SignalLayer(baseline=1.0, transit=0.3, aspect=0.0, event=0.0, composite=1.3)
            for _ in range(24)
        ],
    )
    without_baseline = _build_signal(
        "money",
        [
            V3SignalLayer(baseline=0.0, transit=0.3, aspect=0.0, event=0.0, composite=0.3)
            for _ in range(24)
        ],
    )

    with_baseline_metrics = aggregator.aggregate_theme(with_baseline)
    without_baseline_metrics = aggregator.aggregate_theme(without_baseline)

    assert with_baseline_metrics.confidence_20 > without_baseline_metrics.confidence_20


def test_metrics_rarity_is_distinct_from_intensity():
    aggregator = V3ThemeAggregator()
    sustained_activity = _build_signal(
        "work",
        [
            V3SignalLayer(baseline=1.0, transit=0.9, aspect=0.0, event=0.0, composite=1.9)
            for _ in range(24)
        ],
    )
    one_sharp_spike = _build_signal(
        "work",
        [
            V3SignalLayer(
                baseline=1.0,
                transit=3.0 if hour == 12 else 0.0,
                aspect=0.0,
                event=0.0,
                composite=4.0 if hour == 12 else 1.0,
            )
            for hour in range(24)
        ],
    )

    sustained_metrics = aggregator.aggregate_theme(sustained_activity)
    spike_metrics = aggregator.aggregate_theme(one_sharp_spike)

    assert sustained_metrics.intensity_20 > spike_metrics.intensity_20
    assert spike_metrics.rarity_percentile > sustained_metrics.rarity_percentile


def test_metrics_volatile_day_has_lower_confidence():
    aggregator = V3ThemeAggregator()
    timeline = [
        V3SignalLayer(
            baseline=1.0,
            transit=3.0 if hour % 2 == 0 else -3.0,
            aspect=0.0,
            event=0.0,
            composite=4.0 if hour % 2 == 0 else -2.0,
        )
        for hour in range(24)
    ]

    metrics = aggregator.aggregate_theme(_build_signal("career", timeline))

    assert metrics.confidence_20 < 10.0
    assert metrics.intensity_20 > 15.0
    assert metrics.rarity_percentile > 10.0
