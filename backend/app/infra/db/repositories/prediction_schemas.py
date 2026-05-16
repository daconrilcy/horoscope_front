"""Expose les DTO utilises par les repositories de reference prediction.

Les profils maison y sont scindes entre attributs astrologiques et produit.
"""

from dataclasses import dataclass
from typing import Any, Mapping

from app.domain.astrology.reference import HouseAstrologyProfile
from app.domain.prediction.context import CalibrationData

__all__ = [
    "AspectProfileData",
    "AspectOrbRuleData",
    "AstroPointData",
    "CalibrationData",
    "CategoryData",
    "EventTypeData",
    "HouseAstrologyProfile",
    "HouseCategoryWeightData",
    "HousePredictionProfile",
    "PlanetCategoryWeightData",
    "PlanetProfileData",
    "PlanetSignDignityData",
    "PointCategoryWeightData",
    "PredictionContext",
    "RulesetContext",
    "RulesetData",
]


@dataclass(frozen=True)
class CategoryData:
    id: int
    code: str
    name: str
    display_name: str
    sort_order: int
    is_enabled: bool


@dataclass(frozen=True)
class PlanetProfileData:
    """Vue runtime fusionnant configuration daily et référentiels planétaires."""

    planet_id: int
    code: str
    name: str
    class_code: str
    speed_rank: int
    speed_class: str
    weight_intraday: float
    weight_day_climate: float
    daily_visibility_score: float = 1.0
    daily_emotional_impact_score: float = 1.0
    daily_conscious_activation_score: float = 1.0
    is_enabled: bool = True
    micro_note: str | None = None
    typical_polarity: str | None = None
    orb_active_deg: float | None = None
    orb_peak_deg: float | None = None
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class HousePredictionProfile:
    """Profil produit d'une maison utilise par le moteur de prediction."""

    house_id: int
    house_number: int
    name: str
    visibility_weight: float
    base_priority: int
    keywords: tuple[str, ...]
    micro_note: str | None = None


@dataclass(frozen=True)
class PlanetCategoryWeightData:
    planet_id: int
    planet_code: str
    category_id: int
    category_code: str
    weight: float
    influence_role: str


@dataclass(frozen=True)
class PlanetSignDignityData:
    """Décrit une dignité planétaire normalisée pour un signe et un système."""

    sign_code: str
    planet_code: str
    dignity_type: str
    system: str
    weight: float
    is_primary: bool


@dataclass(frozen=True)
class HouseCategoryWeightData:
    house_id: int
    house_number: int
    category_id: int
    category_code: str
    weight: float
    routing_role: str


@dataclass(frozen=True)
class AstroPointData:
    point_id: int
    code: str
    name: str
    point_type: str


@dataclass(frozen=True)
class PointCategoryWeightData:
    point_id: int
    point_code: str
    category_id: int
    category_code: str
    weight: float


@dataclass(frozen=True)
class AspectProfileData:
    """Profil de scoring enrichi pour un aspect astrologique."""

    aspect_id: int
    code: str
    intensity_weight: float
    default_valence: str
    orb_multiplier: float
    phase_sensitive: bool
    interpretive_valence: str = "amplifying"
    polarity_score: float = 0.0
    energy_type: str = "contextual"
    phase_behavior: Mapping[str, Any] | None = None
    strength_thresholds: Mapping[str, Any] | None = None
    angle: float = 0.0
    family_code: str = ""


@dataclass(frozen=True)
class AspectOrbRuleData:
    """Règle d'orbe daily issue du référentiel versionné des aspects."""

    aspect_code: str
    system_code: str
    calculation_context: str
    source_body_type: str
    target_body_type: str
    orb_deg: float
    priority: int
    is_enabled: bool
    source_planet_code: str | None = None
    source_point_code: str | None = None
    target_planet_code: str | None = None
    target_point_code: str | None = None


@dataclass(frozen=True)
class RulesetData:
    id: int
    version: str
    reference_version_id: int
    zodiac_type: str
    coordinate_mode: str
    house_system: str
    time_step_minutes: int
    is_locked: bool


@dataclass(frozen=True)
class EventTypeData:
    id: int
    code: str
    name: str
    event_group: str | None
    priority: int
    base_weight: float


@dataclass(frozen=True)
class PredictionContext:
    categories: tuple[CategoryData, ...]
    planet_profiles: Mapping[str, PlanetProfileData]
    house_astrology_profiles: Mapping[int, HouseAstrologyProfile]
    house_prediction_profiles: Mapping[int, HousePredictionProfile]
    planet_category_weights: tuple[PlanetCategoryWeightData, ...]
    house_category_weights: tuple[HouseCategoryWeightData, ...]
    sign_rulerships: Mapping[str, str]
    aspect_profiles: Mapping[str, AspectProfileData]
    astro_points: Mapping[str, AstroPointData]
    point_category_weights: tuple[PointCategoryWeightData, ...]
    aspect_orb_rules: tuple[AspectOrbRuleData, ...] = ()
    aspect_system_inheritance: Mapping[str, str | None] | None = None


@dataclass(frozen=True)
class RulesetContext:
    ruleset: RulesetData
    parameters: Mapping[str, Any]
    event_types: Mapping[str, EventTypeData]
