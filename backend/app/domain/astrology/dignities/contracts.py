"""Contrats immutables des resultats de dignites planetaires."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DignityWeight:
    """Poids de scoring applique a une dignite detectee."""

    dignity_type_code: str
    score_value: float
    functional_weight: float
    expression_weight: float
    intensity_weight: float


@dataclass(frozen=True, slots=True)
class EssentialDignityMatch:
    """Dignite essentielle detectee pour une planete."""

    dignity_type_code: str
    score_value: float
    source: str
    reason: str
    sign_code: str
    degree_start: float
    degree_end: float


@dataclass(frozen=True, slots=True)
class AccidentalDignityMatch:
    """Dignite accidentelle detectee pour une planete."""

    dignity_type_code: str
    score_value: float
    source: str
    reason: str
    condition: str


@dataclass(frozen=True, slots=True)
class PlanetDignityInput:
    """Donnees natales objectives necessaires au calcul d'une planete."""

    planet_code: str
    longitude: float
    sign_code: str
    house_number: int
    speed_longitude: float | None
    is_retrograde: bool | None

    @property
    def degree_in_sign(self) -> float:
        """Retourne le degre zodiacal local dans le signe."""
        return self.longitude % 30.0


@dataclass(frozen=True, slots=True)
class PlanetDignityResult:
    """Resultat factuel agrege pour une planete."""

    planet_code: str
    score_profile: str
    tradition: str
    reference_version: str
    sect: str
    essential_score: float
    accidental_score: float
    total_score: float
    functional_strength_score: float
    expression_quality_score: float
    intensity_score: float
    essential_breakdown: tuple[EssentialDignityMatch, ...]
    accidental_breakdown: tuple[AccidentalDignityMatch, ...]
