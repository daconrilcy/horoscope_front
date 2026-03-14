from datetime import UTC, datetime, timedelta

import pytest

from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.schemas import V3TimeBlock, V3TurningPoint


def test_build_v3_favorable_window():
    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    # Rising block with high intensity
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 12.0, 0.8, ["work", "love"])
    ]

    windows = builder.build_v3(blocks, [], {})

    assert len(windows) == 1
    assert windows[0].window_type == "favorable"
    assert windows[0].dominant_categories == ["work", "love"]
    assert windows[0].orientation == "rising"


def test_build_v3_prudence_window():
    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    # Falling block
    blocks = [V3TimeBlock(0, start, start + timedelta(hours=2), "falling", 8.0, 0.8, ["money"])]

    windows = builder.build_v3(blocks, [], {})

    assert len(windows) == 1
    assert windows[0].window_type == "prudence"


def test_build_v3_sobriety_filter():
    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    # Stable block with low intensity (weak day)
    blocks = [V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 2.0, 0.8, ["work"])]

    windows = builder.build_v3(blocks, [], {})

    # AC4: Should be filtered out
    assert len(windows) == 0


def test_build_v3_confidence_filter():
    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    # Rising but low confidence
    blocks = [V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 10.0, 0.2, ["work"])]

    windows = builder.build_v3(blocks, [], {})
    assert len(windows) == 0


def test_build_v3_pivot_window():
    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)
    pivot_time = start + timedelta(minutes=30)

    blocks = [V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 10.0, 0.8, ["work"])]
    pivots = [V3TurningPoint(pivot_time, "regime_change", 5.0, 120, 0.8, ["work"])]

    windows = builder.build_v3(blocks, pivots, {})

    # Should have a pivot window
    assert any(w.window_type == "pivot" for w in windows)


def test_build_v3_score_blending():
    from app.prediction.schemas import V3DailyMetrics

    builder = DecisionWindowBuilder()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    # Block with intensity 10.0
    blocks = [V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 10.0, 0.8, ["work"])]

    # Category metrics with score_20 = 15.0
    category_metrics = {
        "work": V3DailyMetrics(
            score_20=15.0,
            level_day=1.0,
            intensity_day=10.0,
            dominance_day=0.5,
            stability_day=0.8,
            rarity_percentile=5.0,
            avg_score=10.0,
            max_score=12.0,
            min_score=8.0,
            volatility=0.2,
        )
    }

    windows = builder.build_v3(blocks, [], category_metrics)

    # Blended score: 10.0 * 0.7 + 15.0 * 0.3 = 7.0 + 4.5 = 11.5
    assert len(windows) == 1
    assert windows[0].score == pytest.approx(11.5)
