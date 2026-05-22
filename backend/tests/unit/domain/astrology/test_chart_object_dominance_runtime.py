"""Tests des projections dominance depuis le runtime chart-object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.dominance.chart_object_inputs import (
    DominanceChartObjectSelector,
    DominanceInputProjector,
    DominancePayloadEnricher,
    DominancePayloadProjector,
)
from app.domain.astrology.dominance.contracts import (
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition, PlanetPosition
from app.domain.astrology.runtime.chart_object_runtime_data import (
    DignityRuntimePayload,
    DominanceRuntimePayload,
    validate_dominance_payloads,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData


def _objects():
    """Construit des objets runtime couvrant dominance et exclusions."""
    return build_chart_object_runtime_data(
        planet_positions=(
            PlanetPosition(
                planet_code="sun",
                longitude=120.0,
                sign_code="leo",
                house_number=10,
            ),
            PlanetPosition(
                planet_code="mars",
                longitude=15.0,
                sign_code="aries",
                house_number=6,
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


def _dominance_ready_objects():
    """Ajoute les payloads dignity requis avant selection dominance."""
    return tuple(
        replace(
            item,
            payloads=replace(
                item.payloads,
                dignity=DignityRuntimePayload(
                    essential_score=1.0,
                    accidental_score=2.0,
                    total_score=3.0,
                    source="test",
                ),
            ),
        )
        if item.capabilities.supports_dignities
        else item
        for item in _objects()
    )


def _result(code: str, total: float = 0.75, rank: int = 1) -> PlanetDominanceResult:
    """Construit un resultat de dominance stable pour les payloads."""
    return PlanetDominanceResult(
        planet_code=code,
        total_score=total,
        rank=rank,
        dominance_level="high",
        factors=(
            PlanetDominanceFactor(
                factor_code="chart_ruler",
                raw_value=1.0,
                normalized_value=1.0,
                weight=1.4,
                weighted_score=1.4,
                reason="chart ruler",
            ),
        ),
        explanation_facts=("chart ruler",),
    )


def test_selector_uses_dominance_capability_only() -> None:
    """Le selector dominance ne depend pas du type d'objet."""
    selected = DominanceChartObjectSelector().choose(_dominance_ready_objects())

    assert [item.code for item in selected] == ["sun", "mars"]


def test_selector_rejects_duplicate_dominance_candidates() -> None:
    """Le selector dominance refuse les codes candidats ambigus."""
    chart_object = DominanceChartObjectSelector().choose(_dominance_ready_objects())[0]

    with pytest.raises(ValueError, match="duplicate dominance chart object: sun"):
        DominanceChartObjectSelector().choose((chart_object, chart_object))


def test_selector_requires_dignity_payload_for_dignity_capable_candidate() -> None:
    """La dominance ne contourne pas la phase dignity quand elle est applicable."""
    with pytest.raises(ValueError, match="dominance candidate requires dignity payload: sun"):
        DominanceChartObjectSelector().choose(_objects())


def test_input_projector_uses_chart_object_runtime_data() -> None:
    """Le projector d'entree lit longitude et maison du chart-object."""
    projected = DominanceInputProjector().project_many(
        DominanceChartObjectSelector().choose(_dominance_ready_objects())
    )

    assert [item.planet_code for item in projected] == ["sun", "mars"]
    assert projected[0].house_number == 10
    assert projected[0].dignity is not None
    assert projected[0].classifications == ("luminary",)


def test_payload_projector_copies_contribution_without_recalculation() -> None:
    """Le payload copie le score de dominance historique comme contribution."""
    payload = DominancePayloadProjector().project(_result("sun", total=0.42))

    assert payload.contribution_score == 0.42
    assert payload.rank == 1
    assert payload.factors == ("chart_ruler",)
    assert payload.contribution_breakdown[0].factor_code == "chart_ruler"
    assert payload.source == "dominance.planet_dominance_engine"


def test_enricher_returns_new_instances() -> None:
    """L'enricher rattache les payloads sans muter les objets d'origine."""
    objects = _dominance_ready_objects()
    enriched = DominancePayloadEnricher().enrich(
        objects,
        (_result("sun", rank=1), _result("mars", total=0.25, rank=2)),
    )

    assert enriched is not objects
    assert enriched[0] is not objects[0]
    assert objects[0].payloads.dominance is None
    assert enriched[0].payloads.dominance is not None
    validate_dominance_payloads(enriched)


def test_enricher_requires_dignity_payload_before_dominance_payload() -> None:
    """L'enricher dominance ne contourne pas les payloads dignity applicables."""
    with pytest.raises(ValueError, match="dominance enrichment requires dignity payload: sun"):
        DominancePayloadEnricher().enrich(
            _objects(),
            (_result("sun", rank=1), _result("mars", rank=2)),
        )


def test_invalid_dominance_runtime_inputs_fail_explicitly() -> None:
    """Un objet eligible incomplet produit une erreur explicite."""
    broken = replace(_dominance_ready_objects()[0], longitude=None)

    with pytest.raises(ValueError, match="longitude"):
        DominanceInputProjector().project(broken)


def test_enricher_rejects_unknown_dominance_result_target() -> None:
    """Un resultat qui ne cible aucun objet eligible echoue explicitement."""
    with pytest.raises(ValueError, match="unknown dominance result target: ghost"):
        DominancePayloadEnricher().enrich(
            _dominance_ready_objects(),
            (_result("sun", rank=1), _result("mars", rank=2), _result("ghost", rank=3)),
        )


def test_payload_contract_is_immutable_and_non_narrative() -> None:
    """Le payload dominance reste factuel, immuable et sans champ narratif."""
    payload = DominanceRuntimePayload(
        contribution_score=0.5,
        source="test",
        rank=1,
    )

    with pytest.raises(FrozenInstanceError):
        payload.contribution_score = 0.0
    assert not {
        "interpretation",
        "narrative",
        "prompt",
        "llm",
        "meaning",
        "psychological",
        "reason",
    } & set(DominanceRuntimePayload.__dataclass_fields__)
