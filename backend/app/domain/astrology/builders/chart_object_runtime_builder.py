# Projection pure des collections natales historiques en objets runtime unifies.
"""Builder des objets runtime unifies du theme natal."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from app.domain.astrology.planetary_conditions.contracts import (
    AdvancedPlanetaryConditionsResult,
    PlanetaryConditionsBundle,
    PlanetaryMotionCondition,
    PlanetaryMotionDirection,
    SolarPhaseRelationKey,
    SolarProximityConditionKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectAnglePayload,
    ChartObjectCapabilities,
    ChartObjectHouseCuspPayload,
    ChartObjectHousePositionPayload,
    ChartObjectMotionPayload,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    ChartObjectVisibilityPayload,
    FixedStarRuntimePayload,
    ZodiacPositionRuntimeData,
)
from app.domain.astrology.runtime.house_runtime_data import resolve_house_kind


class PlanetChartObjectSource(Protocol):
    """Contrat minimal d'une position planetaire deja calculee."""

    planet_code: str
    longitude: float
    sign_code: str
    house_number: int
    speed_longitude: float | None
    is_retrograde: bool | None


class AstralPointChartObjectSource(Protocol):
    """Contrat minimal d'un point astral natal deja calcule."""

    code: str
    variant_code: str | None
    longitude: float
    sign: str
    degree_in_sign: float
    house: int | None
    calculation_source: str
    is_physical_body: bool


class HouseChartObjectSource(Protocol):
    """Contrat minimal d'une maison runtime deja enrichie."""

    number: int
    cusp_longitude: float
    cusp_sign: str | None
    house_kind: str | None


class FixedStarChartObjectSource(Protocol):
    """Contrat minimal d'une etoile fixe documentaire runtime."""

    code: str
    display_name: str
    longitude: float
    reference_system: str
    source_code: str
    constellation_code: str | None
    magnitude: float | None
    reference_epoch: str | None
    categories: tuple[str, ...]


_LUMINARY_CODES = frozenset({"sun", "moon"})
_ANGLE_HOUSES = (
    ("asc", "Ascendant", 1),
    ("dsc", "Descendant", 7),
    ("mc", "Midheaven", 10),
    ("ic", "Imum Coeli", 4),
)


def build_house_position_payload(
    *,
    house_number: int,
    house_cusp_longitude: float | None = None,
) -> ChartObjectHousePositionPayload:
    """Construit le payload house position depuis le helper canonique."""
    return ChartObjectHousePositionPayload(
        house_number=house_number,
        house_modality=resolve_house_kind(house_number),
        house_cusp_code=f"house_{house_number}_cusp",
        house_cusp_longitude=house_cusp_longitude,
        source="houses.runtime",
    )


def build_chart_object_runtime_data(
    *,
    planet_positions: Sequence[PlanetChartObjectSource],
    astral_points: Sequence[AstralPointChartObjectSource],
    houses: Sequence[HouseChartObjectSource],
    fixed_stars: Sequence[FixedStarChartObjectSource] = (),
    advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None = None,
    include_astral_points_in_aspects: bool = True,
    include_angles_in_aspects: bool = True,
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les collections natales historiques en objets runtime unifies."""
    ordered_houses = tuple(sorted(houses, key=lambda item: item.number))
    return (
        *_build_planet_objects(
            planet_positions,
            advanced_planetary_conditions=advanced_planetary_conditions,
        ),
        *_build_astral_point_objects(
            astral_points,
            include_astral_points_in_aspects=include_astral_points_in_aspects,
        ),
        *_build_angle_objects(
            ordered_houses,
            include_angles_in_aspects=include_angles_in_aspects,
        ),
        *_build_house_cusp_objects(ordered_houses),
        *_build_fixed_star_objects(fixed_stars),
    )


def _build_planet_objects(
    planet_positions: Sequence[PlanetChartObjectSource],
    *,
    advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None,
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les planetes et luminaires depuis leurs positions existantes."""
    objects: list[ChartObjectRuntimeData] = []
    for position in planet_positions:
        planet_code = _normalize_code(position.planet_code)
        is_luminary = planet_code in _LUMINARY_CODES
        condition_bundle = _condition_bundle_for(
            advanced_planetary_conditions,
            planet_code=planet_code,
        )
        motion_payload = _build_motion_payload(position, condition_bundle)
        visibility_payload = _build_visibility_payload(condition_bundle)
        objects.append(
            ChartObjectRuntimeData(
                code=planet_code,
                object_type=ChartObjectType.LUMINARY if is_luminary else ChartObjectType.PLANET,
                display_name=_display_name(planet_code),
                longitude=position.longitude,
                latitude=None,
                zodiac_position=ZodiacPositionRuntimeData(
                    sign_code=position.sign_code,
                    degree_in_sign=position.longitude % 30.0,
                ),
                source=ChartObjectSourceRuntimeData(
                    source_type=ChartObjectSourceType.EPHEMERIS,
                    source_key=planet_code,
                ),
                capabilities=ChartObjectCapabilities(
                    supports_aspects=True,
                    supports_dignities=True,
                    supports_house_position=True,
                    supports_fixed_star_conjunction=True,
                    supports_motion=motion_payload is not None,
                    supports_visibility=visibility_payload is not None,
                    supports_interpretation=True,
                    supports_dominance=True,
                    supports_rulership=True,
                ),
                classifications=("luminary",) if is_luminary else ("planet",),
                payloads=ChartObjectPayloads(
                    house_position=build_house_position_payload(
                        house_number=position.house_number,
                    ),
                    motion=motion_payload,
                    visibility=visibility_payload,
                ),
            )
        )
    return tuple(objects)


def _build_motion_payload(
    position: PlanetChartObjectSource,
    condition_bundle: PlanetaryConditionsBundle | None,
) -> ChartObjectMotionPayload | None:
    """Retourne les faits de mouvement seulement quand ils existent."""
    del position
    if condition_bundle is not None and condition_bundle.motion is not None:
        return _build_motion_payload_from_condition(condition_bundle.motion)
    return None


def _build_motion_payload_from_condition(
    condition: PlanetaryMotionCondition,
) -> ChartObjectMotionPayload:
    """Mappe le contrat motion canonique sans reclassifier la vitesse."""
    return ChartObjectMotionPayload(
        speed_longitude=condition.speed_deg_per_day,
        is_retrograde=condition.is_retrograde,
        direction=condition.direction,
        is_direct=condition.direction is PlanetaryMotionDirection.DIRECT,
        is_stationary=condition.is_stationary,
        speed_state=condition.speed_state,
        absolute_speed_longitude=condition.absolute_speed_deg_per_day,
        normalized_speed_ratio=condition.normalized_speed_ratio,
        source="planetary_conditions.motion",
    )


def _build_visibility_payload(
    condition_bundle: PlanetaryConditionsBundle | None,
) -> ChartObjectVisibilityPayload | None:
    """Mappe les faits solaires deja calcules vers le payload runtime."""
    if condition_bundle is None or condition_bundle.visibility is None:
        return None

    visibility = condition_bundle.visibility
    solar_proximity = condition_bundle.solar_proximity
    solar_phase_relation = condition_bundle.solar_phase_relation
    if solar_proximity is None or solar_phase_relation is None:
        return ChartObjectVisibilityPayload(
            visibility_key=visibility.visibility_key,
            is_visible=visibility.is_visible,
            confidence=visibility.confidence,
            reason=visibility.reason,
        )

    solar_proximity_key: SolarProximityConditionKey | None = solar_proximity.condition_key
    solar_phase_relation_key: SolarPhaseRelationKey | None = solar_phase_relation.relation_key
    solar_separation_deg: float | None = solar_proximity.sun_distance_deg
    is_cazimi: bool | None = solar_proximity.condition_key is SolarProximityConditionKey.CAZIMI
    is_combust: bool | None = solar_proximity.condition_key is SolarProximityConditionKey.COMBUST
    is_under_beams: bool | None = (
        solar_proximity.condition_key is SolarProximityConditionKey.UNDER_BEAMS
    )
    is_oriental = solar_phase_relation.is_oriental
    is_occidental = solar_phase_relation.is_occidental
    if condition_bundle.planet_key == "sun":
        solar_proximity_key = None
        solar_phase_relation_key = None
        solar_separation_deg = None
        is_cazimi = None
        is_combust = None
        is_under_beams = None
        is_oriental = None
        is_occidental = None

    return ChartObjectVisibilityPayload(
        visibility_key=visibility.visibility_key,
        is_visible=visibility.is_visible,
        confidence=visibility.confidence,
        reason=visibility.reason,
        solar_separation_deg=solar_separation_deg,
        solar_proximity_key=solar_proximity_key,
        solar_phase_relation_key=solar_phase_relation_key,
        is_cazimi=is_cazimi,
        is_combust=is_combust,
        is_under_beams=is_under_beams,
        is_oriental=is_oriental,
        is_occidental=is_occidental,
    )


def _condition_bundle_for(
    advanced_planetary_conditions: AdvancedPlanetaryConditionsResult | None,
    *,
    planet_code: str,
) -> PlanetaryConditionsBundle | None:
    """Retourne le bundle avance deja calcule pour une planete."""
    if advanced_planetary_conditions is None:
        return None
    return advanced_planetary_conditions.conditions_by_planet.get(planet_code)


def _build_astral_point_objects(
    astral_points: Sequence[AstralPointChartObjectSource],
    *,
    include_astral_points_in_aspects: bool,
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les points astraux calcules sans recalcul astronomique."""
    objects: list[ChartObjectRuntimeData] = []
    for point in astral_points:
        code = _normalize_code(point.code)
        source_type = (
            ChartObjectSourceType.DERIVED
            if point.calculation_source.startswith("derived:")
            else ChartObjectSourceType.EPHEMERIS
        )
        objects.append(
            ChartObjectRuntimeData(
                code=code,
                object_type=ChartObjectType.ASTRAL_POINT,
                display_name=_display_name(code),
                longitude=point.longitude,
                latitude=None,
                zodiac_position=ZodiacPositionRuntimeData(
                    sign_code=point.sign,
                    degree_in_sign=point.degree_in_sign,
                ),
                source=ChartObjectSourceRuntimeData(
                    source_type=source_type,
                    source_key=point.calculation_source,
                ),
                capabilities=ChartObjectCapabilities(
                    supports_aspects=include_astral_points_in_aspects,
                    supports_house_position=point.house is not None,
                    supports_interpretation=True,
                ),
                classifications=_astral_point_classifications(point),
                payloads=ChartObjectPayloads(
                    house_position=(
                        build_house_position_payload(house_number=point.house)
                        if point.house is not None
                        else None
                    ),
                ),
            )
        )
    return tuple(objects)


def _build_angle_objects(
    houses: Sequence[HouseChartObjectSource],
    *,
    include_angles_in_aspects: bool,
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les angles structurels depuis les cuspides de maisons."""
    houses_by_number = {house.number: house for house in houses}
    objects: list[ChartObjectRuntimeData] = []
    for angle_code, display_name, house_number in _ANGLE_HOUSES:
        house = houses_by_number.get(house_number)
        if house is None:
            continue
        objects.append(
            ChartObjectRuntimeData(
                code=angle_code,
                object_type=ChartObjectType.ANGLE,
                display_name=display_name,
                longitude=house.cusp_longitude,
                latitude=None,
                zodiac_position=_house_zodiac_position(house),
                source=ChartObjectSourceRuntimeData(
                    source_type=ChartObjectSourceType.HOUSE_SYSTEM,
                    source_key=f"house:{house_number}",
                ),
                capabilities=ChartObjectCapabilities(
                    supports_aspects=include_angles_in_aspects,
                    supports_house_position=True,
                    supports_interpretation=True,
                ),
                classifications=("angle",),
                payloads=ChartObjectPayloads(
                    angle=ChartObjectAnglePayload(
                        angle_code=angle_code,
                        associated_house=house_number,
                    ),
                    house_position=build_house_position_payload(
                        house_number=house_number,
                        house_cusp_longitude=house.cusp_longitude,
                    ),
                ),
            )
        )
    return tuple(objects)


def _build_house_cusp_objects(
    houses: Sequence[HouseChartObjectSource],
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette chaque maison par sa cuspide runtime."""
    return tuple(
        ChartObjectRuntimeData(
            code=f"house_{house.number}_cusp",
            object_type=ChartObjectType.HOUSE_CUSP,
            display_name=f"House {house.number} cusp",
            longitude=house.cusp_longitude,
            latitude=None,
            zodiac_position=_house_zodiac_position(house),
            source=ChartObjectSourceRuntimeData(
                source_type=ChartObjectSourceType.HOUSE_SYSTEM,
                source_key=f"house:{house.number}",
            ),
            capabilities=ChartObjectCapabilities(supports_house_position=True),
            classifications=("house_cusp",),
            payloads=ChartObjectPayloads(
                house_position=build_house_position_payload(
                    house_number=house.number,
                    house_cusp_longitude=house.cusp_longitude,
                ),
                house_cusp=ChartObjectHouseCuspPayload(
                    house_number=house.number,
                    cusp_longitude=house.cusp_longitude,
                    cusp_sign=house.cusp_sign,
                    house_kind=house.house_kind,
                ),
            ),
        )
        for house in houses
    )


def _build_fixed_star_objects(
    fixed_stars: Sequence[FixedStarChartObjectSource],
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les etoiles fixes documentaires en objets runtime."""
    objects: list[ChartObjectRuntimeData] = []
    seen_codes: set[str] = set()
    for star in sorted(fixed_stars, key=lambda item: item.code.strip().lower()):
        code = _normalize_code(star.code)
        if code in seen_codes:
            raise ValueError(f"duplicate fixed star chart object code: {code}")
        seen_codes.add(code)
        objects.append(
            ChartObjectRuntimeData(
                code=code,
                object_type=ChartObjectType.FIXED_STAR,
                display_name=star.display_name,
                longitude=star.longitude,
                latitude=None,
                zodiac_position=None,
                source=ChartObjectSourceRuntimeData(
                    source_type=ChartObjectSourceType.CATALOG,
                    source_key=star.source_code,
                ),
                capabilities=ChartObjectCapabilities(),
                classifications=("fixed_star",),
                payloads=ChartObjectPayloads(
                    fixed_star=FixedStarRuntimePayload(
                        catalog_code=code,
                        display_name=star.display_name,
                        reference_system=star.reference_system,
                        source_code=star.source_code,
                        constellation_code=star.constellation_code,
                        magnitude=star.magnitude,
                        reference_epoch=star.reference_epoch,
                        categories=tuple(star.categories),
                    ),
                ),
            )
        )
    return tuple(objects)


def _house_zodiac_position(house: HouseChartObjectSource) -> ZodiacPositionRuntimeData | None:
    """Construit la position zodiacale d'une cuspide si son signe est disponible."""
    if house.cusp_sign is None:
        return None
    return ZodiacPositionRuntimeData(
        sign_code=house.cusp_sign,
        degree_in_sign=house.cusp_longitude % 30.0,
    )


def _astral_point_classifications(
    point: AstralPointChartObjectSource,
) -> tuple[str, ...]:
    """Expose les classes minimales d'un point astral sans nouveau referentiel."""
    classifications = ["astral_point"]
    if point.variant_code is not None:
        classifications.append(f"variant:{point.variant_code}")
    if point.is_physical_body:
        classifications.append("physical_body")
    return tuple(classifications)


def _normalize_code(code: str) -> str:
    """Normalise les codes runtime sans accepter de valeur vide."""
    normalized = code.strip().lower()
    if not normalized:
        raise ValueError("chart object code cannot be empty")
    return normalized


def _display_name(code: str) -> str:
    """Produit un libelle technique stable pour les objets internes."""
    return code.replace("_", " ").title()
