from datetime import UTC, datetime, timedelta

from app.prediction.schemas import AstroEvent, V3TimeBlock
from app.prediction.turning_point_detector import TurningPointDetector


def test_detect_v3_semantics_emergence():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # prev: low intensity, curr: high intensity -> emergence
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 2.0, 0.8, ["work"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "rising",
            10.0,
            0.8,
            ["work", "love"],
        ),
    ]

    events = [
        AstroEvent(
            "aspect_exact_to_personal",
            0.0,
            start + timedelta(hours=2),
            "Sun",
            "Moon",
            "conjunction",
            0.0,
            80,
            1.0,
        )
    ]

    pivots = detector.detect_v3(blocks, events)

    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "emergence"
    assert tp.previous_categories == ["work"]
    assert tp.next_categories == ["work", "love"]
    assert tp.primary_driver is not None
    assert tp.primary_driver.event_type == "aspect_exact_to_personal"
    assert tp.primary_driver.body == "Sun"


def test_detect_v3_semantics_attenuation():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # prev: high intensity, curr: low intensity -> attenuation
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 10.0, 0.8, ["work"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "falling",
            2.0,
            0.8,
            ["work"],
        ),
    ]

    pivots = detector.detect_v3(blocks, [])

    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "attenuation"


def test_detect_v3_semantics_recomposition():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # Orientation change + enough intensity diff to trigger reason
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 6.0, 0.8, ["work"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "stable",
            7.6,
            0.8,
            ["love"],
        ),
    ]

    pivots = detector.detect_v3(blocks, [])

    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.change_type == "recomposition"  # Intensity jump < 2.5.
    assert tp.previous_categories == ["work"]
    assert tp.next_categories == ["love"]


def test_detect_v3_excludes_midnight():
    detector = TurningPointDetector()
    # Midnight transition
    start = datetime(2026, 3, 11, 22, 0, tzinfo=UTC)
    midnight = datetime(2026, 3, 12, 0, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start, midnight, "stable", 2.0, 0.8, ["work"]),
        V3TimeBlock(
            1,
            midnight,
            midnight + timedelta(hours=2),
            "rising",
            10.0,
            0.8,
            ["work"],
        ),
    ]

    pivots = detector.detect_v3(blocks, [])

    # Should be excluded per AC4
    assert len(pivots) == 0


def test_primary_driver_selection_priority():
    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 12, 0, tzinfo=UTC)

    # Drivers: 1 public exact, 1 ingress, 1 generic
    drivers = [
        AstroEvent("generic_event", 0.0, start, "Mars", None, None, 0.0, 90, 1.0),
        AstroEvent("moon_sign_ingress", 0.0, start, "Moon", "Aries", None, 0.0, 50, 1.0),
        AstroEvent(
            "aspect_exact_to_personal",
            0.0,
            start,
            "Sun",
            "Moon",
            "conjunction",
            0.0,
            70,
            1.0,
        ),
    ]

    # Priority 1: public exact aspect should be chosen over public ingress
    primary = detector._select_primary_driver(drivers)
    assert primary.event_type == "aspect_exact_to_personal"


def test_detect_v3_movement_indicators():
    from app.prediction.schemas import V3SignalLayer, V3ThemeSignal

    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # prev: low composite, curr: high composite
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 2.0, 0.8, ["work"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "rising",
            10.0,
            0.8,
            ["love"],
        ),
    ]

    # Mock signals
    t1 = start + timedelta(hours=1)  # middle of block 0
    t2 = start + timedelta(hours=3)  # middle of block 1

    theme_signals = {
        "love": V3ThemeSignal(
            theme_code="love",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 2.0),
                t2: V3SignalLayer(0, 0, 0, 0, 10.0),
            },
        ),
        "work": V3ThemeSignal(
            theme_code="work",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 5.0),
                t2: V3SignalLayer(0, 0, 0, 0, 5.1),
            },
        ),
    }

    pivots = detector.detect_v3(blocks, [], theme_signals)

    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.movement is not None
    assert tp.movement.direction == "rising"
    assert tp.movement.strength > 0
    assert tp.movement.delta_composite == (10.0 + 5.1) - (2.0 + 5.0)

    # Category deltas
    love_delta = next(d for d in tp.category_deltas if d.code == "love")
    assert love_delta.direction == "up"
    assert love_delta.delta_intensity == 8.0

    work_delta = next((d for d in tp.category_deltas if d.code == "work"), None)
    # Work delta is 0.1, which is < 0.2 threshold in my implementation
    assert work_delta is None


def test_detect_v3_movement_attenuation():
    from app.prediction.schemas import V3SignalLayer, V3ThemeSignal

    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 10.0, 0.8, ["love"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "falling",
            2.0,
            0.8,
            ["love"],
        ),
    ]

    t1 = start + timedelta(hours=1)
    t2 = start + timedelta(hours=3)

    theme_signals = {
        "love": V3ThemeSignal(
            theme_code="love",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 10.0),
                t2: V3SignalLayer(0, 0, 0, 0, 2.0),
            },
        ),
    }

    pivots = detector.detect_v3(blocks, [], theme_signals)
    tp = pivots[0]
    assert tp.movement.direction == "falling"
    assert tp.category_deltas[0].direction == "down"


def test_detect_v3_movement_redistribution():
    from app.prediction.schemas import V3SignalLayer, V3ThemeSignal

    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # Orientation change to trigger regime_change + diff >= 1.5
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "rising", 6.0, 0.8, ["love"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "stable",
            7.6,
            0.8,
            ["work"],
        ),
    ]

    t1 = start + timedelta(hours=1)
    t2 = start + timedelta(hours=3)

    # Love goes down, Work goes up, total composite stays similar
    theme_signals = {
        "love": V3ThemeSignal(
            theme_code="love",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 8.0),
                t2: V3SignalLayer(0, 0, 0, 0, 2.0),
            },
        ),
        "work": V3ThemeSignal(
            theme_code="work",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 2.0),
                t2: V3SignalLayer(0, 0, 0, 0, 8.1),
            },
        ),
    }

    pivots = detector.detect_v3(blocks, [], theme_signals)
    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.movement.direction == "recomposition"  # Delta is 0.1.
    assert len(tp.category_deltas) == 2
    assert any(d.code == "love" and d.direction == "down" for d in tp.category_deltas)
    assert any(d.code == "work" and d.direction == "up" for d in tp.category_deltas)


def test_detect_v3_movement_below_threshold():
    from app.prediction.schemas import V3SignalLayer, V3ThemeSignal

    detector = TurningPointDetector()
    start = datetime(2026, 3, 12, 10, 0, tzinfo=UTC)

    # intensity_jump >= 3.0
    blocks = [
        V3TimeBlock(0, start, start + timedelta(hours=2), "stable", 10.0, 0.8, ["love"]),
        V3TimeBlock(
            1,
            start + timedelta(hours=2),
            start + timedelta(hours=4),
            "stable",
            13.1,
            0.8,
            ["love"],
        ),
    ]

    t1 = start + timedelta(hours=1)
    t2 = start + timedelta(hours=3)

    # Very small variations
    theme_signals = {
        "love": V3ThemeSignal(
            theme_code="love",
            timeline={
                t1: V3SignalLayer(0, 0, 0, 0, 5.0),
                t2: V3SignalLayer(0, 0, 0, 0, 5.1),
            },
        ),
    }

    pivots = detector.detect_v3(blocks, [], theme_signals)
    assert len(pivots) == 1
    tp = pivots[0]
    assert tp.movement.direction == "recomposition"
    assert len(tp.category_deltas) == 0  # Below 0.2 threshold.
