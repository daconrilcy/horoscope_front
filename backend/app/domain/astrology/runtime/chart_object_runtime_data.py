# Contrat canonique des objets astrologiques exploitables dans un theme natal.
"""Contrats runtime unifies des objets astrologiques du theme natal."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    PlanetaryMotionDirection,
    PlanetarySpeedState,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
)


class ChartObjectType(StrEnum):
    """Familles canoniques d'objets exploitables dans un theme."""

    PLANET = "planet"
    LUMINARY = "luminary"
    ASTRAL_POINT = "astral_point"
    ANGLE = "angle"
    HOUSE_CUSP = "house_cusp"
    FIXED_STAR = "fixed_star"
    ARABIC_PART = "arabic_part"
    CALCULATED_POINT = "calculated_point"


class ChartObjectSourceType(StrEnum):
    """Sources runtime autorisees pour un objet du theme."""

    EPHEMERIS = "ephemeris"
    HOUSE_SYSTEM = "house_system"
    CATALOG = "catalog"
    DERIVED = "derived"
    USER_OPTION = "user_option"


@dataclass(frozen=True, slots=True)
class ZodiacPositionRuntimeData:
    """Position zodiacale normalisee d'un objet du theme."""

    sign_code: str
    degree_in_sign: float

    def __post_init__(self) -> None:
        """Valide la portion zodiacale minimale portee par l'objet."""
        if not self.sign_code.strip():
            raise ValueError("zodiac position requires a sign code")
        if not 0.0 <= self.degree_in_sign < 30.0:
            raise ValueError("zodiac position degree must be in [0, 30)")


@dataclass(frozen=True, slots=True)
class ChartObjectSourceRuntimeData:
    """Provenance canonique d'un objet runtime du theme."""

    source_type: ChartObjectSourceType
    source_key: str

    def __post_init__(self) -> None:
        """Refuse les objets sans source exploitable."""
        if not self.source_key.strip():
            raise ValueError("chart object source requires a source key")


@dataclass(frozen=True, slots=True)
class ChartObjectCapabilities:
    """Capacites metier selectionnables sans branchement par famille."""

    supports_aspects: bool = False
    supports_dignities: bool = False
    supports_house_position: bool = False
    supports_visibility: bool = False
    supports_motion: bool = False
    supports_interpretation: bool = False
    supports_dominance: bool = False
    supports_fixed_star_conjunction: bool = False


@dataclass(frozen=True, slots=True)
class ChartObjectMotionPayload:
    """Faits de mouvement disponibles pour un corps celeste."""

    speed_longitude: float | None
    is_retrograde: bool | None
    direction: PlanetaryMotionDirection
    is_direct: bool | None
    is_stationary: bool | None
    speed_state: PlanetarySpeedState | None = None
    absolute_speed_longitude: float | None = None
    normalized_speed_ratio: float | None = None
    source: str = "planetary_conditions.motion"

    def __post_init__(self) -> None:
        """Refuse un payload motion qui ne porte aucun fait de mouvement."""
        if (
            self.speed_longitude is None
            and self.is_retrograde is None
            and self.is_stationary is None
            and self.direction is PlanetaryMotionDirection.UNKNOWN
        ):
            raise ValueError("motion payload requires speed or retrograde status")
        if self.direction is PlanetaryMotionDirection.DIRECT and self.is_direct is not True:
            raise ValueError("direct motion payload requires is_direct=True")
        if self.direction is PlanetaryMotionDirection.RETROGRADE and self.is_retrograde is not True:
            raise ValueError("retrograde motion payload requires is_retrograde=True")
        if self.direction is PlanetaryMotionDirection.STATIONARY and self.is_stationary is not True:
            raise ValueError("stationary motion payload requires is_stationary=True")
        if not self.source.strip():
            raise ValueError("motion payload requires a source")


@dataclass(frozen=True, slots=True)
class ChartObjectVisibilityPayload:
    """Faits de visibilite deja calcules et rattaches au runtime."""

    visibility_key: PlanetVisibilityKey
    is_visible: bool | None
    confidence: ConditionConfidence
    reason: str | None
    solar_separation_deg: float | None = None
    solar_proximity_key: SolarProximityConditionKey | None = None
    solar_phase_relation_key: SolarPhaseRelationKey | None = None
    is_cazimi: bool | None = None
    is_combust: bool | None = None
    is_under_beams: bool | None = None
    is_oriental: bool | None = None
    is_occidental: bool | None = None
    source: str = "planetary_conditions"

    def __post_init__(self) -> None:
        """Valide que la visibilite annonce une source et une confiance."""
        if not self.source.strip():
            raise ValueError("visibility payload requires a source")


@dataclass(frozen=True, slots=True)
class ChartObjectDignityPayload:
    """Emplacement reserve aux faits de dignite deja calcules."""

    dignity_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChartObjectPlanetaryConditionsPayload:
    """Emplacement reserve aux conditions planetaires avancees deja calculees."""

    condition_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChartObjectFixedStarPayload:
    """Emplacement reserve aux donnees d'etoile fixe."""

    catalog_code: str


@dataclass(frozen=True, slots=True)
class ChartObjectHousePositionPayload:
    """Faits de position en maison portes par un objet du theme."""

    house_number: int

    def __post_init__(self) -> None:
        """Valide la maison occupee ou associee par l'objet."""
        if not 1 <= self.house_number <= 12:
            raise ValueError("house position payload requires a house number in [1, 12]")


@dataclass(frozen=True, slots=True)
class ChartObjectHouseCuspPayload:
    """Faits propres a une cuspide de maison."""

    house_number: int
    cusp_longitude: float
    cusp_sign: str | None
    house_kind: str | None

    def __post_init__(self) -> None:
        """Valide le numero de maison projete dans le payload."""
        if not 1 <= self.house_number <= 12:
            raise ValueError("house cusp payload requires a house number in [1, 12]")


@dataclass(frozen=True, slots=True)
class ChartObjectAnglePayload:
    """Faits propres a un angle structurel du theme."""

    angle_code: str
    associated_house: int

    def __post_init__(self) -> None:
        """Valide le lien entre angle et maison associee."""
        if not self.angle_code.strip():
            raise ValueError("angle payload requires an angle code")
        if not 1 <= self.associated_house <= 12:
            raise ValueError("angle payload requires a house number in [1, 12]")


@dataclass(frozen=True, slots=True)
class ChartObjectPayloads:
    """Payloads types qui prouvent les donnees annoncees par les capacites."""

    motion: ChartObjectMotionPayload | None = None
    visibility: ChartObjectVisibilityPayload | None = None
    dignity: ChartObjectDignityPayload | None = None
    planetary_conditions: ChartObjectPlanetaryConditionsPayload | None = None
    fixed_star: ChartObjectFixedStarPayload | None = None
    house_position: ChartObjectHousePositionPayload | None = None
    house_cusp: ChartObjectHouseCuspPayload | None = None
    angle: ChartObjectAnglePayload | None = None


@dataclass(frozen=True, slots=True)
class ChartObjectRuntimeData:
    """Objet astrologique unifie selectionnable par capacites."""

    code: str
    object_type: ChartObjectType
    display_name: str
    longitude: float | None
    latitude: float | None
    zodiac_position: ZodiacPositionRuntimeData | None
    source: ChartObjectSourceRuntimeData
    capabilities: ChartObjectCapabilities
    classifications: tuple[str, ...]
    payloads: ChartObjectPayloads

    def __post_init__(self) -> None:
        """Garantit la coherence entre les capacites declarees et les payloads."""
        if not self.code.strip():
            raise ValueError("chart object requires a code")
        if not self.display_name.strip():
            raise ValueError("chart object requires a display name")
        _validate_required_payloads(self.capabilities, self.payloads)


def _validate_required_payloads(
    capabilities: ChartObjectCapabilities,
    payloads: ChartObjectPayloads,
) -> None:
    """Leve une erreur explicite quand capacites et payloads divergent."""
    required_payloads = (
        (capabilities.supports_motion, payloads.motion, "motion"),
        (capabilities.supports_visibility, payloads.visibility, "visibility"),
        (capabilities.supports_dignities, payloads.dignity, "dignity"),
        (capabilities.supports_house_position, payloads.house_position, "house_position"),
        (capabilities.supports_fixed_star_conjunction, payloads.fixed_star, "fixed_star"),
    )
    for is_required, payload, payload_name in required_payloads:
        if is_required and payload is None:
            raise ValueError(f"chart object capability requires {payload_name} payload")
        if not is_required and payload is not None:
            raise ValueError(f"chart object payload requires {payload_name} capability")
