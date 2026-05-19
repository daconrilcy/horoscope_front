"""Tests du contrat de resultat de l'adaptateur interpretatif."""

from __future__ import annotations

from app.domain.astrology.interpretation_adapters.contracts import (
    InterpretationAdapterResult,
    InterpretationSignal,
    InterpretationThemeActivation,
)


def test_interpretation_adapter_result_exposes_required_non_narrative_fields() -> None:
    """Le contrat expose les axes, soutiens et tensions sous codes techniques."""
    result = InterpretationAdapterResult(
        signals=(
            InterpretationSignal(
                signal_code="constraint_on_action",
                theme_code="frustration_pressure",
                source_type="condition_axis",
                source_code="constraint",
                priority="medium",
                priority_rank=30,
                weight=0.7,
                semantic_category="tension_pattern",
                theme_category="tension",
                explanation_fact="condition_axis:constraint:planet=mars:value=0.620",
            ),
            InterpretationSignal(
                signal_code="structural_endurance",
                theme_code="responsibility_structure",
                source_type="compound",
                source_code="saturn_stability",
                priority="high",
                priority_rank=20,
                weight=0.9,
                semantic_category="planetary_signature",
                theme_category="functional",
                explanation_fact="compound:saturn_stability:stability=0.740",
            ),
        ),
        activated_themes=(
            InterpretationThemeActivation(
                theme_code="responsibility_structure",
                theme_category="functional",
                activation_score=0.9,
                priority="high",
                priority_rank=20,
                contributing_signals=("structural_endurance",),
            ),
            InterpretationThemeActivation(
                theme_code="frustration_pressure",
                theme_category="tension",
                activation_score=0.7,
                priority="medium",
                priority_rank=30,
                contributing_signals=("constraint_on_action",),
            ),
        ),
        dominant_topics=("responsibility_structure", "frustration_pressure"),
        dominant_axes=("functional", "tension"),
        tension_patterns=("constraint_on_action",),
        support_patterns=("structural_endurance",),
        critical_patterns=(),
        narrative_priorities=(
            "structural_endurance",
            "constraint_on_action",
            "responsibility_structure",
            "frustration_pressure",
        ),
    )

    assert result.dominant_axes == ("functional", "tension")
    assert result.tension_patterns == ("constraint_on_action",)
    assert result.support_patterns == ("structural_endurance",)
    assert all(" " not in item for item in result.narrative_priorities)
