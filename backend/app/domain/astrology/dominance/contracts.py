"""Contrats immutables du classement factuel des planetes dominantes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanetDominanceFactor:
    """Contribution normalisee d'un facteur pour une planete."""

    factor_code: str
    raw_value: float
    normalized_value: float
    weight: float
    weighted_score: float
    reason: str


@dataclass(frozen=True, slots=True)
class PlanetDominanceResult:
    """Score final et preuves explicables pour une planete."""

    planet_code: str
    total_score: float
    rank: int
    dominance_level: str
    factors: tuple[PlanetDominanceFactor, ...]
    explanation_facts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DominantPlanetsResult:
    """Classement complet des planetes dominantes pour un theme natal."""

    score_profile_code: str
    tradition_code: str
    reference_version_code: str
    planets: tuple[PlanetDominanceResult, ...]
    top_planet_code: str | None
    chart_ruler_code: str | None
    most_elevated_planet_code: str | None
