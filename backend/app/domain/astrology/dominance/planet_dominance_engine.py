"""Moteur pur de classement factuel des dominantes planetaires."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any

from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.dominance.contracts import (
    PlanetDominanceFactorContribution,
    PlanetDominanceFactorType,
    PlanetDominancePlanetResult,
    PlanetDominanceResult,
    PlanetDominanceSummary,
)
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation.dominant_aspects import DominantAspectEvaluator
from app.domain.astrology.runtime.chart_signature_runtime_data import ChartBalanceRuntimeData
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


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
        chart_balance: ChartBalanceRuntimeData | None,
    ) -> PlanetDominanceResult:
        """Produit un classement pondere par les facteurs actifs du runtime."""
        factor_types = tuple(
            PlanetDominanceFactorType(
                code=item.code,
                label=item.label,
                category=item.category,
                description=item.description,
                default_weight=round(item.default_weight, 6),
                sort_order=item.sort_order,
                is_active=item.is_active,
            )
            for item in runtime_reference.dominance_factor_types
            if item.is_active
        )
        planet_codes = tuple(position.planet_code for position in planet_positions)
        luminary_codes = frozenset(
            planet.code for planet in runtime_reference.planets.items if planet.is_luminary
        )
        total_weight = sum(factor.default_weight for factor in factor_types)
        if total_weight <= 0.0:
            raise ValueError("dominance factors require a positive total weight")

        results = []
        for planet_code in planet_codes:
            contributions = tuple(
                self._contribution(
                    factor=factor,
                    planet_code=planet_code,
                    planet_positions=planet_positions,
                    houses=houses,
                    house_rulers=house_rulers,
                    condition_profiles=condition_profiles,
                    aspects=aspects,
                    chart_balance=chart_balance,
                    luminary_codes=luminary_codes,
                )
                for factor in factor_types
            )
            normalized_score = round(
                sum(item.weighted_value for item in contributions) / total_weight,
                6,
            )
            results.append((planet_code, normalized_score, contributions))

        ordered = sorted(results, key=lambda item: (-item[1], item[0]))
        planets = tuple(
            PlanetDominancePlanetResult(
                planet_code=planet_code,
                rank=index + 1,
                dominance_score=score,
                normalized_score=score,
                factors=contributions,
            )
            for index, (planet_code, score, contributions) in enumerate(ordered)
        )
        return PlanetDominanceResult(
            score_profile="planet_dominance_v1",
            reference_version=runtime_reference.reference_version,
            factor_types=factor_types,
            planets=planets,
            summary=self._summary(planets, house_rulers, condition_profiles, houses),
        )

    def _contribution(
        self,
        *,
        factor: PlanetDominanceFactorType,
        planet_code: str,
        planet_positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        condition_profiles: Sequence[PlanetConditionProfile],
        aspects: Sequence[Any],
        chart_balance: ChartBalanceRuntimeData | None,
        luminary_codes: frozenset[str],
    ) -> PlanetDominanceFactorContribution:
        """Calcule une contribution en dispatchant vers le facteur runtime."""
        raw_value, evidence = {
            "chart_ruler": self._chart_ruler_value,
            "angularity": self._angularity_value,
            "condition_strength": self._condition_strength_value,
            "visibility": self._visibility_value,
            "most_elevated": self._most_elevated_value,
            "luminary_emphasis": self._luminary_emphasis_value,
            "house_rulership_load": self._house_rulership_load_value,
            "aspect_centrality": self._aspect_centrality_value,
        }[factor.code](
            planet_code,
            frozenset(position.planet_code for position in planet_positions),
            planet_positions,
            houses,
            house_rulers,
            condition_profiles,
            aspects,
            chart_balance,
            luminary_codes,
        )
        bounded_raw = round(min(max(raw_value, 0.0), 1.0), 6)
        weight = round(factor.default_weight, 6)
        return PlanetDominanceFactorContribution(
            factor_code=factor.code,
            raw_value=bounded_raw,
            weight=weight,
            weighted_value=round(bounded_raw * weight, 6),
            evidence=tuple(evidence),
        )

    def _chart_ruler_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        ruler = next((item.ruler_planet for item in house_rulers if item.house_number == 1), None)
        return (1.0 if ruler == planet_code else 0.0), (f"house_1_ruler:{ruler}",)

    def _angularity_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
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
            return score, (f"house:{house.number}", f"house_kind:{house.house_kind}")
        return 0.0, ("house:not_found",)

    def _condition_strength_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        profile = self._profile(planet_code, profiles)
        max_strength = max((max(item.functional_strength, 0.0) for item in profiles), default=0.0)
        if profile is None or max_strength <= 0.0:
            return 0.0, ("condition_strength:missing",)
        return profile.functional_strength / max_strength, (
            f"functional_strength:{profile.functional_strength:.6g}",
        )

    def _visibility_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        profile = self._profile(planet_code, profiles)
        max_visibility = max((max(item.visibility, 0.0) for item in profiles), default=0.0)
        if profile is None or max_visibility <= 0.0:
            return 0.0, ("visibility:missing",)
        return profile.visibility / max_visibility, (f"visibility:{profile.visibility:.6g}",)

    def _most_elevated_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        positions: Sequence[Any],
        houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        houses_by_number = {house.number: house for house in houses}
        planet_house = next(
            (
                position.house_number
                for position in positions
                if position.planet_code == planet_code
            ),
            None,
        )
        if planet_house is None:
            return 0.0, ("house:missing",)
        distance_to_mc_house = min(abs(planet_house - 10), 12 - abs(planet_house - 10))
        base = max(0.0, 1.0 - (distance_to_mc_house / 6.0))
        if (
            planet_house in houses_by_number
            and houses_by_number[planet_house].house_kind == "angular"
        ):
            base = max(base, 0.75)
        return base, (f"house:{planet_house}",)

    def _luminary_emphasis_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        is_luminary = planet_code in luminary_codes
        return (1.0 if is_luminary else 0.0), (f"luminary:{str(is_luminary).lower()}",)

    def _house_rulership_load_value(
        self,
        planet_code: str,
        _candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        _aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        counts = Counter(item.ruler_planet for item in house_rulers)
        max_count = max(counts.values(), default=0)
        if max_count <= 0:
            return 0.0, ("rulership_load:missing",)
        count = counts.get(planet_code, 0)
        return count / max_count, (f"ruled_house_count:{count}",)

    def _aspect_centrality_value(
        self,
        planet_code: str,
        candidate_planet_codes: frozenset[str],
        _positions: Sequence[Any],
        _houses: Sequence[HouseRuntimeData],
        _house_rulers: Sequence[HouseRulerResult],
        _profiles: Sequence[PlanetConditionProfile],
        aspects: Sequence[Any],
        _balance: ChartBalanceRuntimeData | None,
        _luminary_codes: frozenset[str],
    ) -> tuple[float, tuple[str, ...]]:
        scores: Counter[str] = Counter()
        evidences: dict[str, list[str]] = {}
        ranked_aspects = self._aspect_evaluator.rank(
            tuple(
                aspect.aspect_runtime
                for aspect in aspects
                if getattr(aspect, "aspect_runtime", None) is not None
            )
        )
        for ranked_aspect in ranked_aspects:
            runtime = ranked_aspect.aspect_runtime
            evidence = f"dominant_aspect:{runtime.aspect.code}:rank:{ranked_aspect.rank}"
            for participant in (
                runtime.participants.planet_a,
                runtime.participants.planet_b,
            ):
                if participant not in candidate_planet_codes:
                    continue
                scores[participant] += ranked_aspect.dominance_score
                evidences.setdefault(participant, []).append(evidence)
        max_score = max(scores.values(), default=0.0)
        if max_score > 0.0:
            score = scores.get(planet_code, 0.0)
            return score / max_score, tuple(
                evidences.get(planet_code, ["dominant_aspect:not_in_rank"])
            )

        return 0.0, ("dominant_aspect:missing",)

    def _profile(
        self,
        planet_code: str,
        profiles: Sequence[PlanetConditionProfile],
    ) -> PlanetConditionProfile | None:
        """Retrouve le profil conditionnel d'une planete."""
        return next((profile for profile in profiles if profile.planet_code == planet_code), None)

    def _summary(
        self,
        planets: tuple[PlanetDominancePlanetResult, ...],
        house_rulers: Sequence[HouseRulerResult],
        profiles: Sequence[PlanetConditionProfile],
        houses: Sequence[HouseRuntimeData],
    ) -> PlanetDominanceSummary:
        """Construit une synthese technique depuis les meilleurs scores."""
        chart_ruler = next(
            (item.ruler_planet for item in house_rulers if item.house_number == 1),
            None,
        )
        most_visible = max(
            profiles, key=lambda item: (item.visibility, item.planet_code), default=None
        )
        most_functional = max(
            profiles,
            key=lambda item: (item.functional_strength, item.planet_code),
            default=None,
        )
        angular_counts = Counter(
            occupant.planet
            for house in houses
            if house.house_kind == "angular"
            for occupant in house.occupants
        )
        angular_planet = (
            sorted(angular_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
            if angular_counts
            else None
        )
        return PlanetDominanceSummary(
            primary_planet=planets[0].planet_code if planets else None,
            chart_ruler=chart_ruler,
            most_visible_planet=most_visible.planet_code if most_visible is not None else None,
            most_functional_planet=(
                most_functional.planet_code if most_functional is not None else None
            ),
            angular_dominant_planet=angular_planet,
        )
