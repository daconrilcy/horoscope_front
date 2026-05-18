"""Tests de l'option d'inclusion des points astraux dans les aspects natals."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _build(include_points_in_aspects: bool, monkeypatch):
    """Construit un thème stable avec ou sans points dans les aspects."""
    captured_codes: list[tuple[str, ...]] = []

    def _spy_calculate_major_aspects(positions, *args, **kwargs):
        captured_codes.append(tuple(position.code for position in positions))
        return []

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation.calculate_major_aspects",
        _spy_calculate_major_aspects,
    )
    return build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
        include_points_in_aspects=include_points_in_aspects,
    ), captured_codes


def test_points_are_excluded_from_aspects_by_default(monkeypatch) -> None:
    """Le comportement historique ne calcule pas d'aspects avec les points."""
    result, captured_codes = _build(include_points_in_aspects=False, monkeypatch=monkeypatch)

    participants = set(captured_codes[0])
    assert "north_node" not in participants
    assert "south_node" not in participants
    assert result.aspects == []


def test_points_can_be_included_in_aspects_explicitly(monkeypatch) -> None:
    """L'option explicite ajoute les points au pool aspectable."""
    result, captured_codes = _build(include_points_in_aspects=True, monkeypatch=monkeypatch)

    participants = set(captured_codes[0])
    assert {"north_node", "south_node"} & participants
    assert result.aspects == []


def test_points_can_produce_real_aspect_when_enabled(monkeypatch) -> None:
    """Un point inclus participe réellement au calcul d'aspects existant."""

    def _positions(*args, **kwargs):
        return [
            {"planet_code": "sun", "longitude": 10.0, "sign_code": "aries"},
            {"planet_code": "moon", "longitude": 100.0, "sign_code": "cancer"},
        ]

    def _points(**kwargs):
        return [
            {
                "code": "north_node",
                "variant_code": "true",
                "planet_code": "north_node",
                "longitude": 10.0,
                "sign": "aries",
                "degree_in_sign": 10.0,
                "house": 1,
                "calculation_source": "test:north_node",
                "is_physical_body": False,
            }
        ]

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation.calculate_planet_positions", _positions
    )
    monkeypatch.setattr("app.domain.astrology.natal_calculation.calculate_astral_points", _points)

    disabled = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
        include_points_in_aspects=False,
    )
    enabled = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
        include_points_in_aspects=True,
    )

    disabled_pairs = {(aspect.planet_a, aspect.planet_b) for aspect in disabled.aspects}
    enabled_pairs = {(aspect.planet_a, aspect.planet_b) for aspect in enabled.aspects}
    assert ("north_node", "sun") not in disabled_pairs
    assert ("north_node", "sun") in enabled_pairs
