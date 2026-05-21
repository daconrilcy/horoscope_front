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

    planet_code: str
    is_hayz: bool
    sect_match: bool
    hemisphere_match: bool | None
    sign_gender_match: bool | None
    chart_sect: str
    intrinsic_sect: str
    planet_sect_condition: str
    planet_horizon_position: str
    sign_gender: str
    calculation_basis: str
    reference_system: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RejoicingCondition:
    """Contrat explicite de joie planetaire expose depuis les dignites calculees."""

    planet_code: str
    is_rejoicing: bool
    current_house: int | None
    rejoicing_house: int | None
    calculation_basis: str
    reference_system: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SectNatureMitigationCondition:
    """Contrat explicite de modulation benefique/malefique par la secte."""

    planet_code: str
    planet_nature: str
    chart_sect: str
    intrinsic_sect: str
    planet_sect_condition: str
    is_in_sect: bool
    is_out_of_sect: bool
    mitigation_state: str
    condition_code: str
    condition_family: str
    calculation_basis: str
    reference_system: str
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Valide la forme publique stricte du contrat CS-206."""
        if not self.planet_code.strip():
            raise ValueError("planet_code is required")
        if self.planet_nature not in {
            "benefic",
            "malefic",
            "mixed",
            "neutral",
            "luminary",
            "unknown",
        }:
            raise ValueError("planet_nature is invalid")
        if self.chart_sect not in {"day", "night"}:
            raise ValueError("chart_sect must be day or night")
        if self.intrinsic_sect not in {"diurnal", "nocturnal", "common", "neutral", "unknown"}:
            raise ValueError("intrinsic_sect is invalid")
        if self.planet_sect_condition not in {
            "in_sect",
            "out_of_sect",
            "neutral_to_sect",
            "variable_by_condition",
            "unknown",
        }:
            raise ValueError("planet_sect_condition is invalid")
        if not isinstance(self.is_in_sect, bool) or not isinstance(self.is_out_of_sect, bool):
            raise ValueError("sect flags must be booleans")
        if self.mitigation_state not in {
            "mitigated",
            "aggravated",
            "supported",
            "weakened",
            "neutral",
            "unknown",
        }:
            raise ValueError("mitigation_state is invalid")
        if self.condition_family != "sect_nature_mitigation":
            raise ValueError("condition_family must be sect_nature_mitigation")
        if self.condition_code not in {
            "malefic_mitigated_by_sect",
            "malefic_aggravated_out_of_sect",
            "benefic_supported_by_sect",
            "benefic_weakened_out_of_sect",
            "sect_nature_neutral",
            "sect_nature_unknown",
        }:
            raise ValueError("condition_code is invalid")
        if not self.calculation_basis.strip():
            raise ValueError("calculation_basis is required")
        if not self.reference_system.strip():
            raise ValueError("reference_system is required")


@dataclass(frozen=True, slots=True)
class TraditionalPlanetCondition:
    """Contrats traditionnels publics pour une planete."""

    planet_code: str
    hayz: HayzCondition
    rejoicing: RejoicingCondition
    sect_nature_mitigation: SectNatureMitigationCondition | None = None


@dataclass(frozen=True, slots=True)
class TraditionalConditionsResult:
    """Ensemble des contrats traditionnels publics d'un theme natal."""

    planets: tuple[TraditionalPlanetCondition, ...]
