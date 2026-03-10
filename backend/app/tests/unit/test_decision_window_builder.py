# backend/app/tests/unit/test_decision_window_builder.py
from datetime import datetime, timedelta

from app.prediction.block_generator import TimeBlock
from app.prediction.decision_window_builder import DecisionWindowBuilder

BASE_TIME = datetime(2026, 3, 9, 6, 0, 0)


def test_neutral_blocks_excluded():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="neutral",
        dominant_categories=["energy"],
    )
    # no pivot
    windows = builder.build([block], [], {})
    assert len(windows) == 0


def test_positive_tone_yields_favorable():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="positive",
        dominant_categories=["energy"],
    )
    windows = builder.build([block], [], {"energy": {"note_20": 15, "volatility": 0.5}})
    assert len(windows) == 1
    assert windows[0].window_type == "favorable"


def test_negative_tone_yields_prudence():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="negative",
        dominant_categories=["love"],
    )
    windows = builder.build([block], [], {"love": {"note_20": 5, "volatility": 0.5}})
    assert len(windows) == 1
    assert windows[0].window_type == "prudence"


def test_mixed_tone_yields_prudence():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="mixed",
        dominant_categories=["work"],
    )
    windows = builder.build([block], [], {"work": {"note_20": 10, "volatility": 1.5}})
    assert len(windows) == 1
    assert windows[0].window_type == "prudence"


def test_pivot_block_yields_pivot():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="neutral",
        dominant_categories=["energy"],
    )
    # Mocking turning point
    from app.prediction.turning_point_detector import TurningPoint

    pivots = [
        TurningPoint(
            local_time=BASE_TIME + timedelta(hours=1),
            reason="test",
            categories_impacted=[],
            trigger_event=None,
            severity=0.5,
        )
    ]
    windows = builder.build([block], pivots, {"energy": {"note_20": 10, "volatility": 0.5}})
    assert len(windows) == 1
    assert windows[0].window_type == "pivot"
    assert windows[0].start_local == BASE_TIME + timedelta(hours=1)
    assert windows[0].end_local == BASE_TIME + timedelta(hours=2)


def test_positive_pivot_block_stays_favorable():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=2),
        tone_code="positive",
        dominant_categories=["energy"],
    )
    from app.prediction.turning_point_detector import TurningPoint

    pivots = [
        TurningPoint(
            local_time=BASE_TIME + timedelta(minutes=30),
            reason="high_priority_event",
            categories_impacted=[],
            trigger_event=None,
            severity=1.0,
        )
    ]

    windows = builder.build([block], pivots, {"energy": {"note_20": 15, "volatility": 0.5}})

    assert len(windows) == 1
    assert windows[0].window_type == "favorable"
    assert windows[0].start_local == BASE_TIME
    assert windows[0].end_local == BASE_TIME + timedelta(hours=2)


def test_neutral_pivot_window_is_clipped_to_readable_duration():
    builder = DecisionWindowBuilder()
    block = TimeBlock(
        block_index=0,
        start_local=BASE_TIME,
        end_local=BASE_TIME + timedelta(hours=8),
        tone_code="neutral",
        dominant_categories=["energy"],
    )
    from app.prediction.turning_point_detector import TurningPoint

    pivots = [
        TurningPoint(
            local_time=BASE_TIME,
            reason="delta_note",
            categories_impacted=[],
            trigger_event=None,
            severity=0.8,
        )
    ]

    windows = builder.build([block], pivots, {"energy": {"note_20": 10, "volatility": 0.5}})

    assert len(windows) == 1
    assert windows[0].window_type == "pivot"
    assert windows[0].start_local == BASE_TIME
    assert windows[0].end_local == BASE_TIME + timedelta(minutes=90)


def test_builder_does_not_silently_clip_window_count():
    builder = DecisionWindowBuilder()
    blocks = [
        TimeBlock(
            block_index=index,
            start_local=BASE_TIME + timedelta(hours=index),
            end_local=BASE_TIME + timedelta(hours=index + 1),
            tone_code="positive",
            dominant_categories=["energy"],
        )
        for index in range(7)
    ]

    windows = builder.build(
        blocks,
        [],
        {"energy": {"note_20": 15, "volatility": 0.5}},
    )

    assert len(windows) == 7
