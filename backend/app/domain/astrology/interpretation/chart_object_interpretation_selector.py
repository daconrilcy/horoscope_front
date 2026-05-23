# Selection des objets chart-object eligibles pour l'interpretation.
"""Selector pilote uniquement par la capacite `supports_interpretation`."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectRuntimeData


class ChartObjectInterpretationSelector:
    """Retourne les objets interpretables sans branche par famille ou code."""

    def select(
        self,
        chart_objects: Iterable[ChartObjectRuntimeData],
    ) -> tuple[ChartObjectRuntimeData, ...]:
        """Preserve l'ordre d'entree et exclut les objets non interpretables."""
        selected = tuple(
            chart_object
            for chart_object in chart_objects
            if chart_object.capabilities.supports_interpretation
        )
        code_counts = Counter(chart_object.code for chart_object in selected)
        duplicate_code = next((value for value, count in code_counts.items() if count > 1), None)
        if duplicate_code is not None:
            raise ValueError(
                f"duplicate interpretation-capable chart object code: {duplicate_code}"
            )
        return selected
