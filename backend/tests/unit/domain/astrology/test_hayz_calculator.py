"""Tests des conditions avancees de secte."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_hayz_and_out_of_sect_are_projected_from_canonical_sect_facts() -> None:
    """Les conditions avancees de secte consomment PlanetSectCondition."""
    conditions, _profiles = advanced_engine_result(
        (position("sun", "leo", house_number=10), position("mars", "aries")),
        (
            dignity(
                "sun",
                "hayz",
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
            dignity(
                "mars",
                intrinsic_sect="nocturnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert [(item.source_planet_code, item.condition_code) for item in conditions] == [
        ("mars", "out_of_sect"),
        ("sun", "hayz"),
    ]
    assert {item.condition_type_code for item in conditions} == {"hayz", "out_of_sect"}


def test_hayz_requires_in_sect_even_when_non_sect_factors_match() -> None:
    """Hayz reste faux quand seule la precondition canonique de secte echoue."""
    conditions, _profiles = advanced_engine_result(
        (position("moon", "cancer"),),
        (
            dignity(
                "moon",
                "hayz",
                intrinsic_sect="nocturnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert [item.condition_code for item in conditions] == ["out_of_sect"]
