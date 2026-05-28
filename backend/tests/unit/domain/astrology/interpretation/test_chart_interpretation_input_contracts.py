"""Tests des contrats d'entree interpretative chart-object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    BirthContextInterpretationRuntimeData,
    BirthPlaceInterpretationRuntimeData,
    BirthPrecisionInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    ChartObjectInterpretationRuntimeData,
    DignityInterpretationRuntimeData,
    MotionInterpretationRuntimeData,
)


def test_chart_interpretation_input_contracts_are_immutable_dataclasses() -> None:
    """Les contrats principaux restent immuables et structures."""
    input_data = ChartInterpretationInputRuntimeData(
        chart_id=None,
        chart_type="natal",
        locale=None,
        objects=(),
        aspects=(),
        dignities=(),
        house_positions=(),
        rulerships=(),
        dominance=(),
        fixed_star_contacts=(),
    )

    assert is_dataclass(ChartInterpretationInputRuntimeData)
    assert is_dataclass(BirthContextInterpretationRuntimeData)
    assert is_dataclass(ChartObjectInterpretationRuntimeData)
    assert hasattr(ChartInterpretationInputRuntimeData, "__slots__")
    with pytest.raises(FrozenInstanceError):
        input_data.chart_type = "transit"  # type: ignore[misc]
    assert isinstance(input_data.birth_context.birth_place, BirthPlaceInterpretationRuntimeData)
    assert isinstance(
        input_data.birth_context.precision,
        BirthPrecisionInterpretationRuntimeData,
    )


def test_subcontracts_do_not_expose_forbidden_text_fields() -> None:
    """Les sous-contrats restent factuels et sans champs de texte redactionnel."""
    forbidden = {
        "meaning",
        "narrative",
        "psychological",
        "prompt",
        "llm",
        "good",
        "bad",
        "positive_text",
        "negative_text",
    }

    for contract in (
        ChartInterpretationInputRuntimeData,
        ChartObjectInterpretationRuntimeData,
        DignityInterpretationRuntimeData,
        MotionInterpretationRuntimeData,
    ):
        assert forbidden.isdisjoint({field.name for field in fields(contract)})
