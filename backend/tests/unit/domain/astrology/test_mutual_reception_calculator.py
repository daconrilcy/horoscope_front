"""Tests des receptions mutuelles avancees."""

from __future__ import annotations

from app.domain.astrology.advanced_conditions.advanced_condition_engine import (
    AdvancedConditionEngine,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.advanced_condition_test_helpers import dignity, position, profile


def test_mutual_reception_by_domicile_maps_to_runtime_parent_type() -> None:
    """Une reception mutuelle par domicile produit un sous-code stable."""
    conditions, _profiles = AdvancedConditionEngine().calculate(
        runtime_reference=complete_reference(),
        planet_positions=(
            position("mars", "taurus"),
            position("venus", "aries"),
        ),
        aspects=(),
        dignities=(dignity("mars"), dignity("venus")),
        condition_profiles=(profile("mars"), profile("venus")),
    )

    receptions = [
        item for item in conditions if item.condition_code == "mutual_reception_by_domicile"
    ]

    assert {(item.source_planet_code, item.target_planet_code) for item in receptions} == {
        ("mars", "venus"),
        ("venus", "mars"),
    }
    assert {item.condition_type_code for item in receptions} == {"mutual_reception"}
