# Projection des maisons et maitrises vers les objets runtime du theme natal.
"""Selectors, projectors et enrichers house/rulership pour les chart objects."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    RulershipRuntimePayload,
)


@dataclass(frozen=True, slots=True)
class RulershipProjectionInput:
    """Faits canoniques requis pour projeter les maitrises d'un objet."""

    chart_object: ChartObjectRuntimeData
    rules_houses: tuple[int, ...]
    rules_signs: tuple[str, ...]
    dispositor_code: str | None


class RulershipChartObjectSelector:
    """Selectionne les objets eligibles aux maitrises par capacite declaree."""

    def choose(
        self,
        objects: Sequence[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets eligibles apres controle des codes uniques."""
        selected = tuple(item for item in objects if item.capabilities.supports_rulership)
        duplicated_codes = sorted(
            item_code
            for item_code, count in Counter(item.code for item in selected).items()
            if count > 1
        )
        if duplicated_codes:
            raise ValueError(f"duplicate rulership chart object: {', '.join(duplicated_codes)}")
        return selected


class RulershipPayloadProjector:
    """Projette les faits de maitrise sans recalculer les rulers."""

    def project(self, projection_input: RulershipProjectionInput) -> RulershipRuntimePayload:
        """Construit le payload runtime depuis les resultats historiques."""
        rules_houses = projection_input.rules_houses
        return RulershipRuntimePayload(
            rules_houses=rules_houses,
            is_house_ruler=bool(rules_houses),
            is_ascendant_ruler=1 in rules_houses,
            is_midheaven_ruler=10 in rules_houses,
            dispositor_code=projection_input.dispositor_code,
            rules_signs=projection_input.rules_signs,
            rulership_sources=tuple(
                f"house_rulers.house_{house_number}" for house_number in rules_houses
            ),
            source="house_rulers.sign_rulerships",
        )


class RulershipPayloadEnricher:
    """Ajoute immuablement les payloads rulership aux objets eligibles."""

    def __init__(
        self,
        selector: RulershipChartObjectSelector | None = None,
        projector: RulershipPayloadProjector | None = None,
    ) -> None:
        self._selector = selector or RulershipChartObjectSelector()
        self._projector = projector or RulershipPayloadProjector()

    def enrich(
        self,
        objects: Sequence[ChartObjectRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        sign_rulerships: Mapping[str, str],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne de nouveaux objets avec payloads rulership rattaches."""
        eligible_codes = {item.code for item in self._selector.choose(objects)}
        house_index = _build_house_rulership_index(house_rulers)
        dispositor_index = _normalize_mapping(sign_rulerships)
        enriched: list[ChartObjectRuntimeData] = []
        for chart_object in objects:
            if chart_object.code not in eligible_codes:
                if chart_object.payloads.rulership is not None:
                    raise ValueError(
                        f"rulership payload requires rulership capability: {chart_object.code}"
                    )
                enriched.append(chart_object)
                continue

            projection_input = RulershipProjectionInput(
                chart_object=chart_object,
                rules_houses=tuple(house_index["houses"].get(chart_object.code, ())),
                rules_signs=tuple(house_index["signs"].get(chart_object.code, ())),
                dispositor_code=_dispositor_for(chart_object, dispositor_index),
            )
            enriched.append(
                replace(
                    chart_object,
                    payloads=replace(
                        chart_object.payloads,
                        rulership=self._projector.project(projection_input),
                    ),
                )
            )
        return tuple(enriched)


def _build_house_rulership_index(
    house_rulers: Sequence[HouseRulerResult],
) -> dict[str, Mapping[str, tuple[int, ...] | tuple[str, ...]]]:
    """Indexe les maisons et signes gouvernes depuis HouseRulerResult."""
    houses_by_ruler: defaultdict[str, list[int]] = defaultdict(list)
    signs_by_ruler: defaultdict[str, list[str]] = defaultdict(list)
    for ruler in sorted(house_rulers, key=lambda item: item.house_number):
        ruler_code = _normalize_code(ruler.ruler_planet)
        houses_by_ruler[ruler_code].append(ruler.house_number)
        signs_by_ruler[ruler_code].append(_normalize_code(ruler.cusp_sign))
    return {
        "houses": {
            ruler_code: tuple(house_numbers)
            for ruler_code, house_numbers in houses_by_ruler.items()
        },
        "signs": {
            ruler_code: tuple(sign_codes) for ruler_code, sign_codes in signs_by_ruler.items()
        },
    }


def _normalize_mapping(sign_rulerships: Mapping[str, str]) -> dict[str, str]:
    """Normalise le mapping signe vers maitre fourni par le referentiel."""
    return {
        _normalize_code(sign_code): _normalize_code(ruler_code)
        for sign_code, ruler_code in sign_rulerships.items()
        if _normalize_code(sign_code) and _normalize_code(ruler_code)
    }


def _dispositor_for(
    chart_object: ChartObjectRuntimeData,
    sign_rulerships: Mapping[str, str],
) -> str | None:
    """Retourne le dispositor depuis le signe de l'objet, sans fallback."""
    if chart_object.zodiac_position is None:
        return None
    return sign_rulerships.get(_normalize_code(chart_object.zodiac_position.sign_code))


def _normalize_code(value: object) -> str:
    """Retourne un code metier stable en minuscules."""
    return str(value).strip().lower()
