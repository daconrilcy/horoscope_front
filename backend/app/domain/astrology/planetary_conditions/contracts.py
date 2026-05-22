"""Contrats immutables des conditions planetaires avancees futures."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Mapping


class ConditionSeverity(StrEnum):
    """Niveau d'intensite factuelle d'une condition planetaire."""

    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    EXTREME = "extreme"


class ConditionConfidence(StrEnum):
    """Niveau de confiance associe a un fait conditionnel."""

    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXACT = "exact"


class SolarProximityConditionKey(StrEnum):
    """Etat de proximite geocentrique entre une planete et le Soleil."""

    NONE = "none"
    CAZIMI = "cazimi"
    COMBUST = "combust"
    UNDER_BEAMS = "under_beams"


class SolarPhaseRelationKey(StrEnum):
    """Relation de phase solaire d'une planete."""

    UNKNOWN = "unknown"
    ORIENTAL = "oriental"
    OCCIDENTAL = "occidental"
    CONJUNCT_SOLAR = "conjunct_solar"


class PlanetaryMotionDirection(StrEnum):
    """Direction apparente du mouvement planetaire."""

    DIRECT = "direct"
    RETROGRADE = "retrograde"
    STATIONARY = "stationary"
    UNKNOWN = "unknown"


class PlanetarySpeedState(StrEnum):
    """Classe de vitesse apparente d'une planete."""

    UNKNOWN = "unknown"
    VERY_SLOW = "very_slow"
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"
    VERY_FAST = "very_fast"


@dataclass(frozen=True, slots=True)
class PlanetaryMotionProfile:
    """Seuils factuels utilises pour classer le mouvement d'une planete."""

    planet_key: str
    mean_speed_deg_per_day: float
    stationary_threshold_abs: float
    very_slow_ratio_threshold: float = 0.4
    slow_ratio_threshold: float = 0.8
    fast_ratio_threshold: float = 1.2
    very_fast_ratio_threshold: float = 1.6

    def __post_init__(self) -> None:
        """Valide les seuils de classification sans imposer la vitesse moyenne."""
        if not isfinite(self.mean_speed_deg_per_day):
            raise ValueError("mean speed must be finite")
        if not isfinite(self.stationary_threshold_abs):
            raise ValueError("stationary threshold must be finite")
        if self.stationary_threshold_abs < 0:
            raise ValueError("stationary threshold must be greater than or equal to zero")
        ratio_thresholds = (
            self.very_slow_ratio_threshold,
            self.slow_ratio_threshold,
            self.fast_ratio_threshold,
            self.very_fast_ratio_threshold,
        )
        if any(not isfinite(threshold) for threshold in ratio_thresholds):
            raise ValueError("speed ratio thresholds must be finite")
        if not (
            0
            <= self.very_slow_ratio_threshold
            <= self.slow_ratio_threshold
            <= self.fast_ratio_threshold
            <= self.very_fast_ratio_threshold
        ):
            raise ValueError(
                "speed ratio thresholds must satisfy 0 <= very_slow <= slow <= fast <= very_fast"
            )


class PlanetVisibilityKey(StrEnum):
    """Etat de visibilite astronomique ou heliacale d'une planete."""

    UNKNOWN = "unknown"
    VISIBLE = "visible"
    CONJUNCT_SOLAR = "conjunct_solar"
    INVISIBLE = "invisible"
    UNDER_BEAMS = "under_beams"
    EMERGING = "emerging"
    HELIACAL_RISING = "heliacal_rising"
    HELIACAL_SETTING = "heliacal_setting"


class MoonPhaseKey(StrEnum):
    """Phase lunaire normalisee."""

    UNKNOWN = "unknown"
    NEW_MOON = "new_moon"
    WAXING_CRESCENT = "waxing_crescent"
    FIRST_QUARTER = "first_quarter"
    WAXING_GIBBOUS = "waxing_gibbous"
    FULL_MOON = "full_moon"
    WANING_GIBBOUS = "waning_gibbous"
    LAST_QUARTER = "last_quarter"
    WANING_CRESCENT = "waning_crescent"
    BALSAMIC = "balsamic"


class WaxingWaningState(StrEnum):
    """Etat croissant, decroissant ou exact de la phase lunaire."""

    UNKNOWN = "unknown"
    WAXING = "waxing"
    WANING = "waning"
    EXACT = "exact"


class PlanetaryConditionFamily(StrEnum):
    """Famille canonique d'une condition planetaire avancee."""

    SOLAR_PROXIMITY = "solar_proximity"
    SOLAR_PHASE = "solar_phase"
    MOTION = "motion"
    VISIBILITY = "visibility"
    LUNAR_PHASE = "lunar_phase"


@dataclass(frozen=True, slots=True)
class SolarProximityThresholds:
    """Seuils angulaires utilises pour classer la proximite solaire."""

    cazimi_max_distance_deg: float = 17.0 / 60.0
    combust_max_distance_deg: float = 8.5
    under_beams_max_distance_deg: float = 15.0

    def __post_init__(self) -> None:
        """Valide l'ordre strictement canonique des seuils solaires."""
        if not (
            0
            <= self.cazimi_max_distance_deg
            <= self.combust_max_distance_deg
            <= self.under_beams_max_distance_deg
        ):
            raise ValueError(
                "solar proximity thresholds must satisfy 0 <= cazimi <= combust <= under_beams"
            )


@dataclass(frozen=True, slots=True)
class SolarPhaseRelationThresholds:
    """Seuil de conjonction utilise pour la relation solaire geometrique."""

    conjunction_tolerance_deg: float = 0.5

    def __post_init__(self) -> None:
        """Valide la tolerance sans autoriser une absorption du demi-cercle."""
        if not isfinite(self.conjunction_tolerance_deg):
            raise ValueError("conjunction tolerance must be finite")
        if self.conjunction_tolerance_deg < 0:
            raise ValueError("conjunction tolerance must be greater than or equal to zero")
        if self.conjunction_tolerance_deg >= 180.0:
            raise ValueError("conjunction tolerance must be less than 180")


@dataclass(frozen=True, slots=True)
class PlanetVisibilityThresholds:
    """Seuils angulaires de composition de la visibilite planetaire."""

    conjunction_tolerance_deg: float = 0.5
    under_beams_limit_deg: float = 15.0
    emerging_limit_deg: float = 18.0

    def __post_init__(self) -> None:
        """Valide des seuils finis, positifs et ordonnes."""
        thresholds = (
            self.conjunction_tolerance_deg,
            self.under_beams_limit_deg,
            self.emerging_limit_deg,
        )
        if any(not isfinite(threshold) for threshold in thresholds):
            raise ValueError("planet visibility thresholds must be finite")
        if not (
            0
            <= self.conjunction_tolerance_deg
            <= self.under_beams_limit_deg
            <= self.emerging_limit_deg
        ):
            raise ValueError(
                "planet visibility thresholds must satisfy "
                "0 <= conjunction <= under_beams <= emerging"
            )


@dataclass(frozen=True, slots=True)
class SolarProximityCondition:
    """Contrat factuel de proximite entre une planete et le Soleil."""

    planet_key: str
    condition_key: SolarProximityConditionKey
    sun_distance_deg: float
    orb_deg: float | None
    severity: ConditionSeverity
    is_active: bool
    source: str = "solar_proximity"


@dataclass(frozen=True, slots=True)
class PlanetarySolarPhaseRelation:
    """Contrat factuel de relation oriental-occidental au Soleil."""

    planet_key: str
    relation_key: SolarPhaseRelationKey
    angular_distance_deg: float
    is_oriental: bool | None
    is_occidental: bool | None


@dataclass(frozen=True, slots=True)
class PlanetaryMotionCondition:
    """Contrat factuel du mouvement et de la vitesse planetaire."""

    planet_key: str
    speed_deg_per_day: float
    absolute_speed_deg_per_day: float
    direction: PlanetaryMotionDirection
    speed_state: PlanetarySpeedState
    is_retrograde: bool
    is_stationary: bool
    normalized_speed_ratio: float | None


@dataclass(frozen=True, slots=True)
class PlanetVisibilityCondition:
    """Contrat factuel de visibilite d'une planete."""

    planet_key: str
    visibility_key: PlanetVisibilityKey
    is_visible: bool | None
    confidence: ConditionConfidence
    reason: str | None


@dataclass(frozen=True, slots=True)
class MoonPhaseCondition:
    """Contrat factuel de phase lunaire globale du theme."""

    phase_key: MoonPhaseKey
    sun_moon_angle_deg: float
    illumination_ratio: float | None
    waxing_or_waning: WaxingWaningState
    phase_index: int | None


@dataclass(frozen=True, slots=True)
class PlanetaryConditionSignal:
    """Signal technique non narratif rattache a une condition avancee."""

    planet_key: str
    condition_key: str
    condition_family: PlanetaryConditionFamily
    severity: ConditionSeverity
    confidence: ConditionConfidence
    is_active: bool
    value: float | None
    unit: str | None
    metadata: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        """Fige la metadata technique fournie par l'appelant."""
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PlanetaryConditionsBundle:
    """Regroupement partiel des conditions avancees d'une planete."""

    planet_key: str
    solar_proximity: SolarProximityCondition | None = None
    solar_phase_relation: PlanetarySolarPhaseRelation | None = None
    motion: PlanetaryMotionCondition | None = None
    visibility: PlanetVisibilityCondition | None = None
    signals: tuple[PlanetaryConditionSignal, ...] = ()

    def __post_init__(self) -> None:
        """Fige les signaux fournis pour garantir un contrat immuable."""
        object.__setattr__(self, "signals", tuple(self.signals))


@dataclass(frozen=True, slots=True)
class AdvancedPlanetaryConditionsResult:
    """Resultat contractuel global des conditions planetaires avancees."""

    conditions_by_planet: Mapping[str, PlanetaryConditionsBundle]
    moon_phase: MoonPhaseCondition | None = None
    signals: tuple[PlanetaryConditionSignal, ...] = ()

    def __post_init__(self) -> None:
        """Fige les collections globales des conditions planetaires."""
        object.__setattr__(
            self,
            "conditions_by_planet",
            MappingProxyType(dict(self.conditions_by_planet)),
        )
        object.__setattr__(self, "signals", tuple(self.signals))
