"""Tests de l'agregation des signaux interpretatifs."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import InterpretationSignal
from app.domain.astrology.interpretation_adapters.theme_aggregator import ThemeAggregator


def _signal(
    code: str,
    theme: str,
    category: str,
    *,
    priority: str = "high",
    rank: int = 20,
    weight: float = 0.8,
) -> InterpretationSignal:
    """Construit un signal d'adaptation minimal."""
    return InterpretationSignal(
        signal_code=code,
        theme_code=theme,
        source_type="condition_axis",
        source_code="visibility",
        priority=priority,
        priority_rank=rank,
        weight=weight,
        semantic_category="expression_pattern",
        theme_category=category,
        explanation_fact=f"fact:{code}",
    )


def test_theme_aggregator_groups_signals_and_derives_patterns() -> None:
    """Les themes et listes derivees restent non textuels et stables."""
    result = ThemeAggregator().aggregate(
        (
            _signal(
                "dominant_mars_signature",
                "drive_assertion_action",
                "behavioral",
                priority="critical",
                rank=10,
                weight=1.0,
            ),
            _signal("constraint_on_action", "frustration_pressure", "tension", weight=0.7),
            _signal("structural_endurance", "responsibility_structure", "functional", weight=0.9),
        )
    )

    assert [theme.theme_code for theme in result.activated_themes] == [
        "drive_assertion_action",
        "responsibility_structure",
        "frustration_pressure",
    ]
    assert result.activated_themes[0].activation_score == 1.0
    assert result.dominant_topics == (
        "drive_assertion_action",
        "responsibility_structure",
        "frustration_pressure",
    )
    assert result.tension_patterns == ("constraint_on_action",)
    assert result.support_patterns == ("structural_endurance",)
    assert result.critical_patterns == ("dominant_mars_signature",)
