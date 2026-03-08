import json
from datetime import datetime, timezone

from app.prediction.explainability import (
    ExplainabilityBuilder,
)
from app.prediction.schemas import AstroEvent


def make_event(
    event_type: str,
    dt: datetime,
    body: str,
    target: str,
    aspect: str,
    priority: int,
) -> AstroEvent:
    return AstroEvent(event_type, 0, dt, body, target, aspect, 0, priority, 1.0)


def test_top3_max_3():
    """AC1 — Top 3 contributeurs par catégorie (max 3)"""
    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)

    # 5 events for category 'love'
    contributions_log = [
        (make_event("trine", dt, "Venus", "Mars", "trine", 10), "love", 5.0),
        (make_event("square", dt, "Saturn", "Moon", "square", 20), "love", -10.0),
        (make_event("conjunction", dt, "Jupiter", "Sun", "conjunction", 30), "love", 8.0),
        (make_event("sextile", dt, "Mercury", "Uranus", "sextile", 40), "love", 2.0),
        (make_event("opposition", dt, "Pluto", "Sun", "opposition", 50), "love", -15.0),
    ]

    report = builder.build(contributions_log, "hash", False)

    assert "love" in report.categories
    top_contributors = report.categories["love"].top_contributors
    assert len(top_contributors) == 3
    # Sorted by abs(contribution) descending: -15, -10, 8
    assert top_contributors[0].contribution == -15.0
    assert top_contributors[1].contribution == -10.0
    assert top_contributors[2].contribution == 8.0


def test_sorted_desc():
    """AC2 — Ordre décroissant cohérent"""
    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)

    contributions_log = [
        (make_event("trine", dt, "Venus", "Mars", "trine", 10), "work", 1.0),
        (make_event("square", dt, "Saturn", "Moon", "square", 20), "work", 10.0),
        (make_event("conjunction", dt, "Jupiter", "Sun", "conjunction", 30), "work", 5.0),
    ]

    report = builder.build(contributions_log, "hash", False)
    top = report.categories["work"].top_contributors
    assert top[0].contribution == 10.0
    assert top[1].contribution == 5.0
    assert top[2].contribution == 1.0


def test_debug_mode_on():
    """AC4 — debug_mode=True → debug_data présent"""
    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    contributions_log = [(AstroEvent("trine", 0, dt, "V", "M", "trine", 0, 10, 1.0), "love", 1.0)]
    raw_data = {"2026-03-08T12:00:00": [{"event": "info", "contributions": {"love": 1.0}}]}

    report = builder.build(contributions_log, "hash", True, raw_data)
    assert report.debug_data == raw_data


def test_debug_mode_off():
    """AC4 — debug_mode=False → debug_data is None"""
    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    contributions_log = [(AstroEvent("trine", 0, dt, "V", "M", "trine", 0, 10, 1.0), "love", 1.0)]
    raw_data = {"2026-03-08T12:00:00": [{"event": "info", "contributions": {"love": 1.0}}]}

    report = builder.build(contributions_log, "hash", False, raw_data)
    assert report.debug_data is None


def test_driver_json_valid():
    """
    test_driver_json_valid — contributors sérialisables en JSON valide avec les champs attendus
    """
    from dataclasses import asdict

    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    event = AstroEvent("trine", 0, dt, "Venus", "Mars", "trine", 2.0, 80, 1.5)
    contributions_log = [(event, "love", 7.5)]

    report = builder.build(contributions_log, "hash", False)

    contributors = report.categories["love"].top_contributors
    serialized = json.dumps(
        [
            {k: v.isoformat() if hasattr(v, "isoformat") else v for k, v in asdict(c).items()}
            for c in contributors
        ]
    )
    parsed = json.loads(serialized)

    assert len(parsed) == 1
    assert parsed[0]["event_type"] == "trine"
    assert parsed[0]["body"] == "Venus"
    assert parsed[0]["contribution"] == 7.5
    assert "2026-03-08T12:00:00" in parsed[0]["local_time"]


def test_contributor_fields_complete():
    """test_contributor_fields_complete — chaque ContributorEntry a tous les champs"""
    builder = ExplainabilityBuilder()
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)
    event = AstroEvent(
        event_type="aspect",
        ut_time=123.45,
        local_time=dt,
        body="Venus",
        target="Mars",
        aspect="trine",
        orb_deg=2.5,
        priority=80,
        base_weight=1.5,
        metadata={"phase": "retrograde"},
    )
    contributions_log = [(event, "love", 5.0)]

    report = builder.build(contributions_log, "hash", False)
    entry = report.categories["love"].top_contributors[0]

    assert entry.event_type == "aspect"
    assert entry.body == "Venus"
    assert entry.target == "Mars"
    assert entry.aspect == "trine"
    assert entry.contribution == 5.0
    assert entry.local_time == dt
    assert entry.orb_deg == 2.5
    assert entry.phase == "retrograde"
