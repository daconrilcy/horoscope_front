"""Contrats immutables des resultats de dignites planetaires."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChartSectResult:
    """Contrat chart-level de secte calcule depuis les regles d'horizon."""

    chart_sect: str
    sun_horizon_position: str
    sun_above_horizon: bool
    calculation_basis: str
    reference_system: str

    def __post_init__(self) -> None:
        """Valide la forme publique stricte du contrat de secte."""
        if self.chart_sect not in {"day", "night"}:
            raise ValueError("chart_sect must be day or night")
        if self.sun_horizon_position not in {"above_horizon", "below_horizon"}:
            raise ValueError("sun_horizon_position must be above_horizon or below_horizon")
        if not isinstance(self.sun_above_horizon, bool):
            raise ValueError("sun_above_horizon must be a boolean")
        if not self.calculation_basis.strip():
            raise ValueError("calculation_basis is required")
        if not self.reference_system.strip():
            raise ValueError("reference_system is required")
        expected_horizon = "above_horizon" if self.chart_sect == "day" else "below_horizon"
        expected_above = self.chart_sect == "day"
        if self.sun_horizon_position != expected_horizon:
            raise ValueError("chart_sect and sun_horizon_position are inconsistent")
        if self.sun_above_horizon is not expected_above:
            raise ValueError("chart_sect and sun_above_horizon are inconsistent")


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
    chart_sect: ChartSectResult
    essential_score: float
    accidental_score: float
    total_score: float
    functional_strength_score: float
    expression_quality_score: float
    intensity_score: float
    essential_breakdown: tuple[EssentialDignityMatch, ...]
    accidental_breakdown: tuple[AccidentalDignityMatch, ...]
