from dataclasses import dataclass
from typing import Any, Mapping


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
    planet_id: int
    code: str
    name: str
    class_code: str
    speed_rank: int
    speed_class: str
    weight_intraday: float
    weight_day_climate: float
    typical_polarity: str | None
    orb_active_deg: float | None
    orb_peak_deg: float | None
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class HouseProfileData:
    house_id: int
    number: int
    name: str
    house_kind: str
    visibility_weight: float
    base_priority: int
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class PlanetCategoryWeightData:
    planet_id: int
    planet_code: str
    category_id: int
    category_code: str
    weight: float
    influence_role: str


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
    aspect_id: int
    code: str
    intensity_weight: float
    default_valence: str
    orb_multiplier: float
    phase_sensitive: bool


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
class CalibrationData:
    p05: float | None
    p25: float | None
    p50: float | None
    p75: float | None
    p95: float | None
    sample_size: int | None
    calibration_label: str | None = "provisional"


@dataclass(frozen=True)
class PredictionContext:
    categories: tuple[CategoryData, ...]
    planet_profiles: Mapping[str, PlanetProfileData]
    house_profiles: Mapping[int, HouseProfileData]
    planet_category_weights: tuple[PlanetCategoryWeightData, ...]
    house_category_weights: tuple[HouseCategoryWeightData, ...]
    sign_rulerships: Mapping[str, str]
    aspect_profiles: Mapping[str, AspectProfileData]
    astro_points: Mapping[str, AstroPointData]
    point_category_weights: tuple[PointCategoryWeightData, ...]


@dataclass(frozen=True)
class RulesetContext:
    ruleset: RulesetData
    parameters: Mapping[str, Any]
    event_types: Mapping[str, EventTypeData]
