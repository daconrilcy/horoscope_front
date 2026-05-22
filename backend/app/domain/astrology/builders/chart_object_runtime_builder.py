# Projection pure des collections natales historiques en objets runtime unifies.
"""Builder des objets runtime unifies du theme natal."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

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
    ZodiacPositionRuntimeData,
)


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


_LUMINARY_CODES = frozenset({"sun", "moon"})
_ANGLE_HOUSES = (
    ("asc", "Ascendant", 1),
    ("dsc", "Descendant", 7),
    ("mc", "Midheaven", 10),
    ("ic", "Imum Coeli", 4),
)


def build_chart_object_runtime_data(
    *,
    planet_positions: Sequence[PlanetChartObjectSource],
    astral_points: Sequence[AstralPointChartObjectSource],
    houses: Sequence[HouseChartObjectSource],
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les collections natales historiques en objets runtime unifies."""
    ordered_houses = tuple(sorted(houses, key=lambda item: item.number))
    return (
        *_build_planet_objects(planet_positions),
        *_build_astral_point_objects(astral_points),
        *_build_angle_objects(ordered_houses),
        *_build_house_cusp_objects(ordered_houses),
    )


def _build_planet_objects(
    planet_positions: Sequence[PlanetChartObjectSource],
) -> tuple[ChartObjectRuntimeData, ...]:
    """Projette les planetes et luminaires depuis leurs positions existantes."""
    objects: list[ChartObjectRuntimeData] = []
    for position in planet_positions:
        planet_code = _normalize_code(position.planet_code)
        is_luminary = planet_code in _LUMINARY_CODES
        motion_payload = _build_motion_payload(position)
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
                    supports_house_position=True,
                    supports_motion=motion_payload is not None,
                    supports_interpretation=True,
                    supports_dominance=True,
                ),
                classifications=("luminary",) if is_luminary else ("planet",),
                payloads=ChartObjectPayloads(
                    house_position=ChartObjectHousePositionPayload(
                        house_number=position.house_number,
                    ),
                    motion=motion_payload,
                ),
            )
        )
    return tuple(objects)


def _build_motion_payload(
    position: PlanetChartObjectSource,
) -> ChartObjectMotionPayload | None:
    """Retourne les faits de mouvement seulement quand ils existent."""
    if position.speed_longitude is None and position.is_retrograde is None:
        return None
    return ChartObjectMotionPayload(
        speed_longitude=position.speed_longitude,
        is_retrograde=position.is_retrograde,
    )


def _build_astral_point_objects(
    astral_points: Sequence[AstralPointChartObjectSource],
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
                    supports_aspects=True,
                    supports_house_position=point.house is not None,
                    supports_interpretation=True,
                ),
                classifications=_astral_point_classifications(point),
                payloads=ChartObjectPayloads(
                    house_position=(
                        ChartObjectHousePositionPayload(house_number=point.house)
                        if point.house is not None
                        else None
                    ),
                ),
            )
        )
    return tuple(objects)


def _build_angle_objects(
    houses: Sequence[HouseChartObjectSource],
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
                    supports_aspects=True,
                    supports_house_position=True,
                    supports_interpretation=True,
                    supports_dominance=True,
                ),
                classifications=("angle",),
                payloads=ChartObjectPayloads(
                    angle=ChartObjectAnglePayload(
                        angle_code=angle_code,
                        associated_house=house_number,
                    ),
                    house_position=ChartObjectHousePositionPayload(
                        house_number=house_number,
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
                house_position=ChartObjectHousePositionPayload(
                    house_number=house.number,
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
