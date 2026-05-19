"""Tests du classement deterministe des adaptations."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import (
    InterpretationSignal,
    InterpretationThemeActivation,
)
from app.domain.astrology.interpretation_adapters.priority_ranker import PriorityRanker


def _signal(code: str, rank: int, weight: float) -> InterpretationSignal:
    """Construit un signal minimal pour verifier le tri."""
    return InterpretationSignal(
        signal_code=code,
        theme_code="theme",
        source_type="condition_axis",
        source_code=code,
        priority="high",
        priority_rank=rank,
        weight=weight,
        semantic_category="category",
        theme_category="theme_category",
        explanation_fact=f"fact:{code}",
    )


def test_priority_ranker_sorts_signals_by_runtime_rank_weight_and_code() -> None:
    """Le classement ne depend pas de l'ordre d'entree."""
    result = PriorityRanker().sort_signals(
        (
            _signal("b", 20, 0.5),
            _signal("a", 10, 0.1),
            _signal("c", 20, 0.9),
        )
    )

    assert [signal.signal_code for signal in result] == ["a", "c", "b"]


def test_priority_ranker_sorts_theme_activations_by_rank_score_and_code() -> None:
    """Les activations de themes gardent un ordre stable."""
    result = PriorityRanker().sort_theme_activations(
        (
            InterpretationThemeActivation("b", "expression", 0.7, "high", 20, ("s2",)),
            InterpretationThemeActivation("a", "behavioral", 0.5, "critical", 10, ("s1",)),
            InterpretationThemeActivation("c", "functional", 0.9, "high", 20, ("s3",)),
        )
    )

    assert [theme.theme_code for theme in result] == ["a", "c", "b"]
