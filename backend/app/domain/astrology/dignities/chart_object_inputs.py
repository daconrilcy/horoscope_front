# Projection des objets runtime vers les contrats de dignite astrologique.
"""Selectors, projectors et enrichers dignity pour les chart objects."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace

from app.domain.astrology.dignities.contracts import PlanetDignityInput, PlanetDignityResult
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    DignityBreakdownItem,
    DignityRuntimePayload,
)


class DignityChartObjectSelector:
    """Selectionne les objets eligibles aux dignites par capacite declaree."""

    def choose(
        self,
        objects: Sequence[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets eligibles apres controle des donnees minimales."""
        selected = tuple(item for item in objects if item.capabilities.supports_dignities)
        _ensure_unique_chart_object_codes(selected)
        for chart_object in selected:
            _validate_dignity_candidate(chart_object)
        return selected


class DignityInputProjector:
    """Projette un objet runtime vers l'entree du calculateur de dignite."""

    def project_many(
        self,
        objects: Sequence[ChartObjectRuntimeData],
    ) -> tuple[PlanetDignityInput, ...]:
        """Projette une sequence d'objets en entrees de dignite."""
        return tuple(self.project(item) for item in objects)

    def project(self, chart_object: ChartObjectRuntimeData) -> PlanetDignityInput:
        """Construit l'entree de dignite depuis les payloads runtime."""
        if not chart_object.capabilities.supports_dignities:
            raise ValueError(f"chart object does not support dignities: {chart_object.code}")
        if chart_object.longitude is None:
            raise ValueError(f"dignity input requires longitude: {chart_object.code}")
        if chart_object.zodiac_position is None:
            raise ValueError(f"dignity input requires zodiac position: {chart_object.code}")
        if chart_object.payloads.house_position is None:
            raise ValueError(f"dignity input requires house position: {chart_object.code}")

        motion = chart_object.payloads.motion
        return PlanetDignityInput(
            planet_code=chart_object.code,
            longitude=chart_object.longitude,
            sign_code=chart_object.zodiac_position.sign_code,
            house_number=chart_object.payloads.house_position.house_number,
            speed_longitude=motion.speed_longitude if motion is not None else None,
            is_retrograde=motion.is_retrograde if motion is not None else None,
        )


class DignityPayloadProjector:
    """Projette les resultats calcules sans recomposer les scores."""

    def project(self, result: PlanetDignityResult) -> DignityRuntimePayload:
        """Construit le payload runtime depuis le resultat historique."""
        return DignityRuntimePayload(
            essential_score=result.essential_score,
            accidental_score=result.accidental_score,
            total_score=result.total_score,
            functional_strength_score=result.functional_strength_score,
            expression_quality_score=result.expression_quality_score,
            intensity_score=result.intensity_score,
            essential_breakdown=tuple(
                DignityBreakdownItem(
                    dignity_type_code=item.dignity_type_code,
                    score_value=item.score_value,
                    source=item.source,
                )
                for item in result.essential_breakdown
            ),
            accidental_breakdown=tuple(
                DignityBreakdownItem(
                    dignity_type_code=item.dignity_type_code,
                    score_value=item.score_value,
                    source=item.source,
                )
                for item in result.accidental_breakdown
            ),
            condition_codes=tuple(item.key for item in result.advanced_condition_modifiers),
            source="dignities.planet_dignity_scoring_service",
        )


class DignityPayloadEnricher:
    """Ajoute immuablement les payloads dignity aux objets eligibles."""

    def __init__(self, projector: DignityPayloadProjector | None = None) -> None:
        self._projector = projector or DignityPayloadProjector()

    def enrich(
        self,
        objects: Sequence[ChartObjectRuntimeData],
        results: Sequence[PlanetDignityResult],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne de nouveaux objets avec payloads dignity rattaches."""
        result_by_code = _index_results(results)
        consumed_codes: set[str] = set()
        enriched: list[ChartObjectRuntimeData] = []
        for chart_object in objects:
            if not chart_object.capabilities.supports_dignities:
                if chart_object.payloads.dignity is not None:
                    raise ValueError(
                        f"dignity payload requires dignity capability: {chart_object.code}"
                    )
                enriched.append(chart_object)
                continue
            result = result_by_code.get(chart_object.code)
            if result is None:
                raise ValueError(f"missing dignity result for chart object: {chart_object.code}")
            consumed_codes.add(chart_object.code)
            enriched.append(
                replace(
                    chart_object,
                    payloads=replace(
                        chart_object.payloads,
                        dignity=self._projector.project(result),
                    ),
                )
            )
        unknown_codes = sorted(set(result_by_code) - consumed_codes)
        if unknown_codes:
            raise ValueError(f"unknown dignity result target: {', '.join(unknown_codes)}")
        return tuple(enriched)


def _index_results(
    results: Sequence[PlanetDignityResult],
) -> Mapping[str, PlanetDignityResult]:
    """Indexe les resultats et refuse les doublons silencieux."""
    indexed: dict[str, PlanetDignityResult] = {}
    for result in results:
        if indexed.get(result.planet_code) is not None:
            raise ValueError(f"duplicate dignity result: {result.planet_code}")
        indexed[result.planet_code] = result
    return indexed


def _ensure_unique_chart_object_codes(objects: Sequence[ChartObjectRuntimeData]) -> None:
    """Refuse une selection qui rendrait la projection ambigue."""
    duplicated_codes = sorted(
        item_code
        for item_code, count in Counter(item.code for item in objects).items()
        if count > 1
    )
    if duplicated_codes:
        raise ValueError(f"duplicate dignity chart object: {', '.join(duplicated_codes)}")


def _validate_dignity_candidate(chart_object: ChartObjectRuntimeData) -> None:
    """Valide les faits minimaux requis avant projection dignity."""
    if chart_object.longitude is None:
        raise ValueError(f"dignity candidate requires longitude: {chart_object.code}")
    if chart_object.zodiac_position is None:
        raise ValueError(f"dignity candidate requires zodiac position: {chart_object.code}")
    if chart_object.payloads.house_position is None:
        raise ValueError(f"dignity candidate requires house position: {chart_object.code}")
