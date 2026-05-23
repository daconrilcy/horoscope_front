"""Construction des signaux d'adaptation depuis les faits astrologiques."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignalSet,
)
from app.domain.astrology.interpretation.chart_interpretation_input_contracts import (
    AdvancedConditionInterpretationRuntimeData,
    ChartInterpretationInputRuntimeData,
    DominanceInterpretationRuntimeData,
)
from app.domain.astrology.interpretation_adapters.contracts import InterpretationSignal
from app.domain.astrology.interpretation_adapters.priority_ranker import PriorityRanker
from app.domain.astrology.runtime.runtime_reference import (
    InterpretationAdapterReferenceSet,
    InterpretationAdapterRuleReferenceData,
    InterpretationConditionValue,
)


class SignalBuilder:
    """Applique les regles runtime pour produire des signaux normalises."""

    def __init__(self, ranker: PriorityRanker | None = None) -> None:
        self.ranker = ranker or PriorityRanker()

    def build(
        self,
        *,
        adapter_reference: InterpretationAdapterReferenceSet,
        interpretation_input: ChartInterpretationInputRuntimeData,
        condition_profiles: Iterable[PlanetConditionProfile],
        condition_signals: Iterable[PlanetConditionSignalSet],
    ) -> tuple[InterpretationSignal, ...]:
        """Retourne les signaux applicables aux faits calcules."""
        profiles = tuple(condition_profiles)
        signal_sets = tuple(condition_signals)
        dominance = interpretation_input.dominance
        advanced_facts = interpretation_input.advanced_condition_facts
        signals: list[InterpretationSignal] = []
        for rule in adapter_reference.adapter_rules:
            if not rule.is_active:
                continue
            fact = self._fact_for_rule(
                rule=rule,
                condition_profiles=profiles,
                condition_signals=signal_sets,
                advanced_condition_facts=advanced_facts,
                dominance=dominance,
            )
            if fact is None:
                continue
            signal_type = adapter_reference.signal_type(rule.signal_code)
            theme = adapter_reference.theme(signal_type.theme_code)
            priority = rule.priority_override or signal_type.priority_default
            rank = rule.priority_override_rank or signal_type.priority_default_rank
            signals.append(
                InterpretationSignal(
                    signal_code=signal_type.code,
                    theme_code=signal_type.theme_code,
                    source_type=rule.source_type,
                    source_code=rule.source_code,
                    priority=priority,
                    priority_rank=rank,
                    weight=rule.weight,
                    semantic_category=signal_type.category,
                    theme_category=theme.category,
                    explanation_fact=fact,
                )
            )
        return self.ranker.sort_signals(tuple(signals))

    def _fact_for_rule(
        self,
        *,
        rule: InterpretationAdapterRuleReferenceData,
        condition_profiles: tuple[PlanetConditionProfile, ...],
        condition_signals: tuple[PlanetConditionSignalSet, ...],
        advanced_condition_facts: tuple[AdvancedConditionInterpretationRuntimeData, ...],
        dominance: tuple[DominanceInterpretationRuntimeData, ...],
    ) -> str | None:
        """Retourne le fait source retenu pour une règle applicable."""
        if rule.source_type == "dominant_planet":
            return self._match_dominant_planet(rule, dominance)
        if rule.source_type == "condition_axis":
            return self._match_condition_axis(rule, condition_profiles)
        if rule.source_type == "condition_signal":
            return self._match_condition_signal(rule, condition_signals)
        if rule.source_type == "advanced_condition":
            return self._match_advanced_condition(rule, advanced_condition_facts)
        if rule.source_type == "compound":
            return self._match_compound(rule, condition_profiles, dominance)
        return None

    def _match_dominant_planet(
        self,
        rule: InterpretationAdapterRuleReferenceData,
        dominance: tuple[DominanceInterpretationRuntimeData, ...],
    ) -> str | None:
        """Verifie une dominance planetaire calculee."""
        if not dominance:
            return None
        expected_level = self._condition(rule.conditions, "dominance_level")
        for planet in dominance:
            if planet.code != rule.source_code:
                continue
            if expected_level is not None and planet.dominance_level != expected_level:
                return None
            return (
                f"dominant_planet:{planet.code}:rank={planet.rank}:level={planet.dominance_level}"
            )
        return None

    def _match_condition_axis(
        self,
        rule: InterpretationAdapterRuleReferenceData,
        condition_profiles: tuple[PlanetConditionProfile, ...],
    ) -> str | None:
        """Retient la planete la plus forte sur l'axe demande."""
        threshold = self._float_condition(rule.conditions, "min")
        matches: list[tuple[float, str]] = []
        for profile in condition_profiles:
            value = getattr(profile, rule.source_code, None)
            if not isinstance(value, int | float):
                continue
            if threshold is None or float(value) >= threshold:
                matches.append((float(value), profile.planet_code))
        if not matches:
            return None
        value, planet_code = sorted(matches, key=lambda item: (-item[0], item[1]))[0]
        return f"condition_axis:{rule.source_code}:planet={planet_code}:value={value:.3f}"

    def _match_condition_signal(
        self,
        rule: InterpretationAdapterRuleReferenceData,
        condition_signals: tuple[PlanetConditionSignalSet, ...],
    ) -> str | None:
        """Verifie la presence d'un signal conditionnel deja produit."""
        for signal_set in condition_signals:
            for signal in signal_set.signals:
                if signal.code == rule.source_code or signal.axis == rule.source_code:
                    return (
                        f"condition_signal:{signal.code}:planet={signal_set.planet_code}:"
                        f"axis={signal.axis}"
                    )
        return None

    def _match_advanced_condition(
        self,
        rule: InterpretationAdapterRuleReferenceData,
        advanced_condition_facts: tuple[AdvancedConditionInterpretationRuntimeData, ...],
    ) -> str | None:
        """Verifie la presence d'une condition avancee deja produite."""
        for condition in advanced_condition_facts:
            if rule.source_code not in (condition.condition_code, condition.condition_type_code):
                continue
            return (
                f"advanced_condition:{condition.condition_code}:"
                f"type={condition.condition_type_code}"
            )
        return None

    def _match_compound(
        self,
        rule: InterpretationAdapterRuleReferenceData,
        condition_profiles: tuple[PlanetConditionProfile, ...],
        dominance: tuple[DominanceInterpretationRuntimeData, ...],
    ) -> str | None:
        """Verifie une combinaison de dominance et d'axe conditionnel."""
        planet_code, axis_code = self._compound_parts(rule.source_code)
        if planet_code is None or axis_code is None:
            return None
        dominance_level = self._condition(rule.conditions, "dominance_level") or "dominant"
        dominance_rule = InterpretationAdapterRuleReferenceData(
            code=rule.code,
            source_type="dominant_planet",
            source_code=planet_code,
            conditions=(InterpretationConditionValue("dominance_level", dominance_level),),
            signal_code=rule.signal_code,
            priority_override=rule.priority_override,
            priority_override_rank=rule.priority_override_rank,
            weight=rule.weight,
            is_active=rule.is_active,
            reference_version_code=rule.reference_version_code,
        )
        if self._match_dominant_planet(dominance_rule, dominance) is None:
            return None
        threshold = self._float_condition(rule.conditions, "min")
        for profile in condition_profiles:
            if profile.planet_code != planet_code:
                continue
            axis_value = getattr(profile, axis_code, None)
            if not isinstance(axis_value, int | float):
                return None
            if threshold is not None and float(axis_value) < threshold:
                return None
            return f"compound:{rule.source_code}:{axis_code}={float(axis_value):.3f}"
        return None

    def _compound_parts(self, source_code: str) -> tuple[str | None, str | None]:
        """Decode le couple planete/axe porte par le code source runtime."""
        planet_code, separator, axis_code = source_code.partition("_")
        if not separator or not planet_code.strip() or not axis_code.strip():
            return None, None
        return planet_code, axis_code

    def _condition(
        self, conditions: tuple[InterpretationConditionValue, ...], key: str
    ) -> str | None:
        """Retourne une condition textuelle si elle existe."""
        for condition in conditions:
            if condition.key == key:
                return str(condition.value)
        return None

    def _float_condition(
        self, conditions: tuple[InterpretationConditionValue, ...], key: str
    ) -> float | None:
        """Retourne une condition numerique si elle existe."""
        value = self._condition(conditions, key)
        return None if value is None else float(value)
