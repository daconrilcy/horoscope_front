"""Tests for DecisionWindowBuilder (story 41-3 - AC3, AC4)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.prediction.block_generator import TimeBlock
from app.prediction.decision_window_builder import DecisionWindowBuilder
from app.prediction.schemas import DecisionWindow
from app.prediction.turning_point_detector import TurningPoint


def make_block(
    start_offset_h: int,
    duration_h: int,
    tone_code: str,
    dominant_categories: list[str],
) -> TimeBlock:
    base = datetime(2026, 3, 9, 0, 0, tzinfo=timezone.utc)
    start = base + timedelta(hours=start_offset_h)
    end = start + timedelta(hours=duration_h)
    return TimeBlock(
        block_index=start_offset_h,
        start_local=start,
        end_local=end,
        dominant_categories=dominant_categories,
        tone_code=tone_code,
        driver_events=[],
    )


def make_pivot(hour: int) -> TurningPoint:
    dt = datetime(2026, 3, 9, hour, 0, tzinfo=timezone.utc)
    return TurningPoint(
        local_time=dt,
        reason="delta_note",
        categories_impacted=["love"],
        trigger_event=None,
        severity=0.8,
    )


SCORES = {
    "love": {"note_20": 16, "volatility": 0.4},
    "work": {"note_20": 14, "volatility": 0.5},
    "health": {"note_20": 8, "volatility": 2.0},
    "money": {"note_20": 5, "volatility": 0.3},
}


def test_favorable_window_from_positive_block():
    builder = DecisionWindowBuilder()
    block = make_block(8, 2, "positive", ["love", "work"])
    windows = builder.build([block], [], SCORES)

    assert len(windows) == 1
    assert windows[0].window_type == "favorable"


def test_prudence_window_from_negative_block():
    builder = DecisionWindowBuilder()
    block = make_block(14, 2, "negative", ["health", "money"])
    windows = builder.build([block], [], SCORES)

    assert len(windows) == 1
    assert windows[0].window_type == "prudence"


def test_prudence_window_from_mixed_block():
    builder = DecisionWindowBuilder()
    block = make_block(10, 3, "mixed", ["love", "work"])
    windows = builder.build([block], [], SCORES)

    assert len(windows) == 1
    assert windows[0].window_type == "prudence"


def test_neutral_block_is_skipped():
    # AC3: neutral non-pivot blocks are filtered out (reduce noise)
    builder = DecisionWindowBuilder()
    block = make_block(0, 4, "neutral", ["love", "work"])
    windows = builder.build([block], [], SCORES)

    assert len(windows) == 0


def test_pivot_window_overrides_tone():
    # A block containing a turning point becomes "pivot" regardless of tone
    builder = DecisionWindowBuilder()
    block = make_block(12, 2, "neutral", ["work"])
    pivot = make_pivot(13)  # inside the block (12:00 <= 13:00 < 14:00)
    windows = builder.build([block], [pivot], SCORES)

    assert len(windows) == 1
    assert windows[0].window_type == "pivot"


def test_pivot_outside_block_does_not_affect_neutral():
    builder = DecisionWindowBuilder()
    block = make_block(8, 2, "neutral", ["love"])
    pivot = make_pivot(6)  # before the block
    windows = builder.build([block], [pivot], SCORES)

    # Block is neutral and no pivot inside -> skip
    assert len(windows) == 0


def test_ac3_max_two_dominant_categories():
    # AC3: each window exposes at most 2 dominant categories
    builder = DecisionWindowBuilder()
    block = make_block(9, 3, "positive", ["love", "work", "health"])
    windows = builder.build([block], [], SCORES)

    assert len(windows) == 1
    assert len(windows[0].dominant_categories) <= 2


def test_score_reflects_top_categories():
    builder = DecisionWindowBuilder()
    block_high = make_block(8, 2, "positive", ["love"])   # love note=16
    block_low = make_block(14, 2, "negative", ["money"])  # money note=5

    windows_high = builder.build([block_high], [], SCORES)
    windows_low = builder.build([block_low], [], SCORES)

    assert windows_high[0].score > windows_low[0].score


def test_confidence_inverse_of_volatility():
    builder = DecisionWindowBuilder()
    # love: vol=0.4 -> confidence near 1.0-0.4/3 ~ 0.87
    block_stable = make_block(8, 2, "positive", ["love"])
    # health: vol=2.0 -> confidence near 1.0-2/3 ~ 0.33
    block_volatile = make_block(14, 2, "negative", ["health"])

    [w_stable] = builder.build([block_stable], [], SCORES)
    [w_volatile] = builder.build([block_volatile], [], SCORES)

    assert w_stable.confidence > w_volatile.confidence


def test_multiple_blocks_mixed_types():
    # AC3: reasonable and readable window count
    builder = DecisionWindowBuilder()
    blocks = [
        make_block(0, 6, "neutral", ["work"]),    # skip
        make_block(6, 3, "positive", ["love"]),   # favorable
        make_block(9, 3, "neutral", ["work"]),    # skip
        make_block(12, 4, "negative", ["money"]), # prudence
        make_block(16, 4, "neutral", ["work"]),   # skip
        make_block(20, 4, "mixed", ["health"]),   # prudence
    ]
    pivot = make_pivot(22)  # inside last block (20:00 <= 22:00 < 00:00)

    windows = builder.build(blocks, [pivot], SCORES)
    types = [w.window_type for w in windows]

    assert "favorable" in types
    assert "prudence" in types
    assert "pivot" in types
    # Neutral blocks suppressed: only 3 windows
    assert len(windows) == 3


def test_decision_window_is_frozen_dataclass():
    dw = DecisionWindow(
        start_local=datetime(2026, 3, 9, 8, tzinfo=timezone.utc),
        end_local=datetime(2026, 3, 9, 10, tzinfo=timezone.utc),
        window_type="favorable",
        score=15.0,
        confidence=0.8,
        dominant_categories=["love"],
    )
    with pytest.raises(Exception):
        dw.window_type = "prudence"  # type: ignore[misc]
