"""Calcul du thème natal et structuration des résultats astrologiques."""

from __future__ import annotations

import math
from collections.abc import Callable
from math import isfinite

from pydantic import AliasChoices, BaseModel, Field, model_validator

from app.core.config import AspectSchoolType, FrameType, HouseSystemType, ZodiacType
from app.core.constants import MAX_ORB_DEG, MIN_ORB_DEG
from app.domain.astrology.advanced_conditions import (
    AdvancedConditionEngine,
    AdvancedPlanetaryCondition,
)
from app.domain.astrology.angle_utils import contains_angle
from app.domain.astrology.astral_point_calculation_resolver import (
    AstralPointCalculationInstruction,
    AstralPointCalculationResolver,
)
from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data
from app.domain.astrology.builders.house_runtime_builder import build_house_runtime_data
from app.domain.astrology.builders.sign_runtime_builder import build_sign_runtime_data
from app.domain.astrology.calculators import (
    calculate_houses,
    calculate_major_aspects,
    calculate_planet_positions,
)
from app.domain.astrology.calculators.aspects import build_aspect_body_from_position
from app.domain.astrology.calculators.houses import HOUSE_SYSTEM_CODE, assign_house_number
from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.condition.contracts import (
    PlanetConditionProfile,
    PlanetConditionSignalSet,
)
from app.domain.astrology.condition.planet_condition_profile_service import (
    PlanetConditionProfileService,
)
from app.domain.astrology.condition.planet_condition_signal_builder import (
    PlanetConditionSignalBuilder,
)
from app.domain.astrology.dignities.contracts import PlanetDignityInput, PlanetDignityResult
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.dominance.planet_dominance_engine import PlanetDominanceEngine
from app.domain.astrology.house_ruler_resolver import (
    HouseRulerResolutionError,
    HouseRulerResolver,
    HouseRulerResult,
)
from app.domain.astrology.interpretation.chart_signature import ChartSignatureCalculator
from app.domain.astrology.interpretation_adapters import (
    InterpretationAdapterEngine,
    InterpretationAdapterResult,
)
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData, prepare_birth_data
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectDefinitionRuntimeData,
    AspectOrbRuleRuntimeData,
)
from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData
from app.domain.astrology.runtime.chart_signature_runtime_data import ChartBalanceRuntimeData
from app.domain.astrology.runtime.house_runtime_data import HouseAxisRuntimeData, HouseRuntimeData
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    AstrologySystemReferenceSet,
)
from app.domain.astrology.runtime.sign_runtime_data import SignRuntimeData
from app.domain.astrology.zodiac import normalize_360, sign_from_longitude
from app.infra.observability.metrics import increment_counter


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
    default_valence: str
    interpretive_valence: str
    energy_type: str
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
    dignities: list[PlanetDignityResult] = Field(default_factory=list)
    condition_profiles: list[PlanetConditionProfile] = Field(default_factory=list)
    condition_signals: list[PlanetConditionSignalSet] = Field(default_factory=list)
    advanced_conditions: list[AdvancedPlanetaryCondition] = Field(default_factory=list)
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
) -> AspectResult:
    """Construit un resultat d'aspect avec le catalogue celeste de reference."""
    aspect = AspectResult.model_validate(payload)
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
    aspect_school_code = str(getattr(aspect_school, "value", aspect_school)).strip().lower()
    if timeout_check is not None:
        timeout_check()

    version = runtime_reference.reference_version
    if not version:
        raise NatalCalculationError(
            code="reference_version_not_found",
            message="reference version not found",
            details={"version": ""},
        )

    planets_data = runtime_reference.planets.items
    signs_data = runtime_reference.signs.items
    houses_data = runtime_reference.houses.items
    aspects_data = runtime_reference.aspects.items
    aspect_orb_rules_data = runtime_reference.aspects.orb_rules
    celestial_catalog = CelestialRuntimeCatalog.from_runtime_reference(runtime_reference)

    if not planets_data:
        _raise_invalid_reference(version, "planets", "missing_or_empty")
    if not signs_data:
        _raise_invalid_reference(version, "signs", "missing_or_empty")
    if not houses_data:
        _raise_invalid_reference(version, "houses", "missing_or_empty")
    if not aspects_data:
        _raise_invalid_reference(version, "aspects", "missing_or_empty")

    prepared = prepare_birth_data(birth_input, tt_enabled=tt_enabled, derive_enabled=derive_enabled)
    if timeout_check is not None:
        timeout_check()
    planet_codes = [item.code for item in planets_data if item.code]
    if not planet_codes:
        _raise_invalid_reference(version, "planets", "missing_code")

    sign_codes = [item.code for item in signs_data if item.code]
    if not sign_codes:
        _raise_invalid_reference(version, "signs", "missing_code")

    house_numbers: list[int] = []
    for item in houses_data:
        house_numbers.append(item.number)
    if not house_numbers:
        _raise_invalid_reference(version, "houses", "missing_number")

    # Engine-specific calculation
    if engine == "swisseph":
        if birth_lat is None or birth_lon is None:
            raise NatalCalculationError(
                code="missing_birth_coordinates",
                message="birth_lat and birth_lon are required for swisseph engine",
                details={"engine": engine},
            )
        positions_raw = _build_swisseph_positions(
            prepared.julian_day,
            planet_codes,
            sign_codes=sign_codes,
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            lat=birth_lat,
            lon=birth_lon,
            altitude_m=altitude_m,
        )
        if timeout_check is not None:
            timeout_check()
        houses_raw, effective_house_system = _build_swisseph_houses(
            prepared.julian_day,
            birth_lat,
            birth_lon,
            house_numbers,
            house_system=house_system,
            frame=frame,
            altitude_m=altitude_m,
        )
    else:
        positions_raw = calculate_planet_positions(prepared.julian_day, planet_codes, sign_codes)
        if timeout_check is not None:
            timeout_check()
        houses_raw = calculate_houses(prepared.julian_day, house_numbers)
        effective_house_system = HOUSE_SYSTEM_CODE

    _validate_house_cusps(version, houses_raw)
    if timeout_check is not None:
        timeout_check()

    points_raw = calculate_astral_points(
        julian_day=prepared.julian_day,
        runtime_reference=runtime_reference,
        sign_codes=sign_codes,
        houses_raw=houses_raw,
        engine=engine,
        zodiac=zodiac,
        ayanamsa=ayanamsa,
        frame=frame,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        altitude_m=altitude_m,
    )
    if timeout_check is not None:
        timeout_check()

    # Coherence invariant: house assignment must use the same cusp list we return.
    for position in positions_raw:
        longitude = float(position["longitude"])
        position["house_number"] = assign_house_number(longitude, houses_raw)
        expected_sign = sign_from_longitude(longitude, sign_codes)
        if str(position.get("sign_code")) != expected_sign:
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="planet sign does not match longitude",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "longitude": str(longitude),
                    "expected_sign_code": expected_sign,
                    "actual_sign_code": str(position.get("sign_code", "")),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )
        house_number = int(position["house_number"])
        current_cusp = next(
            (
                float(house["cusp_longitude"])
                for house in houses_raw
                if int(house["number"]) == house_number
            ),
            None,
        )
        next_house_number = 1 if house_number == 12 else house_number + 1
        next_cusp = next(
            (
                float(house["cusp_longitude"])
                for house in houses_raw
                if int(house["number"]) == next_house_number
            ),
            None,
        )
        if current_cusp is None or next_cusp is None:
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="house cusp interval is missing for assigned house",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "house_number": str(house_number),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )
        if not contains_angle(longitude, current_cusp, next_cusp):
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="planet house does not match cusp interval",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "longitude": str(longitude),
                    "house_number": str(house_number),
                    "interval_start": str(current_cusp),
                    "interval_end": str(next_cusp),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )

    aspect_definitions: list[AspectDefinitionRuntimeData] = []
    for item in aspects_data:
        if item.legacy_orb_fields:
            raise NatalCalculationError(
                code="invalid_reference_data",
                message="aspects reference data is invalid",
                details={
                    "reference_version": version,
                    "field": "aspects",
                    "reason": "legacy_orb_fields_forbidden",
                    "legacy_fields": ",".join(item.legacy_orb_fields),
                },
            )
        try:
            aspect_definition = AspectDefinitionRuntimeData(
                code=item.code,
                angle=item.angle,
                family=item.family,
                is_enabled=item.is_enabled,
                is_major=item.is_major,
                is_minor=item.is_minor,
                default_orb_deg=item.default_orb_deg,
                system_code=aspect_school_code,
                default_valence=item.default_valence,
                interpretive_valence=item.interpretive_valence,
                energy_type=item.energy_type,
            )
        except ValueError as error:
            _raise_invalid_reference(version, "aspects", str(error))
        default_orb_value = aspect_definition.default_orb_deg
        if default_orb_value is None:
            _raise_invalid_reference(version, "aspects", "missing_default_orb_deg")
        orb_in_bounds = (
            isfinite(default_orb_value) and MIN_ORB_DEG <= default_orb_value <= MAX_ORB_DEG
        )
        if not orb_in_bounds:
            _raise_invalid_reference(version, "aspects", "invalid_default_orb_deg")
        aspect_definitions.append(aspect_definition)
    if not aspect_definitions:
        _raise_invalid_reference(version, "aspects", "missing_code_or_angle")
    aspect_definitions.sort(key=lambda item: (item.angle, item.code))

    major_aspect_definitions = [
        definition
        for definition in aspect_definitions
        if definition.is_enabled
        and definition.is_major
        and definition.system_code == aspect_school_code
    ]
    if not aspect_orb_rules_data:
        _raise_invalid_reference(version, "aspect_orb_rules", "missing_or_empty")
    aspect_orb_rules: list[AspectOrbRuleRuntimeData] = []
    for item in aspect_orb_rules_data:
        try:
            aspect_orb_rule = AspectOrbRuleRuntimeData(
                aspect_code=item.aspect_code,
                system_code=item.system_code,
                calculation_context=item.calculation_context,
                source_body_type=item.source_body_type,
                source_planet_code=item.source_planet_code,
                source_point_code=item.source_point_code,
                target_body_type=item.target_body_type,
                target_planet_code=item.target_planet_code,
                target_point_code=item.target_point_code,
                orb_deg=item.orb_deg,
                priority=item.priority,
                is_enabled=item.is_enabled,
            )
        except ValueError as error:
            _raise_invalid_reference(version, "aspect_orb_rules", str(error))
        orb_rule_value = aspect_orb_rule.orb_deg
        if aspect_orb_rule.is_enabled:
            rule_in_bounds = (
                isfinite(orb_rule_value) and MIN_ORB_DEG < orb_rule_value <= MAX_ORB_DEG
            )
            if not rule_in_bounds:
                _raise_invalid_reference(version, "aspect_orb_rules", "invalid_orb_deg")
        aspect_orb_rules.append(aspect_orb_rule)

    system_inheritance = _build_system_inheritance(version, runtime_reference.systems)
    aspect_source_positions = [*positions_raw, *(points_raw if include_points_in_aspects else [])]
    aspect_positions = [
        build_aspect_body_from_position(position, celestial_catalog) for position in positions_raw
    ]
    if include_points_in_aspects:
        aspect_positions = [
            build_aspect_body_from_position(position, celestial_catalog)
            for position in aspect_source_positions
        ]

    aspects_raw = calculate_major_aspects(
        aspect_positions,
        major_aspect_definitions,
        orb_rules=aspect_orb_rules,
        system_code=aspect_school_code,
        calculation_context="natal",
        system_inheritance=system_inheritance,
    )
    if timeout_check is not None:
        timeout_check()

    # story 24-2 Observability: track aspects calculated and rejected by orb
    increment_counter(f"aspects_calculated_total_{aspect_school_code}", float(len(aspects_raw)))
    _total_checks = math.comb(len(aspect_source_positions), 2) * len(major_aspect_definitions)
    _rejected = _total_checks - len(aspects_raw)
    if _rejected > 0:
        increment_counter("aspects_rejected_orb_total", float(_rejected))

    positions = [PlanetPosition.model_validate(item) for item in positions_raw]
    dignity_inputs = tuple(
        PlanetDignityInput(
            planet_code=position.planet_code,
            longitude=position.longitude,
            sign_code=position.sign_code,
            house_number=position.house_number,
            speed_longitude=position.speed_longitude,
            is_retrograde=position.is_retrograde,
        )
        for position in positions
    )
    dignities = list(
        PlanetDignityScoringService().calculate(
            dignity_inputs,
            runtime_reference,
        )
    )
    condition_profiles = list(
        PlanetConditionProfileService().calculate(tuple(dignities), runtime_reference)
    )
    points = [NatalAstralPointPosition.model_validate(item) for item in points_raw]
    cusp_houses = [
        HouseRuntimeData(
            number=int(item["number"]),
            cusp_longitude=float(item["cusp_longitude"]),
        )
        for item in houses_raw
    ]
    sign_rulerships = _extract_sign_rulerships(runtime_reference)
    house_axes = _extract_house_axes(version, runtime_reference)
    try:
        house_rulers = HouseRulerResolver(sign_rulerships, sign_codes=sign_codes).resolve(
            cusp_houses,
            positions,
        )
    except HouseRulerResolutionError:
        _raise_invalid_reference(version, "sign_rulerships", "missing_or_incomplete")
    houses = build_house_runtime_data(
        houses=cusp_houses,
        planets=positions,
        house_rulers=house_rulers,
        house_system=effective_house_system,
        sign_rulerships=sign_rulerships,
        house_axes=house_axes,
        celestial_catalog=celestial_catalog,
        sign_codes=sign_codes,
    )
    signs_runtime = build_sign_runtime_data(
        signs=runtime_reference.signs,
        planets=positions,
        dignities=runtime_reference.dignities,
        celestial_catalog=celestial_catalog,
    )
    aspects = [_build_aspect_result(item, celestial_catalog) for item in aspects_raw]
    advanced_conditions, enriched_condition_profiles = AdvancedConditionEngine().calculate(
        runtime_reference=runtime_reference,
        planet_positions=tuple(positions),
        aspects=tuple(aspects),
        dignities=tuple(dignities),
        condition_profiles=tuple(condition_profiles),
    )
    condition_profiles = list(enriched_condition_profiles)
    condition_signals = list(
        PlanetConditionSignalBuilder().build(tuple(condition_profiles), runtime_reference)
    )
    chart_balance = ChartSignatureCalculator().calculate(
        signs=signs_runtime,
        houses=houses,
        aspects=tuple(
            aspect.aspect_runtime for aspect in aspects if aspect.aspect_runtime is not None
        ),
    )
    dominant_planets = PlanetDominanceEngine().calculate(
        runtime_reference=runtime_reference,
        planet_positions=positions,
        houses=houses,
        house_rulers=house_rulers,
        condition_profiles=condition_profiles,
        advanced_conditions=tuple(advanced_conditions),
        aspects=aspects,
    )
    interpretation_adapter = InterpretationAdapterEngine().calculate(
        runtime_reference=runtime_reference,
        planet_positions=positions,
        aspects=aspects,
        dignities=dignities,
        condition_profiles=condition_profiles,
        condition_signals=condition_signals,
        advanced_conditions=tuple(advanced_conditions),
        dominant_planets=dominant_planets,
    )

    return NatalResult(
        reference_version=version,
        ruleset_version=ruleset_version,
        house_system=effective_house_system,
        engine=engine,
        zodiac=zodiac,
        frame=frame,
        ayanamsa=ayanamsa,
        altitude_m=altitude_m,
        ephemeris_path_version=ephemeris_path_version,
        ephemeris_path_hash=ephemeris_path_hash,
        time_scale=prepared.time_scale,
        aspect_school=aspect_school_code,
        aspect_rules_version=aspect_rules_version,
        prepared_input=prepared,
        planet_positions=positions,
        houses=houses,
        signs_runtime=signs_runtime,
        chart_balance=chart_balance,
        house_rulers=house_rulers,
        astral_points=points,
        dignities=dignities,
        condition_profiles=condition_profiles,
        condition_signals=condition_signals,
        advanced_conditions=list(advanced_conditions),
        dominant_planets=dominant_planets,
        interpretation_adapter=interpretation_adapter,
        aspects=aspects,
    )
