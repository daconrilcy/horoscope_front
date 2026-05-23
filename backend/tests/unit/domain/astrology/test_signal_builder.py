"""Tests du builder de signaux interpretatifs."""

from __future__ import annotations

from dataclasses import replace

from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignal,
    PlanetConditionSignalSet,
)
from app.domain.astrology.dominance.contracts import DominantPlanetsResult, PlanetDominanceResult
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AdvancedConditionInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    DominanceInterpretationRuntimeData,
)
from app.domain.astrology.interpretation_adapters.signal_builder import SignalBuilder
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _profile(
    planet_code: str,
    *,
    visibility: float = 0.0,
    stability: float = 0.0,
    constraint: float = 0.0,
) -> PlanetConditionProfile:
    """Construit un profil conditionnel minimal pour les adaptations."""
    return PlanetConditionProfile(
        planet_code=planet_code,
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="test",
        sect="day",
        functional_strength=0.0,
        visibility=visibility,
        stability=stability,
        intensity=0.0,
        coherence=0.0,
        support=0.0,
        constraint=constraint,
        ranking_score=0.0,
        condition_level="moderate",
        breakdown=(),
        explanation_facts=(),
    )


def _dominant(*, planet_code: str, level: str = "dominant") -> DominantPlanetsResult:
    """Construit un classement de dominance minimal."""
    return DominantPlanetsResult(
        score_profile_code="natal_standard_v1",
        tradition_code="modern",
        reference_version_code="v1",
        planets=(
            PlanetDominanceResult(
                planet_code=planet_code,
                total_score=1.0,
                rank=1,
                dominance_level=level,
                factors=(),
                explanation_facts=(),
            ),
        ),
        top_planet_code=planet_code,
        chart_ruler_code=planet_code,
        most_elevated_planet_code=planet_code,
    )


def _interpretation_input(
    *,
    planet_code: str | None = None,
    level: str = "dominant",
    advanced_condition_facts: tuple[AdvancedConditionInterpretationRuntimeData, ...] = (),
) -> ChartInterpretationInputRuntimeData:
    """Construit un input interpretatif minimal pour les tests de signaux."""
    dominance = ()
    if planet_code is not None:
        dominance = (
            DominanceInterpretationRuntimeData(
                code=planet_code,
                score=1.0,
                source="natal_standard_v1",
                rank=1,
                dominance_level=level,
            ),
        )
    return ChartInterpretationInputRuntimeData(
        chart_id=None,
        chart_type="natal",
        locale=None,
        objects=(),
        aspects=(),
        dignities=(),
        house_positions=(),
        rulerships=(),
        dominance=dominance,
        fixed_star_contacts=(),
        advanced_condition_facts=advanced_condition_facts,
    )


def test_signal_builder_maps_dominance_and_condition_axes_from_runtime_rules() -> None:
    """Les règles runtime produisent des signaux techniques deterministes."""
    reference = complete_reference()

    signals = SignalBuilder().build(
        adapter_reference=reference.interpretation_adapter_reference,
        interpretation_input=_interpretation_input(planet_code="mars"),
        condition_profiles=(
            _profile("mars", visibility=0.79, constraint=0.62),
            _profile("venus", visibility=0.71, constraint=0.2),
        ),
        condition_signals=(),
    )

    assert [signal.signal_code for signal in signals] == [
        "dominant_mars_signature",
        "high_externalization",
        "constraint_on_action",
    ]
    assert [signal.priority for signal in signals] == ["critical", "high", "medium"]
    assert signals[1].explanation_fact == "condition_axis:visibility:planet=mars:value=0.790"
    assert signals[2].theme_code == "frustration_pressure"


def test_signal_builder_uses_runtime_priority_default_when_rule_has_no_override() -> None:
    """Le rang par defaut du type de signal reste la source de priorite."""
    reference = complete_reference()
    rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[1],
        priority_override=None,
        priority_override_rank=None,
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        adapter_rules=(rule,),
    )

    signals = SignalBuilder().build(
        adapter_reference=adapter_reference,
        interpretation_input=_interpretation_input(),
        condition_profiles=(_profile("mars", visibility=0.8),),
        condition_signals=(),
    )

    assert signals[0].priority == "high"
    assert signals[0].priority_rank == 20


def test_signal_builder_supports_saturn_stability_compound_rule() -> None:
    """La combinaison Saturne dominant et stabilite forte active le signal dedie."""
    reference = complete_reference()

    signals = SignalBuilder().build(
        adapter_reference=reference.interpretation_adapter_reference,
        interpretation_input=_interpretation_input(planet_code="saturn"),
        condition_profiles=(_profile("saturn", stability=0.74),),
        condition_signals=(),
    )

    assert [signal.signal_code for signal in signals] == ["structural_endurance"]
    assert signals[0].theme_code == "responsibility_structure"


def test_signal_builder_supports_runtime_compound_source_code() -> None:
    """Le code source compound pilote la planete et l'axe a evaluer."""
    reference = complete_reference()
    rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[3],
        source_code="mars_visibility",
        conditions=(
            replace(
                reference.interpretation_adapter_reference.adapter_rules[3].conditions[0],
                value=0.7,
            ),
        ),
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        adapter_rules=(rule,),
    )

    signals = SignalBuilder().build(
        adapter_reference=adapter_reference,
        interpretation_input=_interpretation_input(planet_code="mars"),
        condition_profiles=(_profile("mars", visibility=0.8),),
        condition_signals=(),
    )

    assert [signal.signal_code for signal in signals] == ["structural_endurance"]
    assert signals[0].explanation_fact == "compound:mars_visibility:visibility=0.800"


def test_signal_builder_supports_runtime_condition_signal_rules() -> None:
    """Les signaux conditionnels deja produits peuvent activer une regle runtime."""
    reference = complete_reference()
    rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[1],
        source_type="condition_signal",
        source_code="visibility_high",
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        adapter_rules=(rule,),
    )

    signals = SignalBuilder().build(
        adapter_reference=adapter_reference,
        interpretation_input=_interpretation_input(),
        condition_profiles=(),
        condition_signals=(
            PlanetConditionSignalSet(
                planet_code="mars",
                score_profile="traditional_standard",
                tradition="traditional",
                reference_version="v1",
                signals=(
                    PlanetConditionSignal(
                        code="visibility_high",
                        label="Visibility high",
                        axis="visibility",
                        level="high",
                        level_min=0.7,
                        level_max=1.0,
                        axis_value=0.8,
                        interpretation_use="prioritize_condition_axis",
                        priority_weight=20.0,
                        prompt_hint="visibility_emphasized",
                    ),
                ),
            ),
        ),
    )

    assert [signal.signal_code for signal in signals] == ["high_externalization"]
    assert signals[0].explanation_fact == (
        "condition_signal:visibility_high:planet=mars:axis=visibility"
    )


def test_signal_builder_supports_runtime_advanced_condition_rules() -> None:
    """Les conditions avancees deja detectees peuvent activer une regle runtime."""
    reference = complete_reference()
    rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[2],
        source_type="advanced_condition",
        source_code="hayz",
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        adapter_rules=(rule,),
    )

    signals = SignalBuilder().build(
        adapter_reference=adapter_reference,
        interpretation_input=_interpretation_input(
            advanced_condition_facts=(
                AdvancedConditionInterpretationRuntimeData(
                    condition_code="hayz",
                    condition_type_code="hayz",
                    source_planet_code="mars",
                    target_planet_code=None,
                    score_profile="traditional_advanced_v1",
                    reference_version="v1",
                    score_impact=1.0,
                    ranking_weight=1.1,
                ),
            )
        ),
        condition_profiles=(),
        condition_signals=(),
    )

    assert [signal.signal_code for signal in signals] == ["constraint_on_action"]
    assert signals[0].explanation_fact == "advanced_condition:hayz:type=hayz"
