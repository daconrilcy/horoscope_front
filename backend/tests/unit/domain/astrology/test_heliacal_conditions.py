"""Tests des conditions solaires avancees."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_heliacal_and_orientation_conditions_are_projected() -> None:
    """Les conditions solaires restent des faits rattaches au Soleil."""
    conditions, _profiles = advanced_engine_result(
        (position("mercury", "gemini"), position("venus", "taurus")),
        (
            dignity("mercury", "oriental", "heliacal_rising"),
            dignity("venus", "occidental", "heliacal_setting"),
        ),
    )

    assert {item.condition_code for item in conditions} == {
        "oriental",
        "heliacal_rising",
        "occidental",
        "heliacal_setting",
    }
    assert all(item.target_planet_code == "sun" for item in conditions)
