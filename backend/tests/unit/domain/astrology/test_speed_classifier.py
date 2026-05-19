"""Tests des conditions avancees de vitesse."""

from __future__ import annotations

from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_speed_classifier_emits_stationary_fast_and_slow_conditions() -> None:
    """Les dignites de mouvement sont converties en conditions avancees."""
    conditions, _profiles = advanced_engine_result(
        (
            position("mercury", "gemini"),
            position("venus", "taurus"),
            position("saturn", "capricorn", is_retrograde=True),
        ),
        (
            dignity("mercury", "swift_motion"),
            dignity("venus", "slow_motion"),
            dignity("saturn", "stationary"),
        ),
    )

    assert {item.condition_code for item in conditions} == {
        "fast_motion",
        "slow_motion",
        "stationary_retrograde",
    }
    stationary = next(item for item in conditions if item.condition_code == "stationary_retrograde")
    assert stationary.condition_type_code == "stationary"
