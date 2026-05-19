"""Tests des conditions aspectuelles avancees."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    aspect,
    position,
)


def test_aspect_conditions_use_runtime_natures_and_configured_orbs() -> None:
    """Bonification et maltreatment viennent des aspects valides et des natures runtime."""
    conditions, _profiles = advanced_engine_result(
        (
            position("moon", "cancer"),
            position("jupiter", "pisces"),
            position("mars", "aries"),
        ),
        (),
        (
            aspect("moon", "jupiter", orb_used=1.0, orb_max=6.0),
            aspect("moon", "mars", orb_used=2.0, orb_max=6.0),
            aspect("jupiter", "mars", orb_used=9.0, orb_max=6.0),
        ),
    )

    emitted = {
        (item.source_planet_code, item.condition_code, item.target_planet_code)
        for item in conditions
    }

    assert ("moon", "bonification", "jupiter") in emitted
    assert ("moon", "maltreatment", "mars") in emitted
    assert ("jupiter", "maltreatment", "mars") not in emitted


def test_besiegement_uses_longitudinal_enclosure_by_runtime_malefics() -> None:
    """Le besiegement detecte une planete sur l'arc court entre deux malefiques."""
    conditions, _profiles = advanced_engine_result(
        (
            position("mars", "aries", longitude=10.0),
            position("moon", "aries", longitude=20.0),
            position("saturn", "taurus", longitude=30.0),
            position("sun", "libra", longitude=200.0),
        ),
        (),
    )

    emitted = {
        (item.source_planet_code, item.condition_code, item.target_planet_code)
        for item in conditions
    }

    assert ("moon", "besiegement", "mars,saturn") in emitted
    assert ("sun", "besiegement", "mars,saturn") not in emitted
