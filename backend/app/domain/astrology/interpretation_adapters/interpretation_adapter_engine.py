"""Orchestration pure de la couche d'adaptation interpretative."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignalSet,
)
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    ChartInterpretationInputRuntimeData,
)
from app.domain.astrology.interpretation_adapters.contracts import InterpretationAdapterResult
from app.domain.astrology.interpretation_adapters.priority_ranker import PriorityRanker
from app.domain.astrology.interpretation_adapters.signal_builder import SignalBuilder
from app.domain.astrology.interpretation_adapters.theme_aggregator import ThemeAggregator
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class InterpretationAdapterEngine:
    """Transforme les faits astrologiques calcules en payload semantique."""

    def __init__(
        self,
        signal_builder: SignalBuilder | None = None,
        theme_aggregator: ThemeAggregator | None = None,
    ) -> None:
        ranker = PriorityRanker()
        self.signal_builder = signal_builder or SignalBuilder(ranker)
        self.theme_aggregator = theme_aggregator or ThemeAggregator(ranker)

    def calculate(
        self,
        *,
        runtime_reference: AstrologyRuntimeReference,
        interpretation_input: ChartInterpretationInputRuntimeData,
        condition_profiles: Iterable[PlanetConditionProfile],
        condition_signals: Iterable[PlanetConditionSignalSet],
    ) -> InterpretationAdapterResult:
        """Produit un resultat d'adaptation deterministe depuis le runtime."""
        signals = self.signal_builder.build(
            adapter_reference=runtime_reference.interpretation_adapter_reference,
            interpretation_input=interpretation_input,
            condition_profiles=condition_profiles,
            condition_signals=condition_signals,
        )
        return self.theme_aggregator.aggregate(signals)
