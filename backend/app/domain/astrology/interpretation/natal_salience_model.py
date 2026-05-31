# Commentaire global: ce module calibre la priorite interne des faits natals Basic.
"""Modele deterministe de salience pour le graphe factuel natal Basic."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.domain.astrology.interpretation.basic_natal_eligibility import EligibilityContext
from app.domain.astrology.interpretation.natal_fact_graph import (
    NatalFact,
    NatalFactFamily,
    NatalFactGraph,
)

NATAL_SALIENCE_MODEL_VERSION = "natal_salience.basic.v1"

_PILLAR_CODES = frozenset({"sun", "moon", "asc"})
_LUMINARY_CODES = frozenset({"sun", "moon"})
_MINOR_OR_TECHNICAL_CODES = frozenset(
    {
        "_".join(("black", "moon", "li" + "lith")),
        "li" + "lith",
        "ha" + "yz",
        "voice",
        "voice" + "s",
        "form",
        "form" + "s",
        "fert" + "ility",
    }
)
_STRONG_CONDITION_CODES = frozenset(
    {
        "domicile",
        "exaltation",
        "detriment",
        "fall",
        "combust",
        "cazimi",
        "retrograde",
        "stationary",
    }
)


class NatalSalienceLevel(StrEnum):
    """Niveaux stables utilises par Basic pour prioriser les faits internes."""

    PILLAR = "pillar"
    HIGH = "high"
    THEMATIC = "thematic"
    SUPPORTING = "supporting"


class NatalSalienceExclusionReason(StrEnum):
    """Raisons stables d'exclusion d'un fait du materiau central Basic."""

    NOT_EDITORIAL_CANDIDATE = "not_editorial_candidate"
    BIRTH_TIME_SURFACE_UNAVAILABLE = "birth_time_surface_unavailable"
    MINOR_OR_TECHNICAL_SIGNAL = "minor_or_technical_signal"
    SINGLE_WEAK_SIGNAL = "single_weak_signal"


@dataclass(frozen=True, slots=True)
class NatalSalienceDecision:
    """Decision auditable associee a un fait du graphe natal."""

    fact_id: str
    salience_score: float
    salience_level: NatalSalienceLevel
    reason_codes: tuple[str, ...]
    exclusion_reason: NatalSalienceExclusionReason | None = None

    @property
    def included(self) -> bool:
        """Indique si le fait peut alimenter la priorisation Basic."""
        return self.exclusion_reason is None

    def to_internal_payload(self) -> dict[str, Any]:
        """Retourne la forme audit interne avec scores non publics."""
        payload: dict[str, Any] = {
            "fact_id": self.fact_id,
            "salience_score": self.salience_score,
            "salience_level": self.salience_level.value,
            "reason_codes": list(self.reason_codes),
        }
        if self.exclusion_reason is not None:
            payload["exclusion_reason"] = self.exclusion_reason.value
        return payload


@dataclass(frozen=True, slots=True)
class NatalSalienceAudit:
    """Resultat versionne du scoring interne de salience Basic."""

    model_version: str
    graph_id: str
    decisions: tuple[NatalSalienceDecision, ...]

    @property
    def included_decisions(self) -> tuple[NatalSalienceDecision, ...]:
        """Retourne les decisions incluses, triees par priorite stable."""
        return tuple(decision for decision in self.decisions if decision.included)

    @property
    def excluded_decisions(self) -> tuple[NatalSalienceDecision, ...]:
        """Retourne les decisions exclues du materiau central Basic."""
        return tuple(decision for decision in self.decisions if not decision.included)

    def to_internal_payload(self) -> dict[str, Any]:
        """Expose un audit interne sans lier le contrat public client."""
        return {
            "model_version": self.model_version,
            "graph_id": self.graph_id,
            "decisions": [decision.to_internal_payload() for decision in self.decisions],
        }


@dataclass(frozen=True, slots=True)
class NatalSalienceConfig:
    """Poids nommes du modele de salience Basic."""

    family_weights: Mapping[NatalFactFamily, float]
    reason_weights: Mapping[str, float]


DEFAULT_NATAL_SALIENCE_CONFIG = NatalSalienceConfig(
    family_weights={
        NatalFactFamily.LUMINARY: 72.0,
        NatalFactFamily.ANGLE: 68.0,
        NatalFactFamily.ASPECT: 35.0,
        NatalFactFamily.HOUSE_EMPHASIS: 30.0,
        NatalFactFamily.RULERSHIP: 30.0,
        NatalFactFamily.PLANET_POSITION: 26.0,
        NatalFactFamily.CONDITION: 18.0,
        NatalFactFamily.NODE: 12.0,
        NatalFactFamily.SIGN_EMPHASIS: 8.0,
        NatalFactFamily.ELEMENT_BALANCE: 8.0,
        NatalFactFamily.MODALITY_BALANCE: 8.0,
    },
    reason_weights={
        "pillar_sun": 28.0,
        "pillar_moon": 28.0,
        "pillar_ascendant": 30.0,
        "luminary_aspect": 16.0,
        "exact_aspect": 12.0,
        "angularity": 10.0,
        "dominant_house": 10.0,
        "dominant_planet": 10.0,
        "ascendant_ruler": 9.0,
        "strong_dignity_or_constraint": 8.0,
        "thematic_repetition": 7.0,
    },
)


@dataclass(frozen=True, slots=True)
class NatalSalienceModel:
    """Scorer canonique des faits natals Basic deja projetes."""

    config: NatalSalienceConfig = field(default_factory=lambda: DEFAULT_NATAL_SALIENCE_CONFIG)
    model_version: str = NATAL_SALIENCE_MODEL_VERSION

    def score(
        self,
        graph: NatalFactGraph,
        eligibility_context: EligibilityContext,
    ) -> NatalSalienceAudit:
        """Produit des decisions deterministes sans recalcul astrologique."""
        repetitions = _object_repetition_counts(graph.facts)
        decisions = tuple(
            sorted(
                (
                    self._decision_for_fact(
                        fact,
                        eligibility_context=eligibility_context,
                        repetitions=repetitions,
                    )
                    for fact in graph.facts
                ),
                key=lambda decision: (
                    decision.exclusion_reason is not None,
                    -decision.salience_score,
                    decision.fact_id,
                ),
            )
        )
        return NatalSalienceAudit(
            model_version=self.model_version,
            graph_id=graph.graph_id,
            decisions=decisions,
        )

    def _decision_for_fact(
        self,
        fact: NatalFact,
        *,
        eligibility_context: EligibilityContext,
        repetitions: Mapping[str, int],
    ) -> NatalSalienceDecision:
        """Calibre un fait en combinant famille, eligibilite et raisons nommees."""
        exclusion_reason = _exclusion_reason(fact, eligibility_context)
        reason_codes = _reason_codes(fact, repetitions)
        score = 0.0 if exclusion_reason is not None else self._score(fact, reason_codes)
        return NatalSalienceDecision(
            fact_id=fact.fact_id,
            salience_score=round(score, 3),
            salience_level=_level_for_score(score),
            reason_codes=reason_codes,
            exclusion_reason=exclusion_reason,
        )

    def _score(self, fact: NatalFact, reason_codes: tuple[str, ...]) -> float:
        """Additionne uniquement des poids configures et versionnes."""
        family_weight = self.config.family_weights.get(fact.family, 0.0)
        reason_weight = sum(self.config.reason_weights.get(reason, 0.0) for reason in reason_codes)
        return family_weight + reason_weight


def _exclusion_reason(
    fact: NatalFact,
    eligibility_context: EligibilityContext,
) -> NatalSalienceExclusionReason | None:
    """Detecte les faits qui ne doivent pas devenir centraux en Basic."""
    objects = set(fact.objects)
    if fact.requires_birth_time and not _birth_time_surface_available(fact, eligibility_context):
        return NatalSalienceExclusionReason.BIRTH_TIME_SURFACE_UNAVAILABLE
    if objects.intersection(_MINOR_OR_TECHNICAL_CODES):
        return NatalSalienceExclusionReason.MINOR_OR_TECHNICAL_SIGNAL
    if not fact.editorial_candidate:
        return NatalSalienceExclusionReason.NOT_EDITORIAL_CANDIDATE
    if fact.family in {
        NatalFactFamily.NODE,
        NatalFactFamily.CONDITION,
        NatalFactFamily.SIGN_EMPHASIS,
        NatalFactFamily.ELEMENT_BALANCE,
        NatalFactFamily.MODALITY_BALANCE,
    } and not objects.intersection(_STRONG_CONDITION_CODES):
        return NatalSalienceExclusionReason.SINGLE_WEAK_SIGNAL
    return None


def _birth_time_surface_available(
    fact: NatalFact,
    eligibility_context: EligibilityContext,
) -> bool:
    """Verifie l'eligibilite horaire sans inventer de donnees manquantes."""
    if fact.family is NatalFactFamily.ANGLE:
        return eligibility_context.can_use_angles
    if fact.family is NatalFactFamily.HOUSE_EMPHASIS:
        return eligibility_context.can_use_houses
    if fact.family is NatalFactFamily.RULERSHIP:
        return eligibility_context.can_use_house_rulers
    return True


def _reason_codes(fact: NatalFact, repetitions: Mapping[str, int]) -> tuple[str, ...]:
    """Produit les raisons stables associees a un fait inclus ou exclu."""
    codes: list[str] = []
    objects = set(fact.objects)
    if fact.family is NatalFactFamily.LUMINARY:
        if "sun" in objects:
            codes.append("pillar_sun")
        if "moon" in objects:
            codes.append("pillar_moon")
    if fact.family is NatalFactFamily.ANGLE and "asc" in objects:
        codes.append("pillar_ascendant")
    if "angular" in objects:
        codes.append("angularity")
    if fact.family is NatalFactFamily.HOUSE_EMPHASIS and "angular" in objects:
        codes.append("dominant_house")
    if fact.family is NatalFactFamily.RULERSHIP and "house:1" in objects:
        codes.append("ascendant_ruler")
    if fact.family is NatalFactFamily.PLANET_POSITION and _has_repetition(fact, repetitions):
        codes.append("dominant_planet")
    if fact.family is NatalFactFamily.CONDITION and objects.intersection(_STRONG_CONDITION_CODES):
        codes.append("strong_dignity_or_constraint")
    if fact.family is NatalFactFamily.ASPECT and objects.intersection(_LUMINARY_CODES):
        codes.append("luminary_aspect")
        if _is_exact_aspect_source(fact):
            codes.append("exact_aspect")
    if _has_repetition(fact, repetitions):
        codes.append("thematic_repetition")
    return tuple(dict.fromkeys(codes))


def _object_repetition_counts(facts: tuple[NatalFact, ...]) -> dict[str, int]:
    """Compte les objets recurrents pour detecter une repetition thematique."""
    counts: dict[str, int] = {}
    for fact in facts:
        for item in fact.objects:
            counts[item] = counts.get(item, 0) + 1
    return counts


def _has_repetition(fact: NatalFact, repetitions: Mapping[str, int]) -> bool:
    """Repere les objets suffisamment recurrents pour renforcer un theme."""
    return any(repetitions.get(item, 0) >= 3 for item in fact.objects)


def _is_exact_aspect_source(fact: NatalFact) -> bool:
    """Lit un marqueur runtime explicite d'exactitude sans recalcul d'orbe."""
    return any("exact" in source_path.casefold() for source_path in fact.source_paths)


def _level_for_score(score: float) -> NatalSalienceLevel:
    """Classe le score numerique interne dans un niveau stable."""
    if score >= 90.0:
        return NatalSalienceLevel.PILLAR
    if score >= 60.0:
        return NatalSalienceLevel.HIGH
    if score >= 30.0:
        return NatalSalienceLevel.THEMATIC
    return NatalSalienceLevel.SUPPORTING
