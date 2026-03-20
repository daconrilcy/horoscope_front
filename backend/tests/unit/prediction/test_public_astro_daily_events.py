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


def test_self_aspects_excluded(policy):
    """Aspect where body == target (e.g. Moon square natal Moon) must be filtered out."""
    events = [
        AstroEvent(
            event_type="aspect_exact_to_luminary",
            ut_time=0.0,
            local_time=datetime.now(),
            body="moon",
            target="moon",  # self-aspect — should be excluded
            aspect="square",
            orb_deg=0.1,
            priority=80,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="aspect_exact_to_personal",
            ut_time=0.0,
            local_time=datetime.now(),
            body="moon",
            target="saturn",
            aspect="sextile",
            orb_deg=0.8,
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
    assert len(result["aspects"]) == 1
    assert "Lune Carré Lune" not in result["aspects"]
    assert "Lune Sextile Saturne" in result["aspects"]


def test_extract_enriched_events(policy):
    events = [
        AstroEvent(
            event_type="solar_return",
            ut_time=0.0,
            local_time=datetime.now(),
            body="sun",
            target=None,
            aspect=None,
            orb_deg=0.1,
            priority=95,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="progression_aspect",
            ut_time=0.0,
            local_time=datetime.now(),
            body="prog_sun",
            target="moon",
            aspect="trine",
            orb_deg=0.5,
            priority=65,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="node_conjunction",
            ut_time=0.0,
            local_time=datetime.now(),
            body="venus",
            target="north_node",
            aspect="conjunction",
            orb_deg=0.2,
            priority=60,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="sky_aspect",
            ut_time=0.0,
            local_time=datetime.now(),
            body="jupiter",
            target="saturn",
            aspect="sextile",
            orb_deg=0.1,
            priority=70,
            base_weight=1.0,
        ),
        AstroEvent(
            event_type="fixed_star_conjunction",
            ut_time=0.0,
            local_time=datetime.now(),
            body="moon",
            target="regulus",
            aspect="conjunction",
            orb_deg=0.3,
            priority=45,
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

    assert "Retour Solaire (votre anniversaire astrologique)" in result["returns"]
    assert "Soleil Progressé Trigone Lune (progression)" in result["progressions"]
    assert "Vénus Conjonction Nœud Nord (Rahu)" in result["nodes"]
    assert "Jupiter Sextile Saturne" in result["sky_aspects"]
    assert "Lune conjoint à l'étoile Régulus" in result["fixed_stars"]
