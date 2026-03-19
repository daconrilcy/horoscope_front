from datetime import datetime

import pytest

from app.prediction.public_astro_daily_events import PublicAstroDailyEventsPolicy
from app.prediction.schemas import AstroEvent, V3EvidencePack


@pytest.fixture
def policy():
    return PublicAstroDailyEventsPolicy()


def test_extract_aspects(policy):
    events = [
        AstroEvent(
            event_type="aspect",
            ut_time=0.0,
            local_time=datetime(2026, 3, 19, 12, 0),
            body="venus",
            target="saturn",
            aspect="trine",
            orb_deg=1.2,
            priority=50,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="aspect",
            ut_time=0.0,
            local_time=datetime(2026, 3, 19, 13, 0),
            body="mercury",
            target="jupiter",
            aspect="sextile",
            orb_deg=0.5,
            priority=60,
            base_weight=1.0,
        ),
    ]

    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[],
        metadata={"astro_events": events},
    )

    result = policy.build(None, evidence=evidence)
    assert "Vénus Trigone Saturne" in result["aspects"]
    assert "Mercure Sextile Jupiter" in result["aspects"]


def test_extract_ingress(policy):
    events = [
        AstroEvent(
            event_type="moon_sign_ingress",
            ut_time=0.0,
            local_time=datetime(2026, 3, 19, 14, 35),
            body="moon",
            target="leo",
            aspect=None,
            orb_deg=None,
            priority=100,
            base_weight=1.0,
        )
    ]

    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[],
        metadata={"astro_events": events},
    )

    result = policy.build(None, evidence=evidence)
    assert len(result["ingresses"]) == 1
    assert result["ingresses"][0]["text"] == "Lune entre en Lion"
    assert result["ingresses"][0]["time"] == "14:35"


def test_fallback_none(policy):
    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[],
        metadata={"astro_events": []},
    )
    result = policy.build(None, evidence=evidence)
    assert result is None


def test_multi_aspects_limit(policy):
    planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter"]
    events = [
        AstroEvent(
            event_type="aspect",
            ut_time=0.0,
            local_time=datetime.now(),
            body=planets[i],
            target=planets[i + 1],
            aspect="conjunction",
            orb_deg=float(i),
            priority=i,
            base_weight=1.0,
        )
        for i in range(5)
    ]
    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[],
        metadata={"astro_events": events},
    )
    result = policy.build(None, evidence=evidence)
    assert len(result["aspects"]) == 4


def test_planet_positions(policy):
    # Mock evidence with planet_positions in metadata
    evidence = V3EvidencePack(
        version="1.0",
        generated_at=datetime.now(),
        day_profile={},
        themes={},
        time_windows=[],
        turning_points=[],
        metadata={"planet_positions": {"sun": "pis", "moon": "leo"}},
    )

    result = policy.build(None, evidence=evidence)
    assert "planet_positions" in result
    assert "Soleil en Poissons" in result["planet_positions"]
    assert "Lune en Lion" in result["planet_positions"]
