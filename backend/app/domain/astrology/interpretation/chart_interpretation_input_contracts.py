# Contrats internes pour l'entree unifiee de l'interpretation natale.
"""Structures immuables consommees par les flux interpretatifs internes."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    PlanetaryMotionDirection,
    PlanetarySpeedState,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectSourceType,
    ChartObjectType,
)


@dataclass(frozen=True, slots=True)
class ZodiacInterpretationRuntimeData:
    """Position zodiacale minimale projetee pour l'interpretation."""

    sign_code: str
    degree_in_sign: float


@dataclass(frozen=True, slots=True)
class MotionInterpretationRuntimeData:
    """Faits de mouvement deja calcules et rattaches a un objet."""

    speed_longitude: float | None
    is_retrograde: bool | None
    direction: PlanetaryMotionDirection
    is_direct: bool | None
    is_stationary: bool | None
    speed_state: PlanetarySpeedState | None
    absolute_speed_longitude: float | None
    normalized_speed_ratio: float | None
    source: str


@dataclass(frozen=True, slots=True)
class VisibilityInterpretationRuntimeData:
    """Faits de visibilite deja calcules et rattaches a un objet."""

    visibility_key: PlanetVisibilityKey
    is_visible: bool | None
    confidence: ConditionConfidence
    reason: str | None
    solar_separation_deg: float | None
    solar_proximity_key: SolarProximityConditionKey | None
    solar_phase_relation_key: SolarPhaseRelationKey | None
    is_cazimi: bool | None
    is_combust: bool | None
    is_under_beams: bool | None
    is_oriental: bool | None
    is_occidental: bool | None
    source: str


@dataclass(frozen=True, slots=True)
class DignityBreakdownInterpretationRuntimeData:
    """Detail factuel d'un score de dignite deja produit."""

    dignity_type_code: str
    score_value: float
    source: str


@dataclass(frozen=True, slots=True)
class DignityInterpretationRuntimeData:
    """Projection d'un payload de dignite sans recalcul."""

    code: str
    essential_score: float
    accidental_score: float
    total_score: float
    source: str
    functional_strength_score: float | None
    expression_quality_score: float | None
    intensity_score: float | None
    essential_breakdown: tuple[DignityBreakdownInterpretationRuntimeData, ...] = ()
    accidental_breakdown: tuple[DignityBreakdownInterpretationRuntimeData, ...] = ()
    condition_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DominanceBreakdownInterpretationRuntimeData:
    """Detail factuel d'une contribution de dominance deja produite."""

    factor_code: str
    raw_value: float
    normalized_value: float
    weight: float
    weighted_score: float


@dataclass(frozen=True, slots=True)
class DominanceInterpretationRuntimeData:
    """Projection d'une dominance objet ou chart-level deja calculee."""

    code: str
    score: float
    source: str
    rank: int | None = None
    dominance_level: str | None = None
    factors: tuple[str, ...] = ()
    breakdown: tuple[DominanceBreakdownInterpretationRuntimeData, ...] = ()


@dataclass(frozen=True, slots=True)
class HousePositionInterpretationRuntimeData:
    """Position en maison deja resolue pour un objet interpretable."""

    code: str
    house_number: int
    house_modality: str
    source: str
    house_cusp_code: str | None = None
    house_cusp_longitude: float | None = None


@dataclass(frozen=True, slots=True)
class RulershipInterpretationRuntimeData:
    """Maitrises deja resolues et rattachees a un objet interpretable."""

    code: str
    rules_houses: tuple[int, ...]
    is_house_ruler: bool
    is_ascendant_ruler: bool
    is_midheaven_ruler: bool
    source: str
    dispositor_code: str | None
    rules_signs: tuple[str, ...] = ()
    rulership_sources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FixedStarContactInterpretationRuntimeData:
    """Contact etoile fixe deja calcule pour un objet cible."""

    fixed_star_code: str
    fixed_star_display_name: str
    target_code: str
    target_display_name: str
    fixed_star_longitude_deg: float
    target_longitude_deg: float
    orb_deg: float
    max_orb_deg: float
    rule_code: str
    source: str


@dataclass(frozen=True, slots=True)
class AspectInterpretationRuntimeData:
    """Aspect natal projete depuis son runtime calcule."""

    code: str
    participant_codes: tuple[str, str]
    family: str
    angle: float
    orb: float
    orb_max: float
    strength_level: str
    is_major: bool
    source: str


@dataclass(frozen=True, slots=True)
class AdvancedConditionInterpretationRuntimeData:
    """Condition avancee factuelle projetee pour les regles interpretatives."""

    condition_code: str
    condition_type_code: str
    source_planet_code: str
    target_planet_code: str | None
    score_profile: str
    reference_version: str
    score_impact: float
    ranking_weight: float


@dataclass(frozen=True, slots=True)
class ChartObjectInterpretationRuntimeData:
    """Objet du theme pret pour une consommation interpretative interne."""

    code: str
    display_name: str
    object_type: ChartObjectType
    classifications: tuple[str, ...]
    source_type: ChartObjectSourceType
    source_key: str
    longitude: float | None
    latitude: float | None
    zodiac_position: ZodiacInterpretationRuntimeData
    house_number: int | None
    house_modality: str | None
    dignity: DignityInterpretationRuntimeData | None
    motion: MotionInterpretationRuntimeData | None
    visibility: VisibilityInterpretationRuntimeData | None
    dominance: DominanceInterpretationRuntimeData | None
    rulership: RulershipInterpretationRuntimeData | None
    fixed_star_contacts: tuple[FixedStarContactInterpretationRuntimeData, ...] = ()
    source_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ChartInterpretationMetadataRuntimeData:
    """Metadonnees techniques de l'input interpretatif."""

    source_codes: tuple[str, ...]
    object_count: int
    aspect_count: int


@dataclass(frozen=True, slots=True)
class SignProfileBalancesInterpretationRuntimeData:
    """Profils structurels de signes deja agreges au niveau du theme."""

    elements: tuple[DominanceInterpretationRuntimeData, ...]
    modalities: tuple[DominanceInterpretationRuntimeData, ...]
    polarities: tuple[DominanceInterpretationRuntimeData, ...]
    seasonal_quadrants: tuple[DominanceInterpretationRuntimeData, ...]
    fertility: tuple[DominanceInterpretationRuntimeData, ...]
    voices: tuple[DominanceInterpretationRuntimeData, ...]
    forms: tuple[DominanceInterpretationRuntimeData, ...]


@dataclass(frozen=True, slots=True)
class ChartInterpretationInputRuntimeData:
    """Entree unique construite depuis les objets runtime du theme natal."""

    chart_id: str | None
    chart_type: str
    locale: str | None
    objects: tuple[ChartObjectInterpretationRuntimeData, ...]
    aspects: tuple[AspectInterpretationRuntimeData, ...]
    dignities: tuple[DignityInterpretationRuntimeData, ...]
    house_positions: tuple[HousePositionInterpretationRuntimeData, ...]
    rulerships: tuple[RulershipInterpretationRuntimeData, ...]
    dominance: tuple[DominanceInterpretationRuntimeData, ...]
    fixed_star_contacts: tuple[FixedStarContactInterpretationRuntimeData, ...]
    sign_profile_balances: SignProfileBalancesInterpretationRuntimeData | None = None
    advanced_condition_facts: tuple[AdvancedConditionInterpretationRuntimeData, ...] = ()
    metadata: ChartInterpretationMetadataRuntimeData = field(
        default_factory=lambda: ChartInterpretationMetadataRuntimeData(
            source_codes=(),
            object_count=0,
            aspect_count=0,
        )
    )
