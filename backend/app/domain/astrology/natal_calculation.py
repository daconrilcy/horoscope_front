"""Calcul du thème natal et structuration des résultats astrologiques."""

from __future__ import annotations

from collections.abc import Callable
from math import isfinite

from pydantic import AliasChoices, BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

from app.core.config import AspectSchoolType, FrameType, HouseSystemType, ZodiacType
from app.domain.astrology.advanced_conditions import (
    AdvancedPlanetaryCondition,
    TraditionalConditionsResult,
)
from app.domain.astrology.astral_point_calculation_resolver import (
    AstralPointCalculationInstruction,
    AstralPointCalculationResolver,
)
from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data
from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.calculators import (
    calculate_houses,
    calculate_major_aspects,
    calculate_planet_positions,
)
from app.domain.astrology.calculators.houses import HOUSE_SYSTEM_CODE, assign_house_number
from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignalSet,
)
from app.domain.astrology.dignities.contracts import (
    ChartSectResult,
    PlanetDignityResult,
)
from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.house_ruler_resolver import (
    HouseRulerResult,
)
from app.domain.astrology.interpretation.advanced_conditions import (
    AdvancedConditionInterpretationProfile,
)
from app.domain.astrology.interpretation_adapters import (
    InterpretationAdapterResult,
)
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData, prepare_birth_data
from app.domain.astrology.planetary_conditions import (
    AdvancedPlanetaryConditionsResult,
)
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectInterpretiveHintsRuntimeData,
    AspectRuntimeData,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
)
from app.domain.astrology.runtime.chart_signature_runtime_data import ChartBalanceRuntimeData
from app.domain.astrology.runtime.house_runtime_data import HouseAxisRuntimeData, HouseRuntimeData
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    AstrologySystemReferenceSet,
)
from app.domain.astrology.runtime.sign_runtime_data import SignRuntimeData
from app.domain.astrology.zodiac import normalize_360, sign_from_longitude

__all__ = (
    "build_chart_object_runtime_data",
    "calculate_houses",
    "calculate_major_aspects",
    "calculate_planet_positions",
)


class PlanetPosition(BaseModel):
    planet_code: str
    longitude: float
    sign_code: str
    house_number: int
    speed_longitude: float | None = None
    is_retrograde: bool | None = None


class NatalAstralPointPosition(BaseModel):
    """Position normalisée d'un point astral calculé depuis le runtime DB."""

    code: str
    variant_code: str | None = None
    longitude: float
    sign: str
    degree_in_sign: float
    house: int | None = None
    calculation_source: str
    is_physical_body: bool


HouseResult = HouseRuntimeData


class AspectResult(BaseModel):
    aspect_code: str
    planet_a: str
    planet_b: str
    angle: float
    orb: float
    orb_used: float
    orb_max: float
    family: str
    is_major: bool
    is_minor: bool
    aspect_interpretive_hints: AspectInterpretiveHintsRuntimeData | None = Field(
        default=None,
        exclude=True,
    )
    aspect_runtime: AspectRuntimeData | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def _fill_orb_fields(self) -> AspectResult:
        if self.aspect_runtime is None:
            self.aspect_runtime = build_aspect_runtime_data(self)
        return self


class NatalResult(BaseModel):
    reference_version: str
    ruleset_version: str
    house_system: HouseSystemType
    engine: str = "simplified"
    zodiac: ZodiacType = ZodiacType.TROPICAL
    frame: FrameType = FrameType.GEOCENTRIC
    ayanamsa: str | None = None
    altitude_m: float | None = None
    ephemeris_path_version: str | None = None
    ephemeris_path_hash: str | None = None
    # time_scale: "TT" when Terrestrial Time fields are present, "UT" otherwise (story 22.2).
    time_scale: str = "UT"
    # aspect school and versioned rules identifier (story 24-1).
    aspect_school: AspectSchoolType = AspectSchoolType.MODERN
    aspect_rules_version: str = "1.0.0"
    prepared_input: BirthPreparedData
    planet_positions: list[PlanetPosition]
    houses: list[HouseRuntimeData]
    signs_runtime: list[SignRuntimeData] = Field(default_factory=list)
    chart_balance: ChartBalanceRuntimeData | None = None
    house_rulers: list[HouseRulerResult] = Field(default_factory=list)
    astral_points: list[NatalAstralPointPosition] = Field(
        default_factory=list,
        validation_alias=AliasChoices("astral_points", "points"),
    )
    dignity_sect: ChartSectResult | None = None
    dignities: list[PlanetDignityResult] = Field(default_factory=list)
    condition_profiles: list[PlanetConditionProfile] = Field(default_factory=list)
    condition_signals: list[PlanetConditionSignalSet] = Field(default_factory=list)
    advanced_conditions: list[AdvancedPlanetaryCondition] = Field(default_factory=list)
    advanced_planetary_conditions: SkipJsonSchema[AdvancedPlanetaryConditionsResult | None] = Field(
        default=None,
        exclude=True,
    )
    chart_objects: SkipJsonSchema[list[ChartObjectRuntimeData]] = Field(
        default_factory=list,
        exclude=True,
    )
    interpretation_profiles_by_planet: SkipJsonSchema[
        dict[str, tuple[AdvancedConditionInterpretationProfile, ...]]
    ] = Field(default_factory=dict, exclude=True)
    traditional_conditions: TraditionalConditionsResult | None = None
    dominant_planets: DominantPlanetsResult | None = None
    interpretation_adapter: InterpretationAdapterResult | None = None
    aspects: list[AspectResult]

    @property
    def points(self) -> list[NatalAstralPointPosition]:
        """Expose l'ancien accès en lecture sans changer la sortie canonique."""
        return self.astral_points


def _build_aspect_result(
    payload: dict[str, object],
    celestial_catalog: CelestialRuntimeCatalog,
    interpretive_profiles: dict[str, object] | None = None,
) -> AspectResult:
    """Construit un resultat d'aspect avec le catalogue celeste de reference."""
    aspect = AspectResult.model_validate(payload)
    profile = (
        None if interpretive_profiles is None else interpretive_profiles.get(aspect.aspect_code)
    )
    if profile is not None:
        from app.domain.astrology.builders.aspect_runtime_builder import (
            build_aspect_structural_runtime_data,
        )
        from app.domain.astrology.runtime.aspect_runtime_data import AspectInterpretiveHintResolver

        structural = build_aspect_structural_runtime_data(aspect, celestial_catalog)
        aspect.aspect_interpretive_hints = AspectInterpretiveHintResolver().resolve(
            structural,
            profile,
        )
    aspect.aspect_runtime = build_aspect_runtime_data(aspect, celestial_catalog)
    return aspect


class NatalCalculationError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def _raise_invalid_reference(version: str, field: str, reason: str) -> None:
    raise NatalCalculationError(
        code="invalid_reference_data",
        message=f"{field} reference data is invalid",
        details={"reference_version": version, "field": field, "reason": reason},
    )


def _validate_house_cusps(version: str, houses_raw: list[dict[str, object]]) -> None:
    if len(houses_raw) != 12:
        _raise_invalid_reference(version, "houses", "expected_12_cusps")

    longitudes: list[float] = []
    for house in houses_raw:
        value = house.get("cusp_longitude")
        if value is None:
            _raise_invalid_reference(version, "houses", "missing_cusp_longitude")
        try:
            longitude = float(value)
        except (TypeError, ValueError):
            _raise_invalid_reference(version, "houses", "invalid_cusp_longitude")
        if not isfinite(longitude):
            _raise_invalid_reference(version, "houses", "non_finite_cusp_longitude")
        normalized = normalize_360(longitude)
        if normalized != longitude:
            _raise_invalid_reference(version, "houses", "non_normalized_cusp_longitude")
        longitudes.append(normalized)

    if len(set(longitudes)) != len(longitudes):
        _raise_invalid_reference(version, "houses", "duplicate_cusp_longitude")


def _extract_sign_rulerships(runtime_reference: AstrologyRuntimeReference) -> dict[str, str]:
    """Extrait le mapping signe -> maître depuis les dignités de référence."""
    return dict(runtime_reference.dignities.sign_rulerships)


def _extract_house_axes(
    version: str,
    runtime_reference: AstrologyRuntimeReference,
) -> dict[int, HouseAxisRuntimeData]:
    """Valide les axes de maisons charges depuis le referentiel canonique."""
    raw_axes = runtime_reference.house_axes
    if not raw_axes:
        _raise_invalid_reference(version, "house_axes", "missing_or_empty")

    axes: dict[int, HouseAxisRuntimeData] = {}
    for item in raw_axes:
        house_number = _parse_house_axis_number(version, item.house_number)
        opposite_house = _parse_house_axis_number(version, item.opposite_house)
        theme = item.theme
        if (
            house_number < 1
            or house_number > 12
            or opposite_house < 1
            or opposite_house > 12
            or house_number == opposite_house
            or not theme.strip()
        ):
            _raise_invalid_reference(version, "house_axes", "invalid_entry")
        if house_number in axes:
            _raise_invalid_reference(version, "house_axes", "duplicate_house")
        axes[house_number] = HouseAxisRuntimeData(
            opposite_house=opposite_house,
            theme=theme,
        )

    missing_houses = set(range(1, 13)) - set(axes)
    if missing_houses:
        _raise_invalid_reference(version, "house_axes", "missing_house")
    return axes


def _parse_house_axis_number(version: str, value: object) -> int:
    """Extrait un numéro de maison entier sans coercition silencieuse."""
    if isinstance(value, bool) or not isinstance(value, int):
        _raise_invalid_reference(version, "house_axes", "invalid_house_numbers")
    return value


def _build_system_inheritance(
    version: str,
    systems: AstrologySystemReferenceSet,
) -> dict[str, str | None]:
    """Valide la carte d'héritage des systèmes astrologiques."""
    if not systems.items:
        _raise_invalid_reference(version, "astral_systems", "missing_or_empty")
    inheritance: dict[str, str | None] = {}
    for item in systems.items:
        code = item.code
        if not code.strip():
            _raise_invalid_reference(version, "astral_systems", "missing_code")
        parent = item.inherits_from_system_code
        if parent is not None and not parent.strip():
            _raise_invalid_reference(version, "astral_systems", "invalid_parent")
        inheritance[code.strip().lower()] = None if parent is None else parent.strip().lower()
    if not inheritance:
        _raise_invalid_reference(version, "astral_systems", "missing_or_empty")
    return inheritance


def _build_swisseph_positions(
    jdut: float,
    planet_codes: list[str],
    sign_codes: list[str],
    zodiac: ZodiacType = ZodiacType.TROPICAL,
    ayanamsa: str | None = None,
    frame: FrameType = FrameType.GEOCENTRIC,
    lat: float | None = None,
    lon: float | None = None,
    altitude_m: float | None = None,
) -> list[dict[str, object]]:
    """Build positions_raw list from SwissEph ephemeris provider."""
    from app.domain.astrology.ephemeris_provider import calculate_planets

    ephem_result = calculate_planets(
        jdut,
        lat=lat,
        lon=lon,
        zodiac=zodiac,
        ayanamsa=ayanamsa,
        frame=frame,
        altitude_m=altitude_m,
    )
    planet_data_by_id = {pd.planet_id: pd for pd in ephem_result.planets}

    positions_raw: list[dict[str, object]] = []
    for code in planet_codes:
        pd = planet_data_by_id.get(code)
        if pd is None:
            continue
        longitude = pd.longitude  # already normalized [0, 360) by ephemeris_provider
        positions_raw.append(
            {
                "planet_code": code,
                "longitude": longitude,
                "sign_code": sign_from_longitude(longitude, sign_codes),
                "speed_longitude": pd.speed_longitude,
                "is_retrograde": pd.is_retrograde,
            }
        )
    return positions_raw


def _build_swisseph_houses(
    jdut: float,
    lat: float,
    lon: float,
    house_numbers: list[int],
    house_system: HouseSystemType = HouseSystemType.PLACIDUS,
    frame: FrameType = FrameType.GEOCENTRIC,
    altitude_m: float | None = None,
) -> tuple[list[dict[str, object]], str]:
    """Build houses_raw list from SwissEph houses provider.

    Returns:
        Tuple of (houses_raw, house_system_name).
    """
    from app.domain.astrology.houses_provider import calculate_houses as calc_sw_houses

    house_data = calc_sw_houses(
        jdut,
        lat,
        lon,
        house_system=house_system,
        frame=frame,
        altitude_m=altitude_m,
    )
    houses_raw: list[dict[str, object]] = [
        {"number": number, "cusp_longitude": house_data.cusps[number - 1]}
        for number in house_numbers
        if 1 <= number <= 12
    ]
    return houses_raw, house_data.house_system


def _simplified_point_longitude(
    julian_day: float, instruction: AstralPointCalculationInstruction
) -> float:
    """Produit une longitude déterministe pour les points en moteur simplifié."""
    seed = sum(ord(char) for char in instruction.engine_key or instruction.calculation_mode)
    return normalize_360((julian_day * 0.985647) + seed)


def _engine_point_longitude(
    julian_day: float,
    engine: str,
    instruction: AstralPointCalculationInstruction,
    *,
    zodiac: ZodiacType,
    ayanamsa: str | None,
    frame: FrameType,
    lat: float | None,
    lon: float | None,
    altitude_m: float | None,
) -> float:
    """Calcule une longitude directe selon le moteur natal actif."""
    if instruction.engine_key is None:
        raise NatalCalculationError(
            code="invalid_reference_data",
            message="astral point reference data is invalid",
            details={"field": "astral_points", "reason": "missing_engine_key"},
        )
    if engine == "swisseph":
        from app.domain.astrology.ephemeris_provider import calculate_astral_point_longitude

        return calculate_astral_point_longitude(
            julian_day,
            instruction.engine_key,
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            lat=lat,
            lon=lon,
            altitude_m=altitude_m,
        ).longitude
    return _simplified_point_longitude(julian_day, instruction)


def _calculation_source(engine: str, instruction: AstralPointCalculationInstruction) -> str:
    """Décrit la source technique d'une longitude calculée directement."""
    if engine == "swisseph" and instruction.engine_key is not None:
        return f"swiss_ephemeris:{instruction.engine_key}"
    engine_key = instruction.engine_key or instruction.calculation_mode
    return f"{engine}:{engine_key}"


def opposite_longitude(longitude: float) -> float:
    """Retourne la longitude opposée normalisée sur le zodiaque."""
    return normalize_360(longitude + 180.0)


def calculate_astral_points(
    *,
    julian_day: float,
    runtime_reference: AstrologyRuntimeReference,
    sign_codes: list[str],
    houses_raw: list[dict[str, object]],
    engine: str,
    zodiac: ZodiacType = ZodiacType.TROPICAL,
    ayanamsa: str | None = None,
    frame: FrameType = FrameType.GEOCENTRIC,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    altitude_m: float | None = None,
) -> list[dict[str, object]]:
    """Calcule les points astraux configurés et les normalise pour le résultat natal."""
    resolver = AstralPointCalculationResolver()
    points_by_key: dict[tuple[str, str], dict[str, object]] = {}
    pending = list(runtime_reference.astral_points.items)
    while pending:
        progressed = False
        for point in tuple(pending):
            instruction = resolver.resolve(point)
            key = (instruction.point_code, instruction.variant_code)
            if instruction.is_derived:
                source_key = (
                    str(instruction.derived_from_point_code),
                    str(instruction.derived_from_variant_code),
                )
                source = points_by_key.get(source_key)
                if source is None:
                    continue
                longitude = opposite_longitude(float(source["longitude"]))
                calculation_source = (
                    "derived:"
                    f"{instruction.derived_from_point_code}/{instruction.derived_from_variant_code}"
                    f"+{instruction.longitude_offset_deg:g}"
                )
            else:
                longitude = normalize_360(
                    _engine_point_longitude(
                        julian_day,
                        engine,
                        instruction,
                        zodiac=zodiac,
                        ayanamsa=ayanamsa,
                        frame=frame,
                        lat=birth_lat,
                        lon=birth_lon,
                        altitude_m=altitude_m,
                    )
                )
                calculation_source = _calculation_source(engine, instruction)
            sign_code = sign_from_longitude(longitude, sign_codes)
            points_by_key[key] = {
                "code": point.code,
                "variant_code": instruction.variant_code,
                "planet_code": point.code,
                "longitude": round(longitude, 6),
                "sign": sign_code,
                "degree_in_sign": round(longitude % 30.0, 6),
                "house": assign_house_number(longitude, houses_raw),
                "calculation_source": calculation_source,
                "is_physical_body": point.is_physical_body,
            }
            pending.remove(point)
            progressed = True
        if not progressed:
            unresolved = ",".join(point.code for point in pending)
            _raise_invalid_reference(
                runtime_reference.reference_version,
                "astral_points",
                f"unresolved_derived_points:{unresolved}",
            )
    return list(points_by_key.values())


def build_natal_result(
    birth_input: BirthInput,
    runtime_reference: AstrologyRuntimeReference,
    ruleset_version: str,
    timeout_check: Callable[[], None] | None = None,
    engine: str = "simplified",
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    zodiac: ZodiacType = ZodiacType.TROPICAL,
    ayanamsa: str | None = None,
    frame: FrameType = FrameType.GEOCENTRIC,
    house_system: HouseSystemType = HouseSystemType.PLACIDUS,
    altitude_m: float | None = None,
    ephemeris_path_version: str | None = None,
    ephemeris_path_hash: str | None = None,
    tt_enabled: bool = False,
    derive_enabled: bool = False,
    aspect_school: str = "modern",
    aspect_rules_version: str = "1.0.0",
    include_points_in_aspects: bool = False,
) -> NatalResult:
    from app.domain.astrology.runtime.calculation_graph_runner import (
        CalculationGraphContext,
        CalculationGraphRunner,
    )
    from app.domain.astrology.runtime.natal_calculation_graph import (
        build_natal_calculation_graph_definition,
    )
    from app.domain.astrology.runtime.natal_calculation_registry import (
        build_natal_calculation_node_registry,
    )

    aspect_school_code = str(getattr(aspect_school, "value", aspect_school)).strip().lower()
    if timeout_check is not None:
        timeout_check()

    prepared = prepare_birth_data(birth_input, tt_enabled=tt_enabled, derive_enabled=derive_enabled)
    effective_house_system = (
        str(getattr(house_system, "value", house_system))
        if engine == "swisseph"
        else HOUSE_SYSTEM_CODE
    )
    context = CalculationGraphContext(
        {
            "birth_input": birth_input,
            "birth_datetime": birth_input.birth_date,
            "timezone": birth_input.birth_timezone or "",
            "coordinates": {"lat": birth_lat, "lon": birth_lon},
            "house_system": house_system,
            "zodiac_mode": zodiac,
            "runtime_reference": runtime_reference,
            "locale": "fr",
            "calculation_options": {
                "ruleset_version": ruleset_version,
                "engine": engine,
                "birth_lat": birth_lat,
                "birth_lon": birth_lon,
                "zodiac": zodiac,
                "ayanamsa": ayanamsa,
                "frame": frame,
                "house_system": house_system,
                "altitude_m": altitude_m,
                "ephemeris_path_version": ephemeris_path_version,
                "ephemeris_path_hash": ephemeris_path_hash,
                "tt_enabled": tt_enabled,
                "derive_enabled": derive_enabled,
                "aspect_school_code": aspect_school_code,
                "aspect_rules_version": aspect_rules_version,
                "include_points_in_aspects": include_points_in_aspects,
            },
            "prepared_birth_data": prepared,
            "julian_day": prepared.julian_day,
            "effective_house_system": effective_house_system,
            "timeout_check": timeout_check,
        }
    )
    execution = CalculationGraphRunner(build_natal_calculation_node_registry()).run(
        build_natal_calculation_graph_definition(),
        context,
    )
    if not execution.success:
        error = execution.errors[0]
        if isinstance(error.cause, NatalCalculationError):
            raise error.cause
        raise NatalCalculationError(
            code="natal_graph_node_failed",
            message=error.message,
            details={"node_code": str(error.node_code or ""), "key": str(error.key or "")},
        )
    result = execution.outputs.get("public_natal_result")
    if not isinstance(result, NatalResult):
        raise NatalCalculationError(
            code="missing_graph_output",
            message="natal graph output 'public_natal_result' is required",
            details={"output_key": "public_natal_result"},
        )
    # L'assemblage du graphe conserve le binding historique: dominant_planets=dominant_planets.
    return result


class _NatalInterpretationInputSource:
    """Source minimale pour construire l'input interpretatif sans publier de champ."""

    def __init__(
        self,
        *,
        chart_objects: tuple[ChartObjectRuntimeData, ...],
        aspects: tuple[AspectResult, ...],
        dominant_planets: DominantPlanetsResult,
        advanced_condition_facts: tuple[AdvancedPlanetaryCondition, ...],
    ) -> None:
        """Porte les faits deja calcules necessaires au builder interne."""
        self.chart_objects = chart_objects
        self.aspects = aspects
        self.dominant_planets = dominant_planets
        self.advanced_condition_facts = advanced_condition_facts
