"""Tests du selector d'objets interpretables chart-object."""

from __future__ import annotations

import pytest

from app.domain.astrology.interpretation.chart_object_interpretation_selector import (
    ChartObjectInterpretationSelector,
)
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


def test_selector_excludes_non_interpretable_objects() -> None:
    """Les objets sans capacite d'interpretation sont exclus."""
    selected = ChartObjectInterpretationSelector().select(
        (
            interpretable_chart_object("mars"),
            interpretable_chart_object("regulus", supports_interpretation=False),
        )
    )

    assert [item.code for item in selected] == ["mars"]


def test_selector_preserves_input_order() -> None:
    """L'ordre de `chart_objects` reste stable."""
    selected = ChartObjectInterpretationSelector().select(
        (
            interpretable_chart_object("venus"),
            interpretable_chart_object("mars"),
            interpretable_chart_object("moon"),
        )
    )

    assert [item.code for item in selected] == ["venus", "mars", "moon"]


def test_selector_rejects_duplicate_interpretable_codes() -> None:
    """Les codes interpretables dupliques sont refuses explicitement."""
    with pytest.raises(ValueError, match="duplicate interpretation-capable"):
        ChartObjectInterpretationSelector().select(
            (
                interpretable_chart_object("mars"),
                interpretable_chart_object("mars"),
            )
        )
