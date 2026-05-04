"""Verifie la projection publique des fondations astrologiques."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.domain.prediction.public_projection import PublicAstroFoundationPolicy


def test_astro_foundation_key_movements_limit():
    policy = PublicAstroFoundationPolicy()

    events = []
    for i in range(10):
        e = MagicMock()
        e.body = "mars"
        e.event_type = "aspect"
        e.priority = 60
        e.aspect = "trine"
        e.target = "venus"
        e.orb_deg = 1.0
        events.append(e)

    evidence = MagicMock()
    evidence.metadata = {"astro_events": events}

    day_climate = {"label": "Stable"}
    result = policy.build(
        MagicMock(), day_climate=day_climate, domain_ranking=[], evidence=evidence
    )

    assert len(result["key_movements"]) == 5
    assert len(result["dominant_aspects"]) == 4


def test_astro_foundation_tonality():
    policy = PublicAstroFoundationPolicy()

    e = MagicMock()
    e.body = "mars"
    e.event_type = "aspect"
    e.priority = 60
    e.aspect = "square"  # tonality: ajustement
    e.target = "venus"
    e.orb_deg = 1.0

    evidence = MagicMock()
    evidence.metadata = {"astro_events": [e]}

    day_climate = {"label": "Stable"}
    result = policy.build(
        MagicMock(), day_climate=day_climate, domain_ranking=[], evidence=evidence
    )

    assert result["dominant_aspects"][0]["tonality"] == "ajustement"


def test_astro_foundation_activated_houses():
    policy = PublicAstroFoundationPolicy()

    domain_ranking = [{"key": "pro_ambition", "label": "Pro"}]

    e = MagicMock()
    e.body = "sun"
    e.event_type = "transit_to_natal"
    e.priority = 80
    e.target = None

    evidence = MagicMock()
    evidence.metadata = {"astro_events": [e]}

    day_climate = {"label": "Stable"}
    result = policy.build(
        MagicMock(),
        day_climate=day_climate,
        domain_ranking=domain_ranking,
        evidence=evidence,
    )

    assert result["activated_houses"][0]["house_number"] == 10
    assert result["activated_houses"][0]["house_label"] == "Maison X"


def test_astro_foundation_reads_detected_events_from_engine_output():
    policy = PublicAstroFoundationPolicy()
    event = SimpleNamespace(
        body="mars",
        event_type="aspect_exact_to_angle",
        priority=80,
        aspect="conjunction",
        target="mc",
        orb_deg=0.2,
    )
    engine_output = SimpleNamespace(core=SimpleNamespace(detected_events=[event]))

    result = policy.build(
        MagicMock(),
        day_climate={"label": "Stable"},
        domain_ranking=[],
        engine_output=engine_output,
    )

    assert result is not None
    assert result["key_movements"][0]["event_type"] == "aspect_exact_to_angle"
    assert result["dominant_aspects"][0]["aspect_type"] == "Conjonction"
    assert result["dominant_aspects"][0]["planet_a"] == "Mars"
    assert result["dominant_aspects"][0]["planet_b"] == "Mc"


def test_astro_foundation_recognizes_all_exact_aspect_event_types():
    policy = PublicAstroFoundationPolicy()
    exact_types = [
        "aspect_exact_to_angle",
        "aspect_exact_to_luminary",
        "aspect_exact_to_personal",
    ]
    events = [
        SimpleNamespace(
            body="moon",
            event_type=event_type,
            priority=70,
            aspect="trine",
            target="venus",
            orb_deg=float(index + 1),
        )
        for index, event_type in enumerate(exact_types)
    ]
    engine_output = SimpleNamespace(core=SimpleNamespace(events=events))

    result = policy.build(
        MagicMock(),
        day_climate={"label": "Stable"},
        domain_ranking=[],
        engine_output=engine_output,
    )

    assert [movement["event_type"] for movement in result["key_movements"]] == exact_types
    assert len(result["dominant_aspects"]) == len(exact_types)
    assert {aspect["tonality"] for aspect in result["dominant_aspects"]} == {"fluidité"}
