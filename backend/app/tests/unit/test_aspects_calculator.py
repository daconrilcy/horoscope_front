from app.domain.astrology.calculators.aspects import calculate_major_aspects
from app.domain.astrology.natal_calculation import AspectResult


def test_calculate_major_aspects_uses_default_orb_and_exposes_orb_used() -> None:
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
    assert result[0]["orb"] == 5.5
    assert result[0]["orb_used"] == 6.0


def test_calculate_major_aspects_applies_luminaries_override() -> None:
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
    assert result[0]["orb"] == 7.0
    assert result[0]["orb_used"] == 8.0


def test_calculate_major_aspects_applies_pair_override_with_priority() -> None:
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
            "orb_pair_overrides": {"sun-mercury": 9.0},
        },
    ]

    result = calculate_major_aspects(positions, aspect_definitions)

    assert len(result) == 1
    assert result[0]["orb"] == 8.5
    assert result[0]["orb_used"] == 9.0


def test_aspect_result_serialization_exposes_orb_and_orb_used() -> None:
    aspect = AspectResult(
        aspect_code="square",
        planet_a="sun",
        planet_b="mars",
        angle=90.0,
        orb=3.5,
        orb_used=6.0,
    )

    payload = aspect.model_dump()
    assert payload["orb"] == 3.5
    assert payload["orb_used"] == 6.0
