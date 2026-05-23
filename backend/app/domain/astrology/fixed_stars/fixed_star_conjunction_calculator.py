# Calcul pur des conjonctions entre etoiles fixes et objets runtime.
"""Calculateur deterministe des contacts d'etoiles fixes."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.calculators.aspects import angular_distance_deg
from app.domain.astrology.fixed_stars.contracts import (
    FixedStarConjunctionRulesRuntimeData,
)
from app.domain.astrology.fixed_stars.fixed_star_selectors import (
    FixedStarChartObjectSelector,
    FixedStarConjunctionTargetSelector,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    FixedStarConjunctionRuntimePayload,
)

FIXED_STAR_CONJUNCTION_SOURCE = "fixed_star_conjunction_calculator"


class FixedStarConjunctionCalculator:
    """Calcule les contacts depuis des objets chart-object deja valides."""

    def __init__(
        self,
        rules: FixedStarConjunctionRulesRuntimeData | None = None,
    ) -> None:
        """Prepare le calculateur avec les regles d'orbe centrales."""
        self._rules = rules or FixedStarConjunctionRulesRuntimeData()

    def calculate(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[FixedStarConjunctionRuntimePayload, ...]:
        """Retourne les contacts calcules entre etoiles fixes et cibles."""
        objects = tuple(chart_objects)
        fixed_stars = FixedStarChartObjectSelector().select(objects)
        targets = FixedStarConjunctionTargetSelector().select(objects)
        contacts: list[FixedStarConjunctionRuntimePayload] = []
        for fixed_star in fixed_stars:
            star_payload = fixed_star.payloads.fixed_star
            if star_payload is None:
                continue
            max_orb_deg, rule_code = self._rules.resolve_for(
                star_code=star_payload.catalog_code,
                categories=star_payload.categories,
            )
            for target in targets:
                orb_deg = angular_distance_deg(
                    float(fixed_star.longitude),
                    float(target.longitude),
                )
                if orb_deg <= max_orb_deg:
                    contacts.append(
                        FixedStarConjunctionRuntimePayload(
                            fixed_star_code=fixed_star.code,
                            fixed_star_display_name=fixed_star.display_name,
                            target_code=target.code,
                            target_display_name=target.display_name,
                            fixed_star_longitude_deg=round(float(fixed_star.longitude), 6),
                            target_longitude_deg=round(float(target.longitude), 6),
                            orb_deg=round(orb_deg, 6),
                            max_orb_deg=round(max_orb_deg, 6),
                            rule_code=rule_code,
                            source=FIXED_STAR_CONJUNCTION_SOURCE,
                        )
                    )
        return tuple(
            sorted(
                contacts,
                key=lambda item: (item.target_code, item.fixed_star_code, item.orb_deg),
            )
        )
