from unittest.mock import MagicMock

from app.prediction.public_projection import PublicAstroFoundationPolicy


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
