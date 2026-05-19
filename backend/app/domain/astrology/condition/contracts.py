"""Contrats immutables des profils conditionnels planetaires."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanetConditionBreakdownItem:
    """Contribution factuelle d'une dignite au profil conditionnel."""

    dignity_family: str
    dignity_type_code: str
    source: str
    reason: str
    score_value: float
    functional_strength: float
    visibility: float
    stability: float
    intensity: float
    coherence: float
    support: float
    constraint: float


@dataclass(frozen=True, slots=True)
class PlanetConditionExplanationFact:
    """Fait court et non narratif expose a une future couche de rendu."""

    fact_type: str
    value: str


@dataclass(frozen=True, slots=True)
class PlanetConditionProfile:
    """Profil conditionnel synthetique derive des dignites d'une planete."""

    planet_code: str
    score_profile: str
    tradition: str
    reference_version: str
    sect: str
    functional_strength: float
    visibility: float
    stability: float
    intensity: float
    coherence: float
    support: float
    constraint: float
    ranking_score: float
    condition_level: str
    breakdown: tuple[PlanetConditionBreakdownItem, ...]
    explanation_facts: tuple[PlanetConditionExplanationFact, ...]
