"""Contrats purs des conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import dataclass


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
