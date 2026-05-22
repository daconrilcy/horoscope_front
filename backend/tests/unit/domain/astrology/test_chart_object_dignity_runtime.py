"""Tests des projections dignity depuis le runtime chart-object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.dignities.chart_object_inputs import (
    DignityChartObjectSelector,
    DignityInputProjector,
    DignityPayloadEnricher,
    DignityPayloadProjector,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    ChartSectResult,
    EssentialDignityMatch,
    PlanetDignityResult,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition, PlanetPosition
from app.domain.astrology.runtime.chart_object_runtime_data import (
    DignityRuntimePayload,
    validate_dignity_payloads,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData


def _objects():
    """Construit des objets runtime couvrant candidats et non-candidats."""
    return build_chart_object_runtime_data(
        planet_positions=(
            PlanetPosition(
                planet_code="sun",
                longitude=120.0,
                sign_code="leo",
                house_number=10,
                speed_longitude=1.0,
                is_retrograde=False,
            ),
            PlanetPosition(
                planet_code="mars",
                longitude=15.0,
                sign_code="aries",
                house_number=6,
                speed_longitude=-0.2,
                is_retrograde=True,
            ),
        ),
        astral_points=(
            NatalAstralPointPosition(
                code="north_node",
                variant_code="true",
                longitude=27.0,
                sign="aries",
                degree_in_sign=27.0,
                house=2,
                calculation_source="simplified:node",
                is_physical_body=False,
            ),
        ),
        houses=tuple(
            HouseRuntimeData(number=number, cusp_longitude=float((number - 1) * 30))
            for number in range(1, 13)
        ),
    )


def _result(code: str, total: float = 7.0) -> PlanetDignityResult:
    """Construit un resultat de dignite stable pour les payloads."""
    chart_sect = ChartSectResult(
        chart_sect="day",
        sun_horizon_position="above_horizon",
        sun_above_horizon=True,
        calculation_basis="house",
        reference_system="whole_sign",
    )
    return PlanetDignityResult(
        planet_code=code,
        score_profile="traditional",
        tradition="hellenistic",
        reference_version="v1",
        sect="day",
        chart_sect=chart_sect,
        essential_score=5.0,
        accidental_score=2.0,
        total_score=total,
        functional_strength_score=3.0,
        expression_quality_score=4.0,
        intensity_score=5.0,
        essential_breakdown=(
            EssentialDignityMatch("domicile", 5.0, "essential", "rulership", "leo", 0, 30),
        ),
        accidental_breakdown=(
            AccidentalDignityMatch("angular", 2.0, "accidental", "angular house", "house"),
        ),
    )


def test_selector_uses_dignity_capability_only() -> None:
    """Le selector dignity ne depend pas du type d'objet."""
    selected = DignityChartObjectSelector().choose(_objects())

    assert [item.code for item in selected] == ["sun", "mars"]


def test_selector_rejects_duplicate_dignity_candidates() -> None:
    """Le selector dignity refuse les codes candidats ambigus."""
    chart_object = DignityChartObjectSelector().choose(_objects())[0]

    with pytest.raises(ValueError, match="duplicate dignity chart object: sun"):
        DignityChartObjectSelector().choose((chart_object, chart_object))


def test_selector_rejects_incomplete_dignity_candidate() -> None:
    """Le selector dignity valide les donnees minimales avant projection."""
    broken = replace(DignityChartObjectSelector().choose(_objects())[0], zodiac_position=None)

    with pytest.raises(ValueError, match="dignity candidate requires zodiac position: sun"):
        DignityChartObjectSelector().choose((broken,))


def test_input_projector_uses_chart_object_runtime_data() -> None:
    """Le projector d'entree lit les faits portes par le chart-object."""
    projected = DignityInputProjector().project_many(
        DignityChartObjectSelector().choose(_objects())
    )

    assert [item.planet_code for item in projected] == ["sun", "mars"]
    assert projected[0].sign_code == "leo"
    assert projected[0].house_number == 10


def test_payload_projector_copies_scores_without_recalculation() -> None:
    """Le payload copie les scores historiques sans recomposer le total."""
    payload = DignityPayloadProjector().project(_result("sun", total=99.0))

    assert payload.essential_score == 5.0
    assert payload.accidental_score == 2.0
    assert payload.total_score == 99.0
    assert payload.source == "dignities.planet_dignity_scoring_service"
    assert payload.essential_breakdown[0].source == "essential"


def test_enricher_returns_new_instances_and_preserves_other_payloads() -> None:
    """L'enricher rattache les payloads sans muter les objets d'origine."""
    objects = _objects()
    enriched = DignityPayloadEnricher().enrich(objects, (_result("sun"), _result("mars")))

    assert enriched is not objects
    assert enriched[0] is not objects[0]
    assert objects[0].payloads.dignity is None
    assert enriched[0].payloads.dignity is not None
    assert enriched[0].payloads.house_position == objects[0].payloads.house_position
    validate_dignity_payloads(enriched)


def test_invalid_dignity_runtime_inputs_fail_explicitly() -> None:
    """Un objet eligible incomplet produit une erreur explicite."""
    broken = _objects()[0]
    broken = type(broken)(
        code=broken.code,
        object_type=broken.object_type,
        display_name=broken.display_name,
        longitude=None,
        latitude=broken.latitude,
        zodiac_position=broken.zodiac_position,
        source=broken.source,
        capabilities=broken.capabilities,
        classifications=broken.classifications,
        payloads=broken.payloads,
    )

    with pytest.raises(ValueError, match="longitude"):
        DignityInputProjector().project(broken)


def test_enricher_rejects_unknown_dignity_result_target() -> None:
    """Un resultat qui ne cible aucun objet eligible echoue explicitement."""
    with pytest.raises(ValueError, match="unknown dignity result target: ghost"):
        DignityPayloadEnricher().enrich(
            _objects(),
            (_result("sun"), _result("mars"), _result("ghost")),
        )


def test_payload_contract_is_immutable_and_non_narrative() -> None:
    """Le payload dignity reste factuel, immuable et sans champ narratif."""
    payload = DignityRuntimePayload(
        essential_score=1.0,
        accidental_score=2.0,
        total_score=42.0,
        source="test",
    )

    with pytest.raises(FrozenInstanceError):
        payload.total_score = 0.0
    assert not {
        "interpretation",
        "narrative",
        "prompt",
        "llm",
        "meaning",
        "psychological",
        "reason",
    } & set(DignityRuntimePayload.__dataclass_fields__)
