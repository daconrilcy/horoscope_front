"""Moteur pur des conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from app.domain.astrology.advanced_conditions._dignity_rule_helpers import dignity_by_planet
from app.domain.astrology.advanced_conditions.aspect_condition_detector import (
    AspectConditionDetector,
)
from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    PlanetConditionAxisImpact,
)
from app.domain.astrology.advanced_conditions.hayz_calculator import HayzCalculator
from app.domain.astrology.advanced_conditions.heliacal_condition_calculator import (
    HeliacalConditionCalculator,
)
from app.domain.astrology.advanced_conditions.mutual_reception_calculator import (
    MutualReceptionCalculator,
)
from app.domain.astrology.advanced_conditions.planet_speed_classifier import (
    PlanetSpeedClassifier,
)
from app.domain.astrology.condition.contracts import (
    PlanetConditionBreakdownItem,
    PlanetConditionExplanationFact,
    PlanetConditionProfile,
)
from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import (
    AdvancedConditionWeightReferenceData,
    AstrologyRuntimeReference,
)


class AdvancedConditionEngine:
    """Calcule, score et applique les conditions avancees factuelles."""

    def calculate(
        self,
        *,
        runtime_reference: AstrologyRuntimeReference,
        planet_positions: tuple[Any, ...],
        aspects: tuple[Any, ...],
        dignities: tuple[PlanetDignityResult, ...],
        condition_profiles: tuple[PlanetConditionProfile, ...],
    ) -> tuple[tuple[AdvancedPlanetaryCondition, ...], tuple[PlanetConditionProfile, ...]]:
        """Retourne les conditions avancees et les profils enrichis."""
        profile = runtime_reference.advanced_condition_reference.default_score_profile
        weights = {
            item.condition_type_code: item
            for item in runtime_reference.advanced_condition_reference.weights_for_profile(
                profile.code
            )
        }
        condition_type_codes = frozenset(weights)
        emit_condition = self._condition_emitter(
            score_profile=profile.code,
            reference_version=profile.reference_version_code,
            weights=weights,
        )
        by_dignity = dignity_by_planet(dignities)
        conditions = (
            *MutualReceptionCalculator().calculate(
                planet_positions,
                runtime_reference,
                emit_condition,
            ),
            *HayzCalculator().calculate(
                planet_positions,
                by_dignity,
                runtime_reference,
                emit_condition,
            ),
            *PlanetSpeedClassifier().calculate(planet_positions, by_dignity, emit_condition),
            *HeliacalConditionCalculator().calculate(
                planet_positions,
                by_dignity,
                emit_condition,
                condition_type_codes=condition_type_codes,
            ),
            *AspectConditionDetector().calculate(
                planet_positions,
                aspects,
                by_dignity,
                runtime_reference,
                emit_condition,
                condition_type_codes=condition_type_codes,
            ),
        )
        unique_conditions = self._deduplicate(conditions)
        return unique_conditions, self.enrich_profiles(condition_profiles, unique_conditions)

    def enrich_profiles(
        self,
        profiles: tuple[PlanetConditionProfile, ...],
        conditions: tuple[AdvancedPlanetaryCondition, ...],
    ) -> tuple[PlanetConditionProfile, ...]:
        """Ajoute les impacts avances sans modifier les profils existants."""
        by_planet: dict[str, list[AdvancedPlanetaryCondition]] = {}
        for condition in conditions:
            by_planet.setdefault(condition.source_planet_code, []).append(condition)
        enriched: list[PlanetConditionProfile] = []
        for profile in profiles:
            planet_conditions = tuple(by_planet.get(profile.planet_code, ()))
            if not planet_conditions:
                enriched.append(profile)
                continue
            breakdown = (
                *profile.breakdown,
                *tuple(self._breakdown_item(condition) for condition in planet_conditions),
            )
            facts = (
                *profile.explanation_facts,
                *tuple(self._fact(condition) for condition in planet_conditions),
            )
            enriched.append(
                replace(
                    profile,
                    functional_strength=round(
                        profile.functional_strength
                        + sum(
                            item.axes_impact.functional_strength_delta for item in planet_conditions
                        ),
                        6,
                    ),
                    visibility=round(
                        profile.visibility
                        + sum(item.axes_impact.visibility_delta for item in planet_conditions),
                        6,
                    ),
                    stability=round(
                        profile.stability
                        + sum(item.axes_impact.stability_delta for item in planet_conditions),
                        6,
                    ),
                    intensity=round(
                        profile.intensity
                        + sum(item.axes_impact.intensity_delta for item in planet_conditions),
                        6,
                    ),
                    coherence=round(
                        profile.coherence
                        + sum(item.axes_impact.coherence_delta for item in planet_conditions),
                        6,
                    ),
                    support=round(
                        profile.support
                        + sum(item.axes_impact.support_delta for item in planet_conditions),
                        6,
                    ),
                    constraint=round(
                        profile.constraint
                        + sum(item.axes_impact.constraint_delta for item in planet_conditions),
                        6,
                    ),
                    ranking_score=round(
                        profile.ranking_score
                        + sum(item.ranking_weight for item in planet_conditions),
                        6,
                    ),
                    breakdown=breakdown,
                    explanation_facts=facts,
                )
            )
        return tuple(enriched)

    def _condition_emitter(
        self,
        *,
        score_profile: str,
        reference_version: str,
        weights: dict[str, AdvancedConditionWeightReferenceData],
    ) -> Callable[..., AdvancedPlanetaryCondition]:
        """Construit un emetteur de conditions rattache aux poids runtime."""

        def emit_condition(
            *,
            condition_code: str,
            condition_type_code: str,
            source_planet_code: str,
            target_planet_code: str | None,
            reason: str,
        ) -> AdvancedPlanetaryCondition:
            weight = weights[condition_type_code]
            axes = PlanetConditionAxisImpact(
                functional_strength_delta=round(weight.functional_strength_weight, 6),
                visibility_delta=round(weight.visibility_weight, 6),
                stability_delta=round(weight.stability_weight, 6),
                intensity_delta=round(weight.intensity_weight, 6),
                coherence_delta=round(weight.coherence_weight, 6),
                support_delta=round(weight.support_weight, 6),
                constraint_delta=round(weight.constraint_weight, 6),
            )
            score_impact = round(
                axes.functional_strength_delta
                + axes.visibility_delta
                + axes.stability_delta
                + axes.intensity_delta
                + axes.coherence_delta
                + axes.support_delta
                - axes.constraint_delta,
                6,
            )
            return AdvancedPlanetaryCondition(
                condition_code=condition_code,
                condition_type_code=condition_type_code,
                source_planet_code=source_planet_code,
                target_planet_code=target_planet_code,
                score_profile=score_profile,
                reference_version=reference_version,
                score_impact=score_impact,
                ranking_weight=round(weight.ranking_weight, 6),
                axes_impact=axes,
                reason=reason,
            )

        return emit_condition

    def _breakdown_item(
        self, condition: AdvancedPlanetaryCondition
    ) -> PlanetConditionBreakdownItem:
        """Convertit une condition avancee en contribution de profil."""
        axes = condition.axes_impact
        return PlanetConditionBreakdownItem(
            dignity_family="advanced",
            dignity_type_code=condition.condition_code,
            source=condition.condition_type_code,
            reason=condition.reason,
            score_value=condition.score_impact,
            functional_strength=axes.functional_strength_delta,
            visibility=axes.visibility_delta,
            stability=axes.stability_delta,
            intensity=axes.intensity_delta,
            coherence=axes.coherence_delta,
            support=axes.support_delta,
            constraint=axes.constraint_delta,
        )

    def _fact(self, condition: AdvancedPlanetaryCondition) -> PlanetConditionExplanationFact:
        """Expose un fait court de condition avancee."""
        return PlanetConditionExplanationFact("advanced_condition", condition.condition_code)

    def _deduplicate(
        self,
        conditions: tuple[AdvancedPlanetaryCondition, ...],
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Supprime les doublons d'emission en conservant un ordre stable."""
        seen: set[tuple[str, str, str | None]] = set()
        result: list[AdvancedPlanetaryCondition] = []
        for condition in conditions:
            key = (
                condition.condition_code,
                condition.source_planet_code,
                condition.target_planet_code,
            )
            if key in seen:
                continue
            seen.add(key)
            result.append(condition)
        return tuple(
            sorted(result, key=lambda item: (item.source_planet_code, item.condition_code))
        )
