"""Tests des conditions aspectuelles avancees."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    aspect,
    dignity,
    position,
)


def test_aspect_condition_detector_maps_runtime_dignity_types() -> None:
    """Les types accidentels aspectuels deviennent des conditions avancees."""
    conditions, _profiles = advanced_engine_result(
        (
            position("moon", "cancer"),
            position("jupiter", "pisces"),
            position("saturn", "capricorn"),
        ),
        (
            dignity("moon", "benefic_aspected"),
            dignity("jupiter", "malefic_aspected"),
            dignity("saturn", "besieged_by_malefics"),
        ),
        (aspect("moon", "jupiter"), aspect("jupiter", "saturn")),
    )

    assert {(item.source_planet_code, item.condition_code) for item in conditions} == {
        ("moon", "bonification"),
        ("jupiter", "maltreatment"),
        ("saturn", "besiegement"),
    }
