"""Contrats purs des conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PlanetConditionAxisImpact:
    """Variation normalisee appliquee aux axes conditionnels."""

    functional_strength_delta: float
    visibility_delta: float
    stability_delta: float
    intensity_delta: float
    coherence_delta: float
    support_delta: float
    constraint_delta: float


@dataclass(frozen=True, slots=True)
class AdvancedPlanetaryCondition:
    """Condition avancee factuelle rattachee a un type runtime parent."""

    condition_code: str
    condition_type_code: str
    source_planet_code: str
    target_planet_code: str | None
    score_profile: str
    reference_version: str
    score_impact: float
    ranking_weight: float
    axes_impact: PlanetConditionAxisImpact
    reason: str
    calculation_facts: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class HayzCondition:
    """Contrat explicite de hayz expose depuis les faits traditionnels calcules."""

    is_hayz: bool
    sect_match: bool
    hemisphere_match: bool | None
    sign_gender_match: bool | None
    calculation_basis: str
    reference_system: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RejoicingCondition:
    """Contrat explicite de joie planetaire expose depuis les dignites calculees."""

    is_rejoicing: bool
    current_house: int | None
    rejoicing_house: int | None
    calculation_basis: str
    reference_system: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TraditionalPlanetCondition:
    """Contrats traditionnels publics pour une planete."""

    planet_code: str
    hayz: HayzCondition
    rejoicing: RejoicingCondition


@dataclass(frozen=True, slots=True)
class TraditionalConditionsResult:
    """Ensemble des contrats traditionnels publics d'un theme natal."""

    planets: tuple[TraditionalPlanetCondition, ...]
