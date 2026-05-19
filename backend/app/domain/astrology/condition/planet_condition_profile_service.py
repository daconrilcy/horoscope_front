"""Service pur de normalisation conditionnelle des dignites planetaires."""

from __future__ import annotations

from app.domain.astrology.condition.contracts import (
    PlanetConditionBreakdownItem,
    PlanetConditionExplanationFact,
    PlanetConditionProfile,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    EssentialDignityMatch,
    PlanetDignityResult,
)
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    DignityScoreWeightReferenceData,
)


class PlanetConditionProfileService:
    """Agrège les resultats de dignite en profils conditionnels factuels."""

    def calculate(
        self,
        dignities: tuple[PlanetDignityResult, ...],
        runtime_reference: AstrologyRuntimeReference,
    ) -> tuple[PlanetConditionProfile, ...]:
        """Produit un profil conditionnel par resultat de dignite planetaire."""
        return tuple(
            self._profile_for_result(result, runtime_reference)
            for result in sorted(dignities, key=lambda item: item.planet_code)
        )

    def _profile_for_result(
        self,
        result: PlanetDignityResult,
        runtime_reference: AstrologyRuntimeReference,
    ) -> PlanetConditionProfile:
        """Construit un profil en reutilisant uniquement les poids runtime."""
        essential_weights = self._weight_index(
            runtime_reference.dignity_reference.essential_weights[result.score_profile]
        )
        accidental_weights = self._weight_index(
            runtime_reference.dignity_reference.accidental_weights[result.score_profile]
        )
        breakdown = (
            *self._breakdown_items("essential", result.essential_breakdown, essential_weights),
            *self._breakdown_items("accidental", result.accidental_breakdown, accidental_weights),
        )
        visibility = self._axis_sum(breakdown, "visibility")
        stability = self._axis_sum(breakdown, "stability")
        coherence = self._axis_sum(breakdown, "coherence")
        support = self._axis_sum(breakdown, "support")
        constraint = self._axis_sum(breakdown, "constraint")
        ranking_score = self._ranking_score(
            functional_strength=result.functional_strength_score,
            visibility=visibility,
            stability=stability,
            intensity=result.intensity_score,
            coherence=coherence,
            support=support,
            constraint=constraint,
        )
        return PlanetConditionProfile(
            planet_code=result.planet_code,
            score_profile=result.score_profile,
            tradition=result.tradition,
            reference_version=result.reference_version,
            sect=result.sect,
            functional_strength=round(result.functional_strength_score, 6),
            visibility=visibility,
            stability=stability,
            intensity=round(result.intensity_score, 6),
            coherence=coherence,
            support=support,
            constraint=constraint,
            ranking_score=ranking_score,
            condition_level=self._condition_level(ranking_score),
            breakdown=breakdown,
            explanation_facts=self._explanation_facts(result, ranking_score),
        )

    def _breakdown_items(
        self,
        dignity_family: str,
        matches: tuple[EssentialDignityMatch, ...] | tuple[AccidentalDignityMatch, ...],
        weights: dict[str, DignityScoreWeightReferenceData],
    ) -> tuple[PlanetConditionBreakdownItem, ...]:
        """Associe chaque match de dignite a ses axes de poids runtime."""
        items: list[PlanetConditionBreakdownItem] = []
        for match in matches:
            weight = weights[match.dignity_type_code]
            items.append(
                PlanetConditionBreakdownItem(
                    dignity_family=dignity_family,
                    dignity_type_code=match.dignity_type_code,
                    source=match.source,
                    reason=match.reason,
                    score_value=round(match.score_value, 6),
                    functional_strength=round(weight.functional_weight, 6),
                    visibility=round(weight.condition_visibility, 6),
                    stability=round(weight.condition_stability, 6),
                    intensity=round(weight.intensity_weight, 6),
                    coherence=round(weight.condition_coherence, 6),
                    support=round(weight.condition_support, 6),
                    constraint=round(weight.condition_constraint, 6),
                )
            )
        return tuple(items)

    def _weight_index(
        self,
        weights: tuple[DignityScoreWeightReferenceData, ...],
    ) -> dict[str, DignityScoreWeightReferenceData]:
        """Indexe les poids par code de dignite sans redefinir leurs valeurs."""
        return {weight.dignity_type_code: weight for weight in weights}

    def _axis_sum(
        self,
        breakdown: tuple[PlanetConditionBreakdownItem, ...],
        field_name: str,
    ) -> float:
        """Additionne un axe deja transporte par le runtime."""
        return round(sum(float(getattr(item, field_name)) for item in breakdown), 6)

    def _ranking_score(
        self,
        *,
        functional_strength: float,
        visibility: float,
        stability: float,
        intensity: float,
        coherence: float,
        support: float,
        constraint: float,
    ) -> float:
        """Classe le profil depuis les axes canoniques sans autre source."""
        return round(
            functional_strength
            + visibility
            + stability
            + intensity
            + coherence
            + support
            - constraint,
            6,
        )

    def _condition_level(self, ranking_score: float) -> str:
        """Discretise le score de classement de facon stable."""
        if ranking_score >= 3.0:
            return "strong"
        if ranking_score >= 1.0:
            return "supportive"
        if ranking_score > -1.0:
            return "mixed"
        if ranking_score > -3.0:
            return "challenged"
        return "strained"

    def _explanation_facts(
        self,
        result: PlanetDignityResult,
        ranking_score: float,
    ) -> tuple[PlanetConditionExplanationFact, ...]:
        """Expose des faits courts sans texte editorial."""
        return (
            PlanetConditionExplanationFact(
                "essential_match_count",
                str(len(result.essential_breakdown)),
            ),
            PlanetConditionExplanationFact(
                "accidental_match_count",
                str(len(result.accidental_breakdown)),
            ),
            PlanetConditionExplanationFact("ranking_score", f"{ranking_score:.6g}"),
        )
