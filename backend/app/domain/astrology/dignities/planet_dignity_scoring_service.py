"""Orchestration des scores de dignites planetaires natales."""

from __future__ import annotations

from app.domain.astrology.dignities.accidental_dignity_calculator import (
    AccidentalDignityCalculator,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    EssentialDignityMatch,
    PlanetDignityInput,
    PlanetDignityResult,
)
from app.domain.astrology.dignities.essential_dignity_calculator import (
    EssentialDignityCalculator,
)
from app.domain.astrology.dignities.sect_calculator import SectCalculator
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class PlanetDignityScoringService:
    """Coordonne les calculateurs de dignites sous forme factuelle."""

    def __init__(
        self,
        essential_calculator: EssentialDignityCalculator | None = None,
        accidental_calculator: AccidentalDignityCalculator | None = None,
        sect_calculator: SectCalculator | None = None,
    ) -> None:
        self.essential_calculator = essential_calculator or EssentialDignityCalculator()
        self.accidental_calculator = accidental_calculator or AccidentalDignityCalculator()
        self.sect_calculator = sect_calculator or SectCalculator()

    def calculate(
        self,
        planets: tuple[PlanetDignityInput, ...],
        runtime_reference: AstrologyRuntimeReference,
        score_profile: str | None = None,
    ) -> tuple[PlanetDignityResult, ...]:
        """Calcule un resultat de dignite pour chaque planete natale."""
        dignity_reference = runtime_reference.dignity_reference
        resolved_profile = score_profile or dignity_reference.default_score_profile
        tradition = self._tradition(dignity_reference.score_profiles, resolved_profile)
        sect = self.sect_calculator.calculate(planets, dignity_reference)
        return tuple(
            self._calculate_planet(
                planet,
                planets=planets,
                runtime_reference=runtime_reference,
                score_profile=resolved_profile,
                tradition=tradition,
                sect=sect,
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
        sect: str,
    ) -> PlanetDignityResult:
        """Calcule et agrege les dignites d'une planete."""
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
        essential_weights = self._weight_index(
            runtime_reference.dignity_reference.essential_weights[score_profile]
        )
        accidental_weights = self._weight_index(
            runtime_reference.dignity_reference.accidental_weights[score_profile]
        )
        return PlanetDignityResult(
            planet_code=planet.planet_code,
            score_profile=score_profile,
            tradition=tradition,
            reference_version=runtime_reference.reference_version,
            sect=sect,
            essential_score=self._score(essential),
            accidental_score=self._score(accidental),
            total_score=self._score(essential) + self._score(accidental),
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
