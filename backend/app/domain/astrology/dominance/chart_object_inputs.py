# Projection des objets runtime vers les contrats de dominance astrologique.
"""Selectors, projectors et enrichers dominance pour les chart objects."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from app.domain.astrology.dominance.contracts import PlanetDominanceResult
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectMotionPayload,
    ChartObjectRuntimeData,
    ChartObjectVisibilityPayload,
    DignityRuntimePayload,
    DominanceBreakdownItem,
    DominanceRuntimePayload,
)


@dataclass(frozen=True, slots=True)
class DominanceChartObjectInput:
    """Donnees runtime d'un objet candidat au classement de dominance."""

    planet_code: str
    longitude: float
    house_number: int
    classifications: tuple[str, ...] = ()
    dignity: DignityRuntimePayload | None = None
    motion: ChartObjectMotionPayload | None = None
    visibility: ChartObjectVisibilityPayload | None = None


class DominanceChartObjectSelector:
    """Selectionne les objets candidats a la dominance par capacite."""

    def choose(
        self,
        objects: Sequence[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets eligibles apres controle des donnees runtime."""
        selected = tuple(item for item in objects if item.capabilities.supports_dominance)
        _ensure_unique_chart_object_codes(selected)
        for chart_object in selected:
            _validate_dominance_candidate(chart_object)
        return selected


class DominanceInputProjector:
    """Projette les objets runtime vers l'entree du moteur historique."""

    def project_many(
        self,
        objects: Sequence[ChartObjectRuntimeData],
    ) -> tuple[DominanceChartObjectInput, ...]:
        """Projette une sequence d'objets en entrees de dominance."""
        return tuple(self.project(item) for item in objects)

    def project(self, chart_object: ChartObjectRuntimeData) -> DominanceChartObjectInput:
        """Construit l'entree de dominance depuis les payloads runtime."""
        if not chart_object.capabilities.supports_dominance:
            raise ValueError(f"chart object does not support dominance: {chart_object.code}")
        if chart_object.longitude is None:
            raise ValueError(f"dominance input requires longitude: {chart_object.code}")
        if chart_object.payloads.house_position is None:
            raise ValueError(f"dominance input requires house position: {chart_object.code}")
        if chart_object.source.source_type.value != "ephemeris":
            raise ValueError(f"dominance input requires ephemeris source: {chart_object.code}")
        return DominanceChartObjectInput(
            planet_code=chart_object.code,
            longitude=chart_object.longitude,
            house_number=chart_object.payloads.house_position.house_number,
            classifications=chart_object.classifications,
            dignity=chart_object.payloads.dignity,
            motion=chart_object.payloads.motion,
            visibility=chart_object.payloads.visibility,
        )


class DominancePayloadProjector:
    """Projette les resultats de dominance sans recalculer la contribution."""

    def project(self, result: PlanetDominanceResult) -> DominanceRuntimePayload:
        """Construit le payload runtime depuis le resultat historique."""
        return DominanceRuntimePayload(
            contribution_score=result.total_score,
            rank=result.rank,
            contribution_breakdown=tuple(
                DominanceBreakdownItem(
                    factor_code=item.factor_code,
                    raw_value=item.raw_value,
                    normalized_value=item.normalized_value,
                    weight=item.weight,
                    weighted_score=item.weighted_score,
                )
                for item in result.factors
            ),
            factors=tuple(item.factor_code for item in result.factors),
            source="dominance.planet_dominance_engine",
        )


class DominancePayloadEnricher:
    """Ajoute immuablement les payloads dominance aux objets eligibles."""

    def __init__(self, projector: DominancePayloadProjector | None = None) -> None:
        self._projector = projector or DominancePayloadProjector()

    def enrich(
        self,
        objects: Sequence[ChartObjectRuntimeData],
        results: Sequence[PlanetDominanceResult],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne de nouveaux objets avec payloads dominance rattaches."""
        result_by_code = _index_results(results)
        consumed_codes: set[str] = set()
        enriched: list[ChartObjectRuntimeData] = []
        for chart_object in objects:
            if not chart_object.capabilities.supports_dominance:
                if chart_object.payloads.dominance is not None:
                    raise ValueError(
                        f"dominance payload requires dominance capability: {chart_object.code}"
                    )
                enriched.append(chart_object)
                continue
            if (
                chart_object.capabilities.supports_dignities
                and chart_object.payloads.dignity is None
            ):
                raise ValueError(
                    f"dominance enrichment requires dignity payload: {chart_object.code}"
                )
            result = result_by_code.get(chart_object.code)
            if result is None:
                raise ValueError(f"missing dominance result for chart object: {chart_object.code}")
            consumed_codes.add(chart_object.code)
            enriched.append(
                replace(
                    chart_object,
                    payloads=replace(
                        chart_object.payloads,
                        dominance=self._projector.project(result),
                    ),
                )
            )
        unknown_codes = sorted(set(result_by_code) - consumed_codes)
        if unknown_codes:
            raise ValueError(f"unknown dominance result target: {', '.join(unknown_codes)}")
        return tuple(enriched)


def _index_results(
    results: Sequence[PlanetDominanceResult],
) -> Mapping[str, PlanetDominanceResult]:
    """Indexe les resultats et refuse les doublons silencieux."""
    indexed: dict[str, PlanetDominanceResult] = {}
    for result in results:
        if indexed.get(result.planet_code) is not None:
            raise ValueError(f"duplicate dominance result: {result.planet_code}")
        indexed[result.planet_code] = result
    return indexed


def _ensure_unique_chart_object_codes(objects: Sequence[ChartObjectRuntimeData]) -> None:
    """Refuse une selection qui rendrait la dominance ambigue."""
    duplicated_codes = sorted(
        item_code
        for item_code, count in Counter(item.code for item in objects).items()
        if count > 1
    )
    if duplicated_codes:
        raise ValueError(f"duplicate dominance chart object: {', '.join(duplicated_codes)}")


def _validate_dominance_candidate(chart_object: ChartObjectRuntimeData) -> None:
    """Valide les faits minimaux requis avant projection dominance."""
    if chart_object.longitude is None:
        raise ValueError(f"dominance candidate requires longitude: {chart_object.code}")
    if chart_object.payloads.house_position is None:
        raise ValueError(f"dominance candidate requires house position: {chart_object.code}")
    if chart_object.source.source_type.value != "ephemeris":
        raise ValueError(f"dominance candidate requires ephemeris source: {chart_object.code}")
    if chart_object.capabilities.supports_dignities and chart_object.payloads.dignity is None:
        raise ValueError(f"dominance candidate requires dignity payload: {chart_object.code}")
