"""Tests du projector d'objets interpretables chart-object."""

from __future__ import annotations

import pytest

from app.domain.astrology.interpretation.chart_object_interpretation_projector import (
    ChartObjectInterpretationProjector,
)
from app.domain.astrology.runtime.chart_object_runtime_data import ZodiacPositionRuntimeData
from tests.unit.domain.astrology.interpretation.test_support import interpretable_chart_object


def test_projector_requires_zodiac_position() -> None:
    """Un objet interpretable sans position zodiacale produit une erreur explicite."""
    chart_object = interpretable_chart_object(
        "mars",
        zodiac_position=ZodiacPositionRuntimeData(sign_code="aries", degree_in_sign=1.0),
        with_payloads=False,
    )
    chart_object = chart_object.__class__(
        code=chart_object.code,
        object_type=chart_object.object_type,
        display_name=chart_object.display_name,
        longitude=chart_object.longitude,
        latitude=chart_object.latitude,
        zodiac_position=None,
        source=chart_object.source,
        capabilities=chart_object.capabilities,
        classifications=chart_object.classifications,
        payloads=chart_object.payloads,
    )

    with pytest.raises(ValueError, match="requires zodiac position"):
        ChartObjectInterpretationProjector().project(chart_object)


def test_projector_maps_motion_visibility_payloads_without_recalculation() -> None:
    """Motion et visibilite sont copiees depuis les payloads existants."""
    projected = ChartObjectInterpretationProjector().project(interpretable_chart_object())

    assert projected.motion is not None
    assert projected.motion.source == "fixture.motion"
    assert projected.visibility is not None
    assert projected.visibility.source == "fixture.visibility"


def test_projector_maps_dignity_dominance_payloads_without_recalculation() -> None:
    """Dignite et dominance objet sont copiees depuis les payloads existants."""
    projected = ChartObjectInterpretationProjector().project(interpretable_chart_object())

    assert projected.dignity is not None
    assert projected.dignity.total_score == 3.0
    assert projected.dominance is not None
    assert projected.dominance.score == 0.82
    assert projected.dominance.factors == ("angularity",)


def test_projector_maps_house_rulership_payloads_without_resolver() -> None:
    """Maisons et maitrises sont copiees depuis les payloads existants."""
    projected = ChartObjectInterpretationProjector().project(interpretable_chart_object())

    assert projected.house_number == 1
    assert projected.house_modality == "angular"
    assert projected.rulership is not None
    assert projected.rulership.rules_houses == (1,)
    assert projected.rulership.is_ascendant_ruler is True


def test_projector_maps_fixed_star_contacts() -> None:
    """Les contacts fixed star sont copies depuis les payloads existants."""
    projected = ChartObjectInterpretationProjector().project(interpretable_chart_object())

    assert len(projected.fixed_star_contacts) == 1
    assert projected.fixed_star_contacts[0].fixed_star_code == "regulus"
    assert projected.fixed_star_contacts[0].target_code == "mars"
