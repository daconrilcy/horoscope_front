"""Tests du moteur de conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.advanced_conditions.contracts import PlanetConditionAxisImpact
from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_advanced_condition_contracts_are_immutable() -> None:
    """Les impacts d'axes avances ne sont pas mutables."""
    impact = PlanetConditionAxisImpact(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    with pytest.raises(FrozenInstanceError):
        impact.functional_strength_delta = 2.0


def test_advanced_condition_engine_enriches_profiles_without_replacing_them() -> None:
    """Le moteur ajoute breakdown et faits avances aux profils existants."""
    conditions, profiles = advanced_engine_result(
        (position("sun", "leo"),),
        (dignity("sun", "hayz"),),
    )

    assert len(conditions) == 1
    profile = profiles[0]
    assert profile.planet_code == "sun"
    assert profile.breakdown[0].dignity_family == "advanced"
    assert profile.breakdown[0].dignity_type_code == "hayz"
    assert profile.explanation_facts[0].fact_type == "advanced_condition"
    assert profile.ranking_score > 1.0
