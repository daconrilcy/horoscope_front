# Selection pure des objets runtime utiles aux conjonctions d'etoiles fixes.
"""Selectors des etoiles fixes et des cibles par payloads et capacites."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite

from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectRuntimeData


class FixedStarChartObjectSelector:
    """Selectionne les etoiles fixes depuis le payload runtime dedie."""

    def select(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets portant un payload d'etoile fixe valide."""
        selected: list[ChartObjectRuntimeData] = []
        seen_codes: set[str] = set()
        for chart_object in chart_objects:
            if chart_object.payloads.fixed_star is None:
                continue
            code = _normalized_code(chart_object.code, "fixed star")
            _required_longitude(chart_object.longitude, code, "fixed star")
            if code in seen_codes:
                raise ValueError(f"duplicate fixed star chart object code: {code}")
            seen_codes.add(code)
            selected.append(chart_object)
        return tuple(selected)


class FixedStarConjunctionTargetSelector:
    """Selectionne les cibles par capacite de conjonction fixed star."""

    def select(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Retourne les objets eligibles comme cibles de contacts."""
        selected: list[ChartObjectRuntimeData] = []
        seen_codes: set[str] = set()
        for chart_object in chart_objects:
            if not chart_object.capabilities.supports_fixed_star_conjunction:
                continue
            if chart_object.payloads.fixed_star is not None:
                continue
            code = _normalized_code(chart_object.code, "fixed star conjunction target")
            _required_longitude(chart_object.longitude, code, "fixed star conjunction target")
            if code in seen_codes:
                raise ValueError(f"duplicate fixed star conjunction target code: {code}")
            seen_codes.add(code)
            selected.append(chart_object)
        return tuple(selected)


def _normalized_code(code: str, label: str) -> str:
    """Normalise un code selectionne en refusant les valeurs vides."""
    normalized_code = code.strip().lower()
    if not normalized_code:
        raise ValueError(f"{label} requires code")
    return normalized_code


def _required_longitude(value: object, code: str, label: str) -> float:
    """Valide une longitude numerique et finie pour la selection."""
    if value is None:
        raise ValueError(f"{label} {code} requires longitude")
    if isinstance(value, bool):
        raise ValueError(f"{label} {code} longitude must be numeric")
    try:
        longitude = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} {code} longitude must be numeric") from error
    if not isfinite(longitude):
        raise ValueError(f"{label} {code} longitude must be finite")
    return longitude
