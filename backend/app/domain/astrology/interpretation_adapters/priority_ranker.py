"""Classement deterministe des signaux et themes d'adaptation."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import (
    InterpretationSignal,
    InterpretationThemeActivation,
)


class PriorityRanker:
    """Ordonne les objets d'adaptation selon les rangs fournis par le runtime."""

    def sort_signals(
        self, signals: tuple[InterpretationSignal, ...]
    ) -> tuple[InterpretationSignal, ...]:
        """Trie les signaux de manière stable et explicable."""
        return tuple(
            sorted(
                signals,
                key=lambda item: (
                    item.priority_rank,
                    -item.weight,
                    item.theme_code,
                    item.signal_code,
                    item.source_code,
                ),
            )
        )

    def sort_theme_activations(
        self, themes: tuple[InterpretationThemeActivation, ...]
    ) -> tuple[InterpretationThemeActivation, ...]:
        """Trie les themes actives selon priorite puis score."""
        return tuple(
            sorted(
                themes,
                key=lambda item: (
                    item.priority_rank,
                    -item.activation_score,
                    item.theme_category,
                    item.theme_code,
                ),
            )
        )
