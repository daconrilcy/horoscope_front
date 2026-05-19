"""Contrats immutables du classement factuel des planetes dominantes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanetDominanceFactorType:
    """Facteur actif de dominance charge depuis le referentiel runtime."""

    code: str
    label: str
    category: str
    description: str
    default_weight: float
    sort_order: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class PlanetDominanceFactorContribution:
    """Contribution ponderee d'un facteur pour une planete."""

    factor_code: str
    raw_value: float
    weight: float
    weighted_value: float
    evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PlanetDominancePlanetResult:
    """Score final et preuves par facteur pour une planete."""

    planet_code: str
    rank: int
    dominance_score: float
    normalized_score: float
    factors: tuple[PlanetDominanceFactorContribution, ...]


@dataclass(frozen=True, slots=True)
class PlanetDominanceSummary:
    """Synthese technique non editoriale du classement dominant."""

    primary_planet: str | None
    chart_ruler: str | None
    most_visible_planet: str | None
    most_functional_planet: str | None
    angular_dominant_planet: str | None


@dataclass(frozen=True, slots=True)
class PlanetDominanceResult:
    """Classement complet des planetes dominantes pour un theme natal."""

    score_profile: str
    reference_version: str
    factor_types: tuple[PlanetDominanceFactorType, ...]
    planets: tuple[PlanetDominancePlanetResult, ...]
    summary: PlanetDominanceSummary
