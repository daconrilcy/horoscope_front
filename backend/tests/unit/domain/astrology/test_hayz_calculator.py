"""Tests des conditions avancees de secte."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_hayz_and_out_of_sect_are_projected_from_accidental_dignities() -> None:
    """Les conditions de secte viennent des resultats de dignites deja calcules."""
    conditions, _profiles = advanced_engine_result(
        (position("sun", "leo"), position("mars", "aries")),
        (dignity("sun", "hayz"), dignity("mars", "out_of_sect")),
    )

    assert [(item.source_planet_code, item.condition_code) for item in conditions] == [
        ("mars", "out_of_sect"),
        ("sun", "hayz"),
    ]
    assert {item.condition_type_code for item in conditions} == {"hayz", "out_of_sect"}
