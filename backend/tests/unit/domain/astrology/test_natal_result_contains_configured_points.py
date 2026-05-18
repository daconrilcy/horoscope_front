"""Tests du branchement des points astraux dans le résultat natal."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_natal_result_contains_configured_astral_points() -> None:
    """Le résultat natal expose `points[]` normalisé sans champs plats."""
    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )

    by_code = {point.code: point for point in result.points}
    assert set(by_code) == {"north_node", "south_node"}
    assert by_code["north_node"].variant_code == "true"
    assert by_code["north_node"].sign
    assert 0.0 <= by_code["north_node"].degree_in_sign < 30.0
    assert by_code["north_node"].house is not None
    assert not hasattr(result, "true_node")
    assert not hasattr(result, "mean_node")
    assert not hasattr(result, "lilith")
