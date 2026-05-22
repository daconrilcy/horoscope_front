# Selection et projection des objets runtime vers le moteur d'aspects.
"""Frontiere d'entree canonique du calculateur d'aspects natal."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.runtime.aspect_calculation_contracts import AspectBodyRuntimeData
from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectRuntimeData


class AspectChartObjectSelector:
    """Selectionne les objets aspectables sans branchement par famille."""

    def select(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets dont la capacite aspects est active."""
        selected: list[ChartObjectRuntimeData] = []
        seen_codes: set[str] = set()
        for chart_object in chart_objects:
            if not chart_object.capabilities.supports_aspects:
                continue
            code = chart_object.code.strip().lower()
            if chart_object.longitude is None:
                raise ValueError(f"aspectable chart object {code} requires longitude")
            if code in seen_codes:
                raise ValueError(f"duplicate aspectable chart object code: {code}")
            seen_codes.add(code)
            selected.append(chart_object)
        return tuple(selected)


class AspectBodyProjector:
    """Projette les objets aspectables vers le contrat technique d'aspects."""

    def __init__(self, celestial_catalog: CelestialRuntimeCatalog | None = None) -> None:
        """Prepare la projection avec le catalogue celeste canonique."""
        self._celestial_catalog = celestial_catalog or CelestialRuntimeCatalog.empty()

    def project(self, chart_object: ChartObjectRuntimeData) -> AspectBodyRuntimeData:
        """Convertit un objet runtime valide en participant d'aspect."""
        longitude = _required_longitude(chart_object.longitude, chart_object.code)
        code = chart_object.code.strip().lower()
        return AspectBodyRuntimeData(
            code=code,
            body_type=self._celestial_catalog.body_type_for_code(code),
            longitude=longitude,
        )

    def project_many(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[AspectBodyRuntimeData, ...]:
        """Projette une sequence d'objets en preservant leur ordre."""
        return tuple(self.project(chart_object) for chart_object in chart_objects)


def _required_longitude(value: object, code: str) -> float:
    """Valide une longitude aspectable numerique et finie."""
    if value is None:
        raise ValueError(f"aspect body projection requires longitude for {code}")
    if isinstance(value, bool):
        raise ValueError(f"aspect body projection longitude must be numeric for {code}")
    try:
        longitude = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"aspect body projection longitude must be numeric for {code}") from error
    if not isfinite(longitude):
        raise ValueError(f"aspect body projection longitude must be finite for {code}")
    return longitude
