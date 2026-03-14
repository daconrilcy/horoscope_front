from datetime import UTC, datetime, timedelta

import pytest

from app.prediction.schemas import AstroEvent, V3TimeBlock
from app.prediction.turning_point_detector import TurningPointDetector


def test_detect_v3_valid_regime_change():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 10.0, 0.8, ["work"]),
    ]

    # 5.0 intensity diff, 120m duration, 0.8 confidence -> Valid
    pivots = detector.detect_v3(blocks, [])

    assert len(pivots) == 1
    assert pivots[0].reason == "regime_change"
    assert pivots[0].local_time == start
    assert pivots[0].amplitude == 5.0


def test_detect_v3_intensity_jump():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "rising", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 9.0, 0.8, ["work"]),
    ]

    # 4.0 intensity diff (>= MIN_V3_AMPLITUDE=3.0), same orientation -> Valid intensity jump
    pivots = detector.detect_v3(blocks, [])

    assert len(pivots) == 1
    assert pivots[0].reason == "intensity_jump"


def test_detect_v3_rejection_low_duration():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(minutes=30), "rising", 10.0, 0.8, ["work"]),
    ]

    # Only 30m duration following ( < MIN_V3_DURATION_FOLLOWING=60 ) -> Rejected
    pivots = detector.detect_v3(blocks, [])
    assert len(pivots) == 0


def test_detect_v3_rejection_low_confidence():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.4, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 10.0, 0.8, ["work"]),
    ]

    # 0.4 confidence ( < MIN_V3_CONFIDENCE=0.5 ) -> Rejected
    pivots = detector.detect_v3(blocks, [])
    assert len(pivots) == 0


def test_detect_v3_rejection_low_regime_amplitude():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 6.2, 0.8, ["work"]),
    ]

    # 1.2 intensity diff ( < MIN_V3_REGIME_AMPLITUDE=1.5 ) -> Rejected
    pivots = detector.detect_v3(blocks, [])
    assert len(pivots) == 0


def test_detect_v3_accept_solid_regime_amplitude():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 6.6, 0.8, ["work"]),
    ]

    # 1.6 intensity diff ( >= MIN_V3_REGIME_AMPLITUDE=1.5 ) -> Valid
    pivots = detector.detect_v3(blocks, [])
    assert len(pivots) == 1
    assert pivots[0].amplitude == pytest.approx(1.6)


def test_detect_v3_with_drivers():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start - timedelta(hours=2), start, "stable", 5.0, 0.8, ["work"]),
        V3TimeBlock(1, start, start + timedelta(hours=2), "rising", 10.0, 0.8, ["work"]),
    ]

    event = AstroEvent(
        event_type="aspect_exact_to_personal",
        ut_time=0.0,
        local_time=start + timedelta(minutes=5),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.0,
        priority=80,
        base_weight=1.0,
    )

    pivots = detector.detect_v3(blocks, [event])
    assert len(pivots) == 1
    assert len(pivots[0].drivers) == 1
    assert pivots[0].drivers[0].event_type == "aspect_exact_to_personal"
