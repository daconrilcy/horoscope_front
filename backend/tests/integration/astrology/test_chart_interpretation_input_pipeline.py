"""Test d'integration de l'input interpretatif dans le pipeline natal."""

from __future__ import annotations

from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.natal_calculation import build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_natal_pipeline_builds_interpretation_input_from_chart_objects() -> None:
    """Le pipeline natal fournit les faits necessaires au builder central."""
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

    interpretation_input = ChartInterpretationInputBuilder().build(result)

    assert interpretation_input.objects
    assert interpretation_input.aspects
    assert interpretation_input.dignities
    assert interpretation_input.house_positions
    assert interpretation_input.rulerships
    assert interpretation_input.dominance
    assert result.interpretation_adapter is not None
    assert result.planet_positions
    assert result.houses
    assert result.dignities
