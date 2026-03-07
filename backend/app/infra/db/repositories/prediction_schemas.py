from dataclasses import dataclass
from typing import Any


@dataclass
class CategoryData:
    id: int
    code: str
    name: str
    display_name: str
    sort_order: int
    is_enabled: bool


@dataclass
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
    keywords: list[str]


@dataclass
class HouseProfileData:
    house_id: int
    number: int
    name: str
    house_kind: str
    visibility_weight: float
    base_priority: int
    keywords: list[str]


@dataclass
class PlanetCategoryWeightData:
    planet_id: int
    planet_code: str
    category_id: int
    category_code: str
    weight: float
    influence_role: str


@dataclass
class HouseCategoryWeightData:
    house_id: int
    house_number: int
    category_id: int
    category_code: str
    weight: float
    influence_role: str


@dataclass
class AstroPointData:
    point_id: int
    code: str
    name: str
    point_type: str


@dataclass
class PointCategoryWeightData:
    point_id: int
    point_code: str
    category_id: int
    category_code: str
    weight: float


@dataclass
class AspectProfileData:
    aspect_id: int
    code: str
    intensity_weight: float
    default_valence: str
    orb_multiplier: float
    phase_sensitive: bool


@dataclass
class RulesetData:
    id: int
    version: str
    reference_version_id: int
    zodiac_type: str
    coordinate_mode: str
    house_system: str
    time_step_minutes: int
    is_locked: bool


@dataclass
class EventTypeData:
    id: int
    code: str
    name: str
    event_group: str | None
    priority: int
    base_weight: float


@dataclass
class CalibrationData:
    p05: float | None
    p25: float | None
    p50: float | None
    p75: float | None
    p95: float | None
    sample_size: int | None


@dataclass
class PredictionContext:
    categories: list[CategoryData]
    planet_profiles: dict[str, PlanetProfileData]
    house_profiles: dict[int, HouseProfileData]
    planet_category_weights: list[PlanetCategoryWeightData]
    house_category_weights: list[HouseCategoryWeightData]
    sign_rulerships: dict[str, str]
    aspect_profiles: dict[str, AspectProfileData]
    astro_points: dict[str, AstroPointData]
    point_category_weights: list[PointCategoryWeightData]


@dataclass
class RulesetContext:
    ruleset: RulesetData
    parameters: dict[str, Any]
    event_types: dict[str, EventTypeData]
