"""Orchestration des scores de dignites planetaires natales."""

from __future__ import annotations

from app.domain.astrology.dignities.accidental_dignity_calculator import (
    AccidentalDignityCalculator,
)
from app.domain.astrology.dignities.advanced_condition_modifiers import (
    calculate_advanced_condition_modifiers,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    AccidentalDignityModifier,
    ChartSectResult,
    EssentialDignityMatch,
    PlanetDignityInput,
    PlanetDignityResult,
)
from app.domain.astrology.dignities.essential_dignity_calculator import (
    EssentialDignityCalculator,
)
from app.domain.astrology.dignities.planet_sect_condition_calculator import (
    PlanetSectConditionCalculator,
)
from app.domain.astrology.dignities.sect_calculator import SectCalculator
from app.domain.astrology.planetary_conditions.contracts import (
    AdvancedPlanetaryConditionsResult,
)
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class PlanetDignityScoringService:
    """Coordonne les calculateurs de dignites sous forme factuelle."""

    def __init__(
        self,
        essential_calculator: EssentialDignityCalculator | None = None,
        accidental_calculator: AccidentalDignityCalculator | None = None,
        sect_calculator: SectCalculator | None = None,
        planet_sect_condition_calculator: PlanetSectConditionCalculator | None = None,
    ) -> None:
        self.essential_calculator = essential_calculator or EssentialDignityCalculator()
        self.accidental_calculator = accidental_calculator or AccidentalDignityCalculator()
        self.sect_calculator = sect_calculator or SectCalculator()
        self.planet_sect_condition_calculator = (
            planet_sect_condition_calculator or PlanetSectConditionCalculator()
        )

    def calculate(
        self,
        planets: tuple[PlanetDignityInput, ...],
        runtime_reference: AstrologyRuntimeReference,
        score_profile: str | None = None,
        advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None = None,
    ) -> tuple[PlanetDignityResult, ...]:
        """Calcule un resultat de dignite pour chaque planete natale."""
        dignity_reference = runtime_reference.dignity_reference
        resolved_profile = score_profile or dignity_reference.default_score_profile
        tradition = self._tradition(dignity_reference.score_profiles, resolved_profile)
        chart_sect = self.sect_calculator.calculate(planets, dignity_reference)
        return tuple(
            self._calculate_planet(
                planet,
                planets=planets,
                runtime_reference=runtime_reference,
                score_profile=resolved_profile,
                tradition=tradition,
                chart_sect=chart_sect,
                advanced_planetary_conditions=advanced_planetary_conditions,
            )
            for planet in planets
        )

    def _calculate_planet(
        self,
        planet: PlanetDignityInput,
        *,
        planets: tuple[PlanetDignityInput, ...],
        runtime_reference: AstrologyRuntimeReference,
        score_profile: str,
        tradition: str,
        chart_sect: ChartSectResult,
        advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None,
    ) -> PlanetDignityResult:
        """Calcule et agrege les dignites d'une planete."""
        sect = chart_sect.chart_sect
        essential = self.essential_calculator.calculate(
            planet,
            signs=runtime_reference.signs,
            dignity_reference=runtime_reference.dignity_reference,
            score_profile=score_profile,
            sect=sect,
            tradition=tradition,
        )
        accidental = self.accidental_calculator.calculate(
            planet,
            all_planets=planets,
            dignity_reference=runtime_reference.dignity_reference,
            score_profile=score_profile,
            tradition=tradition,
            sect=sect,
            signs=runtime_reference.signs,
        )
        advanced_modifiers = self._advanced_condition_modifiers(
            planet,
            advanced_planetary_conditions,
        )
        essential_weights = self._weight_index(
            runtime_reference.dignity_reference.essential_weights[score_profile]
        )
        accidental_weights = self._weight_index(
            runtime_reference.dignity_reference.accidental_weights[score_profile]
        )
        essential_score = self._score(essential)
        accidental_score = self._score(accidental) + self._modifier_score(advanced_modifiers)
        return PlanetDignityResult(
            planet_code=planet.planet_code,
            score_profile=score_profile,
            tradition=tradition,
            reference_version=runtime_reference.reference_version,
            sect=sect,
            chart_sect=chart_sect,
            sect_condition=self.planet_sect_condition_calculator.calculate(
                planet,
                chart_sect=chart_sect,
                dignity_reference=runtime_reference.dignity_reference,
            ),
            essential_score=essential_score,
            accidental_score=accidental_score,
            total_score=essential_score + accidental_score,
            functional_strength_score=self._weighted_sum(
                essential, accidental, essential_weights, accidental_weights, "functional_weight"
            ),
            expression_quality_score=self._weighted_sum(
                essential, accidental, essential_weights, accidental_weights, "expression_weight"
            ),
            intensity_score=self._weighted_sum(
                essential, accidental, essential_weights, accidental_weights, "intensity_weight"
            ),
            essential_breakdown=essential,
            accidental_breakdown=accidental,
            advanced_condition_modifiers=advanced_modifiers,
        )

    def _tradition(self, profiles: object, score_profile: str) -> str:
        """Retourne la tradition associee au profil de scoring."""
        for profile in profiles:  # type: ignore[union-attr]
            if profile.code == score_profile:
                return profile.tradition
        raise ValueError(f"unknown dignity score profile: {score_profile}")

    def _score(
        self, matches: tuple[EssentialDignityMatch, ...] | tuple[AccidentalDignityMatch, ...]
    ) -> float:
        """Additionne les scores detectes."""
        return sum(match.score_value for match in matches)

    def _advanced_condition_modifiers(
        self,
        planet: PlanetDignityInput,
        advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None,
    ) -> tuple[AccidentalDignityModifier, ...]:
        """Retourne les modificateurs avances associes a la planete."""
        if advanced_planetary_conditions is None:
            return ()
        bundle = advanced_planetary_conditions.conditions_by_planet.get(planet.planet_code)
        if bundle is None:
            return ()
        return calculate_advanced_condition_modifiers(
            bundle=bundle,
            moon_phase=advanced_planetary_conditions.moon_phase,
        )

    def _modifier_score(self, modifiers: tuple[AccidentalDignityModifier, ...]) -> float:
        """Additionne les deltas avances sans poids runtime historique."""
        return sum(modifier.score_delta for modifier in modifiers)

    def _weight_index(self, weights: object) -> dict[str, object]:
        """Indexe les poids runtime par type de dignite."""
        return {weight.dignity_type_code: weight for weight in weights}  # type: ignore[union-attr]

    def _weighted_sum(
        self,
        essential: tuple[EssentialDignityMatch, ...],
        accidental: tuple[AccidentalDignityMatch, ...],
        essential_weights: dict[str, object],
        accidental_weights: dict[str, object],
        field_name: str,
    ) -> float:
        """Additionne un axe de poids configure par le runtime."""
        total = 0.0
        for match in essential:
            total += float(getattr(essential_weights[match.dignity_type_code], field_name))
        for match in accidental:
            total += float(getattr(accidental_weights[match.dignity_type_code], field_name))
        return total
