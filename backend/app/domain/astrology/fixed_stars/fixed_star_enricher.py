# Enrichissement immuable des objets cible avec contacts d'etoiles fixes.
"""Enricher des payloads calcules de conjonctions d'etoiles fixes."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    FixedStarConjunctionRuntimePayload,
)


class FixedStarConjunctionEnricher:
    """Rattache les contacts aux cibles sans mutation en place."""

    def enrich(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
        conjunctions: Iterable[FixedStarConjunctionRuntimePayload],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne de nouvelles instances enrichies par code cible."""
        objects = tuple(chart_objects)
        objects_by_code = {item.code: item for item in objects}
        conjunctions_by_target: dict[str, list[FixedStarConjunctionRuntimePayload]] = {
            item.code: [] for item in objects
        }
        for conjunction in conjunctions:
            target_code = conjunction.target_code
            if target_code not in objects_by_code:
                raise ValueError(f"unknown fixed star conjunction target: {target_code}")
            conjunctions_by_target[target_code].append(conjunction)

        return tuple(
            replace(
                chart_object,
                payloads=replace(
                    chart_object.payloads,
                    fixed_star_conjunctions=tuple(conjunctions_by_target[chart_object.code]),
                ),
            )
            for chart_object in objects
        )
