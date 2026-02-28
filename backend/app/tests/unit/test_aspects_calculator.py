"""Tests unitaires pour le calculateur d'aspects (stories 20-x, 24-1, 24-2).

Couvre:
- orb_used (déviation réelle) et orb_max (seuil résolu par priorité) [story 24-2]
- Résolution prioritaire: pair_override > luminary_override > default_orb [story 24-2 AC1]
- Serialisation AspectResult [story 24-1, 24-2]
"""
from app.domain.astrology.calculators.aspects import calculate_major_aspects
from app.domain.astrology.natal_calculation import AspectResult


def test_calculate_major_aspects_uses_default_orb_and_exposes_orb_used_and_orb_max() -> None:
    """Avec default_orb: orb_used = déviation réelle, orb_max = seuil résolu."""
    positions = [
        {"planet_code": "sun", "longitude": 0.0},
        {"planet_code": "mars", "longitude": 95.5},
    ]
    aspect_definitions = [
        {"code": "square", "angle": 90.0, "default_orb_deg": 6.0},
    ]

    result = calculate_major_aspects(positions, aspect_definitions)

    assert len(result) == 1
    assert result[0]["aspect_code"] == "square"
    assert result[0]["orb"] == 5.5       # backward compat: déviation réelle
    assert result[0]["orb_used"] == 5.5  # story 24-2: déviation réelle (renommé)
    assert result[0]["orb_max"] == 6.0   # story 24-2: seuil résolu (priorité)


def test_calculate_major_aspects_applies_luminaries_override() -> None:
    """Avec luminary override: orb_max = seuil luminaire, orb_used = déviation réelle."""
    positions = [
        {"planet_code": "sun", "longitude": 0.0},
        {"planet_code": "moon", "longitude": 97.0},
    ]
    aspect_definitions = [
        {
            "code": "square",
            "angle": 90.0,
            "default_orb_deg": 6.0,
            "orb_luminaries": 8.0,
        },
    ]

    result = calculate_major_aspects(positions, aspect_definitions)

    assert len(result) == 1
    assert result[0]["orb"] == 7.0       # backward compat: déviation réelle
    assert result[0]["orb_used"] == 7.0  # déviation réelle
    assert result[0]["orb_max"] == 8.0   # seuil = luminary override


def test_calculate_major_aspects_applies_pair_override_with_priority() -> None:
    """pair_override prend la priorité sur luminary_override: orb_max = pair override."""
    positions = [
        {"planet_code": "sun", "longitude": 0.0},
        {"planet_code": "mercury", "longitude": 98.5},
    ]
    aspect_definitions = [
        {
            "code": "square",
            "angle": 90.0,
            "default_orb_deg": 6.0,
            "orb_luminaries": 8.0,
            "orb_pair_overrides": {"mercury-sun": 9.0},
        },
    ]

    result = calculate_major_aspects(positions, aspect_definitions)

    assert len(result) == 1
    # mercury-sun normalized to mercury-sun (alphabetical)
    assert result[0]["planet_a"] == "mercury"
    assert result[0]["planet_b"] == "sun"
    assert result[0]["orb"] == 8.5       # backward compat: déviation réelle
    assert result[0]["orb_used"] == 8.5  # déviation réelle  
    assert result[0]["orb_max"] == 9.0   # seuil = pair override (priorité maximale)


def test_aspect_result_serialization_exposes_orb_orb_used_and_orb_max() -> None:
    """AspectResult expose orb (compat), orb_used (déviation) et orb_max (seuil)."""
    aspect = AspectResult(
        aspect_code="square",
        planet_a="mars",
        planet_b="sun",
        angle=90.0,
        orb=3.5,
        orb_used=3.5,
        orb_max=6.0,
    )

    payload = aspect.model_dump()
    assert payload["planet_a"] == "mars"
    assert payload["planet_b"] == "sun"
    assert payload["orb"] == 3.5
    assert payload["orb_used"] == 3.5
    assert payload["orb_max"] == 6.0
