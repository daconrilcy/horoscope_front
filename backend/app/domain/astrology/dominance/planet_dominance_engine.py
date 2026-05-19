"""Moteur pur de classement factuel des dominantes planetaires."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any

from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation.dominant_aspects import DominantAspectEvaluator
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    DominanceScoreWeightReferenceData,
)


class PlanetDominanceEngine:
    """Classe les planetes dominantes depuis des faits natals deja calcules."""

    def __init__(self, aspect_evaluator: DominantAspectEvaluator | None = None) -> None:
        """Initialise le moteur avec l'evaluateur canonique des aspects dominants."""
        self._aspect_evaluator = aspect_evaluator or DominantAspectEvaluator()

    def calculate(
        self,
        *,
        runtime_reference: AstrologyRuntimeReference,
        planet_positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        condition_profiles: Sequence[PlanetConditionProfile],
        aspects: Sequence[Any],
        advanced_conditions: Sequence[Any] = (),
    ) -> DominantPlanetsResult:
        """Produit un classement pondere par le profil actif du runtime."""
        dominance_reference = runtime_reference.dominance_reference
        score_profile = dominance_reference.default_score_profile
        score_weights = dominance_reference.weights_for_profile(score_profile.code)
        total_weight = sum(weight.weight for weight in score_weights)
        if total_weight <= 0.0:
            raise ValueError("dominance score weights require a positive total weight")

        planet_codes = tuple(position.planet_code for position in planet_positions)
        luminary_codes = frozenset(
            planet.code for planet in runtime_reference.planets.items if planet.is_luminary
        )
        results = []
        for planet_code in planet_codes:
            factors = tuple(
                self._factor(
                    weight=weight,
                    planet_code=planet_code,
                    planet_positions=planet_positions,
                    houses=houses,
                    house_rulers=house_rulers,
                    condition_profiles=condition_profiles,
                    advanced_conditions=advanced_conditions,
                    aspects=aspects,
                    luminary_codes=luminary_codes,
                )
                for weight in score_weights
            )
            total_score = round(sum(item.weighted_score for item in factors) / total_weight, 6)
            results.append((planet_code, total_score, factors))

        ordered = sorted(results, key=lambda item: (-item[1], item[0]))
        planets = tuple(
            PlanetDominanceResult(
                planet_code=planet_code,
                total_score=score,
                rank=index + 1,
                dominance_level=self._dominance_level(score),
                factors=factors,
                explanation_facts=self._explanation_facts(factors),
            )
            for index, (planet_code, score, factors) in enumerate(ordered)
        )
        return DominantPlanetsResult(
            score_profile_code=score_profile.code,
            tradition_code=score_profile.tradition_code,
            reference_version_code=score_profile.reference_version_code,
            planets=planets,
            top_planet_code=planets[0].planet_code if planets else None,
            chart_ruler_code=self._chart_ruler(house_rulers),
            most_elevated_planet_code=self._most_elevated_planet(planet_positions, houses),
        )

    def _factor(
        self,
        *,
        weight: DominanceScoreWeightReferenceData,
        planet_code: str,
        planet_positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        condition_profiles: Sequence[PlanetConditionProfile],
        advanced_conditions: Sequence[Any],
        aspects: Sequence[Any],
        luminary_codes: frozenset[str],
    ) -> PlanetDominanceFactor:
        """Calcule une contribution en dispatchant vers le facteur runtime."""
        raw_value, reason = {
            "chart_ruler": self._chart_ruler_value,
            "angularity": self._angularity_value,
            "condition_strength": self._condition_strength_value,
            "visibility": self._visibility_value,
            "most_elevated": self._most_elevated_value,
            "luminary_emphasis": self._luminary_emphasis_value,
            "house_rulership_load": self._house_rulership_load_value,
            "aspect_centrality": self._aspect_centrality_value,
        }[weight.factor_type_code](
            planet_code,
            frozenset(position.planet_code for position in planet_positions),
            planet_positions,
            houses,
            house_rulers,
            condition_profiles,
            advanced_conditions,
            aspects,
            luminary_codes,
        )
        normalized = self._normalize(raw_value, weight.min_value, weight.max_value)
        factor_weight = round(weight.weight, 6)
        return PlanetDominanceFactor(
            factor_code=weight.factor_type_code,
            raw_value=round(raw_value, 6),
            normalized_value=normalized,
            weight=factor_weight,
            weighted_score=round(normalized * factor_weight, 6),
            reason=reason,
        )

    def _chart_ruler_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        ruler = self._chart_ruler(house_rulers)
        if ruler == planet_code:
            return 1.0, f"{planet_code} rules the Ascendant sign."
        return 0.0, f"{planet_code} is not the chart ruler."

    def _angularity_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        for house in houses:
            if not any(occupant.planet == planet_code for occupant in house.occupants):
                continue
            score = (
                1.0
                if house.house_kind == "angular"
                else 0.5
                if house.house_kind == "succedent"
                else 0.2
            )
            return score, f"{planet_code} is in house {house.number} ({house.house_kind})."
        return 0.0, f"{planet_code} has no resolved house placement."

    def _condition_strength_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        profiles: Sequence[PlanetConditionProfile],
        advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        profile = self._profile(planet_code, profiles)
        max_strength = max((max(item.functional_strength, 0.0) for item in profiles), default=0.0)
        if profile is None or max_strength <= 0.0:
            return 0.0, f"{planet_code} has no condition strength profile."
        advanced_weight = sum(
            float(getattr(condition, "ranking_weight", 0.0))
            for condition in advanced_conditions
            if getattr(condition, "source_planet_code", None) == planet_code
        )
        return (
            (profile.functional_strength + advanced_weight) / max_strength,
            (
                f"{planet_code} functional strength is {profile.functional_strength:.6g}; "
                f"advanced ranking weight is {advanced_weight:.6g}."
            ),
        )

    def _visibility_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        profile = self._profile(planet_code, profiles)
        max_visibility = max((max(item.visibility, 0.0) for item in profiles), default=0.0)
        if profile is None or max_visibility <= 0.0:
            return 0.0, f"{planet_code} has no visibility profile."
        return (
            profile.visibility / max_visibility,
            f"{planet_code} visibility is {profile.visibility:.6g}.",
        )

    def _most_elevated_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        elevated = self._most_elevated_planet(positions, houses)
        if elevated == planet_code:
            return 1.0, f"{planet_code} is the most elevated planet."
        planet_house = self._planet_house(planet_code, positions)
        if planet_house is None:
            return 0.0, f"{planet_code} has no house for elevation scoring."
        distance_to_mc_house = min(abs(planet_house - 10), 12 - abs(planet_house - 10))
        return max(0.0, 1.0 - (distance_to_mc_house / 6.0)), (
            f"{planet_code} is {distance_to_mc_house} houses from the MC house."
        )

    def _luminary_emphasis_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        is_luminary = planet_code in luminary_codes
        return (1.0 if is_luminary else 0.0), (
            f"{planet_code} is a luminary." if is_luminary else f"{planet_code} is not a luminary."
        )

    def _house_rulership_load_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        _aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        counts = Counter(item.ruler_planet for item in house_rulers)
        max_count = max(counts.values(), default=0)
        if max_count <= 0:
            return 0.0, f"{planet_code} has no house rulership load."
        count = counts.get(planet_code, 0)
        return count / max_count, f"{planet_code} rules {count} houses."

    def _aspect_centrality_value(
        self,
        planet_code: str,
        candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _advanced_conditions: Sequence[Any],
        aspects: Sequence[Any],
        _luminary_codes: frozenset[str],
    ) -> tuple[float, str]:
        scores: Counter[str] = Counter()
        ranked_aspects = self._aspect_evaluator.rank(
            tuple(
                aspect.aspect_runtime
                for aspect in aspects
                if getattr(aspect, "aspect_runtime", None) is not None
            )
        )
        for ranked_aspect in ranked_aspects:
            runtime = ranked_aspect.aspect_runtime
            for participant in (
                runtime.participants.planet_a,
                runtime.participants.planet_b,
            ):
                if participant in candidate_planet_codes:
                    scores[participant] += ranked_aspect.dominance_score
        max_score = max(scores.values(), default=0.0)
        if max_score <= 0.0:
            return 0.0, f"{planet_code} has no significant aspect centrality."
        score = scores.get(planet_code, 0.0)
        return score / max_score, f"{planet_code} aspect centrality score is {score:.6g}."

    def _profile(
        self,
        planet_code: str,
        profiles: Sequence[PlanetConditionProfile],
    ) -> PlanetConditionProfile | None:
        """Retrouve le profil conditionnel d'une planete."""
        return next((profile for profile in profiles if profile.planet_code == planet_code), None)

    def _chart_ruler(self, house_rulers: Sequence[HouseRulerResult]) -> str | None:
        """Retourne le maitre de l'Ascendant deja resolu."""
        return next((item.ruler_planet for item in house_rulers if item.house_number == 1), None)

    def _most_elevated_planet(
        self,
        positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
    ) -> str | None:
        """Identifie la planete prioritaire en maison 10, puis proche du MC."""
        houses_by_number = {house.number: house for house in houses}
        scored: list[tuple[float, str]] = []
        for position in positions:
            house_number = self._planet_house(position.planet_code, positions)
            if house_number is None:
                continue
            distance_to_mc_house = min(abs(house_number - 10), 12 - abs(house_number - 10))
            score = 1.0 - (distance_to_mc_house / 6.0)
            if (
                house_number in houses_by_number
                and houses_by_number[house_number].house_kind == "angular"
            ):
                score = max(score, 0.75)
            scored.append((score, position.planet_code))
        if not scored:
            return None
        return sorted(scored, key=lambda item: (-item[0], item[1]))[0][1]

    def _planet_house(self, planet_code: str, positions: Sequence[Any]) -> int | None:
        """Retourne la maison calculee d'une planete."""
        return next(
            (
                position.house_number
                for position in positions
                if position.planet_code == planet_code
            ),
            None,
        )

    def _normalize(self, raw_value: float, min_value: float, max_value: float) -> float:
        """Normalise une valeur dans les bornes du profil de scoring."""
        bounded = min(max(raw_value, min_value), max_value)
        return round((bounded - min_value) / (max_value - min_value), 6)

    def _dominance_level(self, score: float) -> str:
        """Classe un score normalise dans les niveaux stables du brief."""
        if score < 0.2:
            return "very_low"
        if score < 0.4:
            return "low"
        if score < 0.6:
            return "moderate"
        if score < 0.8:
            return "high"
        return "dominant"

    def _explanation_facts(self, factors: tuple[PlanetDominanceFactor, ...]) -> tuple[str, ...]:
        """Expose les raisons positives sans produire de texte editorial."""
        return tuple(factor.reason for factor in factors if factor.normalized_value > 0.0)
