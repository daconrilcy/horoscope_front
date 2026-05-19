"""Agregation des signaux d'adaptation en themes actives."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import (
    InterpretationAdapterResult,
    InterpretationSignal,
    InterpretationThemeActivation,
)
from app.domain.astrology.interpretation_adapters.priority_ranker import PriorityRanker


class ThemeAggregator:
    """Regroupe les signaux par theme et derive les listes de priorisation."""

    def __init__(self, ranker: PriorityRanker | None = None) -> None:
        self.ranker = ranker or PriorityRanker()

    def aggregate(self, signals: tuple[InterpretationSignal, ...]) -> InterpretationAdapterResult:
        """Produit le resultat complet d'adaptation depuis les signaux."""
        themes = self.ranker.sort_theme_activations(self._theme_activations(signals))
        return InterpretationAdapterResult(
            signals=signals,
            activated_themes=themes,
            dominant_topics=tuple(theme.theme_code for theme in themes),
            dominant_axes=self._dominant_axes(themes),
            tension_patterns=tuple(
                signal.signal_code for signal in signals if signal.theme_category == "tension"
            ),
            support_patterns=tuple(
                signal.signal_code for signal in signals if signal.theme_category == "functional"
            ),
            critical_patterns=tuple(
                signal.signal_code for signal in signals if signal.priority == "critical"
            ),
            narrative_priorities=self._result_priorities(signals, themes),
        )

    def _theme_activations(
        self, signals: tuple[InterpretationSignal, ...]
    ) -> tuple[InterpretationThemeActivation, ...]:
        """Calcule les activations par theme."""
        by_theme: dict[str, list[InterpretationSignal]] = {}
        for signal in signals:
            by_theme.setdefault(signal.theme_code, []).append(signal)
        activations: list[InterpretationThemeActivation] = []
        for theme_code, theme_signals in by_theme.items():
            ordered = self.ranker.sort_signals(tuple(theme_signals))
            activation_score = min(1.0, sum(signal.weight for signal in ordered))
            first = ordered[0]
            activations.append(
                InterpretationThemeActivation(
                    theme_code=theme_code,
                    theme_category=first.theme_category,
                    activation_score=round(activation_score, 3),
                    priority=first.priority,
                    priority_rank=first.priority_rank,
                    contributing_signals=tuple(signal.signal_code for signal in ordered),
                )
            )
        return tuple(activations)

    def _dominant_axes(self, themes: tuple[InterpretationThemeActivation, ...]) -> tuple[str, ...]:
        """Classe les categories thematiques actives."""
        scores: dict[str, float] = {}
        for theme in themes:
            scores[theme.theme_category] = scores.get(theme.theme_category, 0.0) + (
                theme.activation_score
            )
        return tuple(
            category
            for category, _score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        )

    def _result_priorities(
        self,
        signals: tuple[InterpretationSignal, ...],
        themes: tuple[InterpretationThemeActivation, ...],
    ) -> tuple[str, ...]:
        """Construit une liste stable de priorites aval non textuelles."""
        ordered_codes = [signal.signal_code for signal in signals]
        ordered_codes.extend(theme.theme_code for theme in themes)
        return tuple(dict.fromkeys(ordered_codes))
