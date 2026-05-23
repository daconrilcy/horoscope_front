# Adapters des nodes du graphe natal vers les calculateurs astrologiques existants.
"""Fournit les calculateurs explicites consommes par le runner du graphe natal."""

from __future__ import annotations

import math
from dataclasses import dataclass
from math import isfinite

from app.core.constants import MAX_ORB_DEG, MIN_ORB_DEG
from app.domain.astrology.advanced_conditions import (
    AdvancedConditionEngine,
    AdvancedPlanetaryCondition,
    TraditionalConditionsResult,
)
from app.domain.astrology.angle_utils import contains_angle
from app.domain.astrology.builders.chart_object_house_runtime_enricher import (
    RulershipPayloadEnricher,
)
from app.domain.astrology.builders.house_runtime_builder import build_house_runtime_data
from app.domain.astrology.builders.sign_runtime_builder import build_sign_runtime_data
from app.domain.astrology.calculators.aspect_inputs import (
    AspectBodyProjector,
    AspectChartObjectSelector,
)
from app.domain.astrology.calculators.houses import HOUSE_SYSTEM_CODE, assign_house_number
from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.condition.contracts import PlanetConditionProfile
from app.domain.astrology.condition.planet_condition_profile_service import (
    PlanetConditionProfileService,
)
from app.domain.astrology.condition.planet_condition_signal_builder import (
    PlanetConditionSignalBuilder,
)
from app.domain.astrology.dignities.chart_object_inputs import (
    DignityChartObjectSelector,
    DignityInputProjector,
    DignityPayloadEnricher,
)
from app.domain.astrology.dignities.contracts import ChartSectResult, PlanetDignityResult
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from app.domain.astrology.dominance.chart_object_inputs import (
    DominanceChartObjectSelector,
    DominanceInputProjector,
    DominancePayloadEnricher,
)
from app.domain.astrology.dominance.contracts import DominantPlanetsResult
from app.domain.astrology.dominance.planet_dominance_engine import PlanetDominanceEngine
from app.domain.astrology.fixed_stars.fixed_star_conjunction_calculator import (
    FixedStarConjunctionCalculator,
)
from app.domain.astrology.fixed_stars.fixed_star_enricher import FixedStarConjunctionEnricher
from app.domain.astrology.house_ruler_resolver import HouseRulerResolutionError, HouseRulerResult
from app.domain.astrology.interpretation.advanced_conditions import (
    AdvancedConditionInterpretationProfile,
    resolve_advanced_condition_profiles,
)
from app.domain.astrology.interpretation.chart_interpretation_input_builder import (
    ChartInterpretationInputBuilder,
)
from app.domain.astrology.interpretation.chart_signature import ChartSignatureCalculator
from app.domain.astrology.interpretation_adapters import (
    InterpretationAdapterEngine,
    InterpretationAdapterResult,
)
from app.domain.astrology.natal_calculation import (
    AspectResult,
    NatalAstralPointPosition,
    NatalCalculationError,
    PlanetPosition,
    _build_aspect_result,
    _build_system_inheritance,
    _extract_house_axes,
    _extract_sign_rulerships,
    _NatalInterpretationInputSource,
    _raise_invalid_reference,
    _validate_house_cusps,
)
from app.domain.astrology.natal_preparation import BirthPreparedData, prepare_birth_data
from app.domain.astrology.planetary_conditions import (
    AdvancedPlanetaryConditionsResult,
    calculate_advanced_planetary_conditions,
)
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectDefinitionRuntimeData,
    AspectOrbRuleRuntimeData,
)
from app.domain.astrology.runtime.calculation_graph_runner import CalculationGraphContext
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectRuntimeData,
    FixedStarConjunctionRuntimePayload,
    validate_dignity_payloads,
    validate_dominance_payloads,
    validate_rulership_payloads,
)
from app.domain.astrology.runtime.chart_signature_runtime_data import ChartBalanceRuntimeData
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference
from app.domain.astrology.runtime.sign_runtime_data import SignRuntimeData
from app.domain.astrology.zodiac import sign_from_longitude
from app.infra.observability.metrics import increment_counter


@dataclass(frozen=True, slots=True)
class NatalFixedStarOutput:
    """Sortie canonique des conjonctions avec enrichissement chart-object associe."""

    conjunctions: tuple[FixedStarConjunctionRuntimePayload, ...]
    chart_objects: tuple[ChartObjectRuntimeData, ...]


@dataclass(frozen=True, slots=True)
class NatalDignityOutput:
    """Sortie des dignites avec les payloads runtime qui en dependent."""

    dignities: tuple[PlanetDignityResult, ...]
    dignity_sect: ChartSectResult | None
    condition_profiles: tuple[PlanetConditionProfile, ...]
    chart_objects: tuple[ChartObjectRuntimeData, ...]
    interpretation_profiles_by_planet: dict[str, tuple[AdvancedConditionInterpretationProfile, ...]]


@dataclass(frozen=True, slots=True)
class NatalAdvancedConditionsOutput:
    """Sortie des conditions avancees et des profils enrichis associes."""

    advanced_conditions: tuple[AdvancedPlanetaryCondition, ...]
    condition_profiles: tuple[PlanetConditionProfile, ...]
    condition_signals: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class NatalDominanceOutput:
    """Sortie de dominance et chart objects finaux enrichis."""

    dominant_planets: DominantPlanetsResult
    chart_objects: tuple[ChartObjectRuntimeData, ...]


@dataclass(frozen=True, slots=True)
class NatalInterpretationOutput:
    """Sortie interpretative interne conservee hors JSON public."""

    interpretation_adapter: InterpretationAdapterResult
    traditional_conditions: TraditionalConditionsResult


def prepare_birth_data_node(context: CalculationGraphContext) -> BirthPreparedData:
    """Prepare les donnees de naissance a partir des options du graphe."""
    options = _options(context)
    return prepare_birth_data(
        _required(context, "birth_input"),
        tt_enabled=bool(options["tt_enabled"]),
        derive_enabled=bool(options["derive_enabled"]),
    )


def calculate_houses_node(context: CalculationGraphContext) -> list[dict[str, object]]:
    """Calcule les cuspides de maisons en deleguant au moteur actif."""
    from app.domain.astrology import natal_calculation

    prepared = _prepared(context)
    house_numbers = _house_numbers(_runtime_reference(context))
    options = _options(context)
    if options["engine"] == "swisseph":
        birth_lat = options["birth_lat"]
        birth_lon = options["birth_lon"]
        if birth_lat is None or birth_lon is None:
            raise NatalCalculationError(
                code="missing_birth_coordinates",
                message="birth_lat and birth_lon are required for swisseph engine",
                details={"engine": str(options["engine"])},
            )
        houses_raw, _effective_house_system_name = natal_calculation._build_swisseph_houses(
            prepared.julian_day,
            float(birth_lat),
            float(birth_lon),
            house_numbers,
            house_system=options["house_system"],
            frame=options["frame"],
            altitude_m=options["altitude_m"],
        )
    else:
        houses_raw = natal_calculation.calculate_houses(prepared.julian_day, house_numbers)
    _validate_house_cusps(_version(context), houses_raw)
    _run_timeout(context)
    return houses_raw


def calculate_planet_positions_node(context: CalculationGraphContext) -> list[PlanetPosition]:
    """Calcule les positions planetaires puis valide maisons et signes."""
    prepared = _prepared(context)
    runtime_reference = _runtime_reference(context)
    planet_codes = _planet_codes(runtime_reference)
    sign_codes = _sign_codes(runtime_reference)
    houses_raw = _required(context, "houses_raw")
    options = _options(context)
    from app.domain.astrology import natal_calculation

    if options["engine"] == "swisseph":
        positions_raw = natal_calculation._build_swisseph_positions(
            prepared.julian_day,
            planet_codes,
            sign_codes=sign_codes,
            zodiac=options["zodiac"],
            ayanamsa=options["ayanamsa"],
            frame=options["frame"],
            lat=options["birth_lat"],
            lon=options["birth_lon"],
            altitude_m=options["altitude_m"],
        )
    else:
        positions_raw = natal_calculation.calculate_planet_positions(
            prepared.julian_day,
            planet_codes,
            sign_codes,
        )
    _assign_and_validate_planet_houses(
        positions_raw,
        houses_raw,
        sign_codes,
        _version(context),
        _effective_house_system(context),
    )
    _run_timeout(context)
    return [PlanetPosition.model_validate(item) for item in positions_raw]


def calculate_astral_points_node(
    context: CalculationGraphContext,
) -> list[NatalAstralPointPosition]:
    """Calcule les points astraux depuis le resolver existant."""
    options = _options(context)
    from app.domain.astrology import natal_calculation

    points_raw = natal_calculation.calculate_astral_points(
        julian_day=_prepared(context).julian_day,
        runtime_reference=_runtime_reference(context),
        sign_codes=_sign_codes(_runtime_reference(context)),
        houses_raw=_required(context, "houses_raw"),
        engine=str(options["engine"]),
        zodiac=options["zodiac"],
        ayanamsa=options["ayanamsa"],
        frame=options["frame"],
        birth_lat=options["birth_lat"],
        birth_lon=options["birth_lon"],
        altitude_m=options["altitude_m"],
    )
    _run_timeout(context)
    return [NatalAstralPointPosition.model_validate(item) for item in points_raw]


def resolve_house_rulerships_node(context: CalculationGraphContext) -> list[HouseRulerResult]:
    """Resout les gouvernances de maisons via `HouseRulerResolver`."""
    from app.domain.astrology.house_ruler_resolver import HouseRulerResolver

    runtime_reference = _runtime_reference(context)
    sign_codes = _sign_codes(runtime_reference)
    sign_rulerships = _extract_sign_rulerships(runtime_reference)
    cusp_houses = _cusp_houses(context)
    try:
        return list(
            HouseRulerResolver(sign_rulerships, sign_codes=sign_codes).resolve(
                cusp_houses,
                _required(context, "planet_positions"),
            )
        )
    except HouseRulerResolutionError:
        _raise_invalid_reference(_version(context), "sign_rulerships", "missing_or_incomplete")


def build_houses_runtime_node(context: CalculationGraphContext) -> list[HouseRuntimeData]:
    """Construit les maisons runtime depuis les cuspides et rulers existants."""
    runtime_reference = _runtime_reference(context)
    return list(
        build_house_runtime_data(
            houses=_cusp_houses(context),
            planets=_required(context, "planet_positions"),
            house_rulers=_required(context, "house_rulerships"),
            house_system=_effective_house_system(context),
            sign_rulerships=_extract_sign_rulerships(runtime_reference),
            house_axes=_extract_house_axes(_version(context), runtime_reference),
            celestial_catalog=_celestial_catalog(context),
            sign_codes=_sign_codes(runtime_reference),
        )
    )


def build_motion_visibility_payloads_node(
    context: CalculationGraphContext,
) -> AdvancedPlanetaryConditionsResult:
    """Calcule les conditions planetaires avancees sans recalcul chart-object."""
    positions = _required(context, "planet_positions")
    return calculate_advanced_planetary_conditions(
        planetary_positions={position.planet_code: position for position in positions},
        planetary_speeds_deg_per_day={
            position.planet_code: position.speed_longitude
            for position in positions
            if position.speed_longitude is not None
        },
    )


def build_chart_object_runtime_data_node(
    context: CalculationGraphContext,
) -> list[ChartObjectRuntimeData]:
    """Construit les chart objects puis ajoute les payloads de rulership."""
    from app.domain.astrology import natal_calculation

    runtime_reference = _runtime_reference(context)
    chart_objects = list(
        natal_calculation.build_chart_object_runtime_data(
            planet_positions=_required(context, "planet_positions"),
            astral_points=_required(context, "astral_points"),
            houses=_required(context, "houses_runtime"),
            fixed_stars=runtime_reference.fixed_stars.items,
            advanced_planetary_conditions=_required(context, "motion_visibility_payloads"),
            include_astral_points_in_aspects=bool(_options(context)["include_points_in_aspects"]),
            include_angles_in_aspects=False,
        )
    )
    chart_objects = list(
        RulershipPayloadEnricher().enrich(
            chart_objects,
            _required(context, "house_rulerships"),
            _extract_sign_rulerships(runtime_reference),
        )
    )
    validate_rulership_payloads(tuple(chart_objects))
    return chart_objects


def calculate_fixed_star_conjunctions_node(
    context: CalculationGraphContext,
) -> NatalFixedStarOutput:
    """Delegue le calcul fixed-star puis conserve les chart objects enrichis."""
    chart_objects = _required(context, "chart_objects")
    conjunctions = tuple(FixedStarConjunctionCalculator().calculate(chart_objects))
    enriched = tuple(FixedStarConjunctionEnricher().enrich(chart_objects, conjunctions))
    return NatalFixedStarOutput(conjunctions=conjunctions, chart_objects=enriched)


def calculate_major_aspects_node(context: CalculationGraphContext) -> list[AspectResult]:
    """Calcule les aspects depuis les chart objects enrichis fixed-star."""
    aspect_definitions, aspect_orb_rules = _aspect_runtime_rules(context)
    chart_objects = _chart_objects_after_fixed_stars(context)
    aspectable_chart_objects = AspectChartObjectSelector().select(chart_objects)
    aspect_positions = list(
        AspectBodyProjector(_celestial_catalog(context)).project_many(aspectable_chart_objects)
    )
    from app.domain.astrology import natal_calculation

    aspects_raw = natal_calculation.calculate_major_aspects(
        aspect_positions,
        aspect_definitions,
        orb_rules=aspect_orb_rules,
        system_code=_aspect_school_code(context),
        calculation_context="natal",
        system_inheritance=_build_system_inheritance(
            _version(context),
            _runtime_reference(context).systems,
        ),
    )
    _run_timeout(context)
    increment_counter(
        f"aspects_calculated_total_{_aspect_school_code(context)}",
        float(len(aspects_raw)),
    )
    rejected = math.comb(len(aspect_positions), 2) * len(aspect_definitions) - len(aspects_raw)
    if rejected > 0:
        increment_counter("aspects_rejected_orb_total", float(rejected))
    return [_build_aspect_result(item, _celestial_catalog(context)) for item in aspects_raw]


def calculate_dignities_node(context: CalculationGraphContext) -> NatalDignityOutput:
    """Calcule les dignites et enrichit les chart objects par payloads."""
    runtime_reference = _runtime_reference(context)
    advanced_planetary_conditions = _required(context, "motion_visibility_payloads")
    chart_objects = _chart_objects_after_fixed_stars(context)
    dignity_inputs = DignityInputProjector().project_many(
        DignityChartObjectSelector().choose(chart_objects)
    )
    dignities = tuple(
        PlanetDignityScoringService().calculate(
            dignity_inputs,
            runtime_reference,
            advanced_planetary_conditions=advanced_planetary_conditions,
        )
    )
    enriched = tuple(DignityPayloadEnricher().enrich(chart_objects, dignities))
    validate_dignity_payloads(enriched)
    condition_profiles = tuple(
        PlanetConditionProfileService().calculate(dignities, runtime_reference)
    )
    interpretation_profiles_by_planet = {
        planet_key: resolve_advanced_condition_profiles(
            bundle=bundle,
            moon_phase=advanced_planetary_conditions.moon_phase,
        )
        for planet_key, bundle in advanced_planetary_conditions.conditions_by_planet.items()
    }
    return NatalDignityOutput(
        dignities=dignities,
        dignity_sect=dignities[0].chart_sect if dignities else None,
        condition_profiles=condition_profiles,
        chart_objects=enriched,
        interpretation_profiles_by_planet=interpretation_profiles_by_planet,
    )


def build_sign_runtime_data_node(context: CalculationGraphContext) -> list[SignRuntimeData]:
    """Construit les signes runtime avec les dignites deja calculees."""
    return list(
        build_sign_runtime_data(
            signs=_runtime_reference(context).signs,
            planets=_required(context, "planet_positions"),
            dignities=_runtime_reference(context).dignities,
            celestial_catalog=_celestial_catalog(context),
        )
    )


def calculate_advanced_conditions_node(
    context: CalculationGraphContext,
) -> NatalAdvancedConditionsOutput:
    """Calcule les conditions avancees depuis aspects, dignites et profils."""
    dignity_output = _required(context, "dignities")
    advanced_conditions, enriched_condition_profiles = AdvancedConditionEngine().calculate(
        runtime_reference=_runtime_reference(context),
        planet_positions=tuple(_required(context, "planet_positions")),
        aspects=tuple(_required(context, "aspects_runtime")),
        dignities=dignity_output.dignities,
        condition_profiles=dignity_output.condition_profiles,
    )
    condition_profiles = tuple(enriched_condition_profiles)
    condition_signals = tuple(
        PlanetConditionSignalBuilder().build(condition_profiles, _runtime_reference(context))
    )
    return NatalAdvancedConditionsOutput(
        advanced_conditions=tuple(advanced_conditions),
        condition_profiles=condition_profiles,
        condition_signals=condition_signals,
    )


def calculate_chart_signature_node(context: CalculationGraphContext) -> ChartBalanceRuntimeData:
    """Calcule la signature du theme depuis les surfaces runtime."""
    return ChartSignatureCalculator().calculate(
        signs=_required(context, "signs_runtime"),
        houses=_required(context, "houses_runtime"),
        aspects=tuple(
            aspect.aspect_runtime
            for aspect in _required(context, "aspects_runtime")
            if aspect.aspect_runtime is not None
        ),
    )


def calculate_dominance_node(context: CalculationGraphContext) -> NatalDominanceOutput:
    """Calcule la dominance puis enrichit les chart objects finaux."""
    dignity_output = _required(context, "dignities")
    advanced_output = _required(context, "advanced_conditions")
    dominance_inputs = DominanceInputProjector().project_many(
        DominanceChartObjectSelector().choose(dignity_output.chart_objects)
    )
    dominant_planets = PlanetDominanceEngine().calculate(
        runtime_reference=_runtime_reference(context),
        chart_object_positions=dominance_inputs,
        houses=_required(context, "houses_runtime"),
        house_rulers=_required(context, "house_rulerships"),
        condition_profiles=list(advanced_output.condition_profiles),
        advanced_conditions=advanced_output.advanced_conditions,
        aspects=_required(context, "aspects_runtime"),
    )
    chart_objects = tuple(
        DominancePayloadEnricher().enrich(dignity_output.chart_objects, dominant_planets.planets)
    )
    validate_dominance_payloads(chart_objects)
    return NatalDominanceOutput(dominant_planets=dominant_planets, chart_objects=chart_objects)


def build_interpretation_input_node(context: CalculationGraphContext) -> NatalInterpretationOutput:
    """Construit les sorties interpretatives internes apres dominance."""
    dominance_output = _required(context, "dominance")
    advanced_output = _required(context, "advanced_conditions")
    chart_interpretation_input = ChartInterpretationInputBuilder().build(
        _NatalInterpretationInputSource(
            chart_objects=dominance_output.chart_objects,
            aspects=tuple(_required(context, "aspects_runtime")),
            dominant_planets=dominance_output.dominant_planets,
            advanced_condition_facts=advanced_output.advanced_conditions,
        )
    )
    interpretation_adapter = InterpretationAdapterEngine().calculate(
        runtime_reference=_runtime_reference(context),
        interpretation_input=chart_interpretation_input,
        condition_profiles=list(advanced_output.condition_profiles),
        condition_signals=list(advanced_output.condition_signals),
    )
    from app.domain.astrology.advanced_conditions import TraditionalConditionNormalizer

    traditional_conditions = TraditionalConditionNormalizer().normalize(
        dignities=list(_required(context, "dignities").dignities),
        planet_positions=list(_required(context, "planet_positions")),
        advanced_conditions=advanced_output.advanced_conditions,
        runtime_reference=_runtime_reference(context),
    )
    return NatalInterpretationOutput(
        interpretation_adapter=interpretation_adapter,
        traditional_conditions=traditional_conditions,
    )


def project_identity_node(context: CalculationGraphContext, key: str) -> object:
    """Expose une projection legacy comme sortie terminale sans nouveau calcul."""
    return _required(context, key)


def project_public_natal_result_node(context: CalculationGraphContext) -> object:
    """Delegue l'assemblage final a l'assembler dedie."""
    from app.domain.astrology.runtime.natal_result_assembler import NatalResultAssembler

    return NatalResultAssembler().assemble(context)


def _assign_and_validate_planet_houses(
    positions_raw: list[dict[str, object]],
    houses_raw: list[dict[str, object]],
    sign_codes: list[str],
    version: str,
    effective_house_system: str,
) -> None:
    """Assigne les maisons et conserve les invariants de coherence historiques."""
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
        _validate_planet_house_interval(position, houses_raw, version, effective_house_system)


def _validate_planet_house_interval(
    position: dict[str, object],
    houses_raw: list[dict[str, object]],
    version: str,
    effective_house_system: str,
) -> None:
    """Verifie que la maison assignee contient bien la longitude planetaire."""
    longitude = float(position["longitude"])
    house_number = int(position["house_number"])
    current_cusp = _house_cusp(houses_raw, house_number)
    next_cusp = _house_cusp(houses_raw, 1 if house_number == 12 else house_number + 1)
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


def _house_cusp(houses_raw: list[dict[str, object]], house_number: int) -> float | None:
    """Retourne une cuspide normalisee pour une maison donnee."""
    return next(
        (
            float(house["cusp_longitude"])
            for house in houses_raw
            if int(house["number"]) == house_number
        ),
        None,
    )


def _aspect_runtime_rules(
    context: CalculationGraphContext,
) -> tuple[list[AspectDefinitionRuntimeData], list[AspectOrbRuleRuntimeData]]:
    """Construit les definitions d'aspects runtime depuis le referentiel."""
    runtime_reference = _runtime_reference(context)
    aspect_school_code = _aspect_school_code(context)
    aspect_definitions = [
        _aspect_definition(context, item) for item in runtime_reference.aspects.items
    ]
    if not aspect_definitions:
        _raise_invalid_reference(_version(context), "aspects", "missing_code_or_angle")
    aspect_definitions.sort(key=lambda item: (item.angle, item.code))
    major_aspect_definitions = [
        definition
        for definition in aspect_definitions
        if definition.is_enabled
        and definition.is_major
        and definition.system_code == aspect_school_code
    ]
    if not runtime_reference.aspects.orb_rules:
        _raise_invalid_reference(_version(context), "aspect_orb_rules", "missing_or_empty")
    return major_aspect_definitions, [
        _aspect_orb_rule(context, item) for item in runtime_reference.aspects.orb_rules
    ]


def _aspect_definition(
    context: CalculationGraphContext,
    item: object,
) -> AspectDefinitionRuntimeData:
    """Valide une definition d'aspect issue du referentiel."""
    if item.legacy_orb_fields:
        raise NatalCalculationError(
            code="invalid_reference_data",
            message="aspects reference data is invalid",
            details={
                "reference_version": _version(context),
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
            system_code=_aspect_school_code(context),
            default_valence=item.default_valence,
            interpretive_valence=item.interpretive_valence,
            energy_type=item.energy_type,
        )
    except ValueError as error:
        _raise_invalid_reference(_version(context), "aspects", str(error))
    default_orb_value = aspect_definition.default_orb_deg
    if default_orb_value is None:
        _raise_invalid_reference(_version(context), "aspects", "missing_default_orb_deg")
    if not (isfinite(default_orb_value) and MIN_ORB_DEG <= default_orb_value <= MAX_ORB_DEG):
        _raise_invalid_reference(_version(context), "aspects", "invalid_default_orb_deg")
    return aspect_definition


def _aspect_orb_rule(context: CalculationGraphContext, item: object) -> AspectOrbRuleRuntimeData:
    """Valide une regle d'orbe issue du referentiel."""
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
        _raise_invalid_reference(_version(context), "aspect_orb_rules", str(error))
    if aspect_orb_rule.is_enabled and not (
        isfinite(aspect_orb_rule.orb_deg) and MIN_ORB_DEG < aspect_orb_rule.orb_deg <= MAX_ORB_DEG
    ):
        _raise_invalid_reference(_version(context), "aspect_orb_rules", "invalid_orb_deg")
    return aspect_orb_rule


def _chart_objects_after_fixed_stars(
    context: CalculationGraphContext,
) -> tuple[ChartObjectRuntimeData, ...]:
    """Retourne les chart objects enrichis fixed-star si le node est disponible."""
    fixed_output = context.values.get("fixed_star_conjunctions")
    if isinstance(fixed_output, NatalFixedStarOutput):
        return fixed_output.chart_objects
    return tuple(_required(context, "chart_objects"))


def _cusp_houses(context: CalculationGraphContext) -> list[HouseRuntimeData]:
    """Projette les cuspides brutes en objets runtime minimaux."""
    return [
        HouseRuntimeData(number=int(item["number"]), cusp_longitude=float(item["cusp_longitude"]))
        for item in _required(context, "houses_raw")
    ]


def _runtime_reference(context: CalculationGraphContext) -> AstrologyRuntimeReference:
    """Retourne le referentiel runtime attendu par les nodes."""
    return _required(context, "runtime_reference")


def _prepared(context: CalculationGraphContext) -> BirthPreparedData:
    """Retourne les donnees de naissance preparees."""
    return _required(context, "prepared_birth_data")


def _version(context: CalculationGraphContext) -> str:
    """Retourne la version de reference avec validation minimale."""
    version = _runtime_reference(context).reference_version
    if not version:
        raise NatalCalculationError(
            code="reference_version_not_found",
            message="reference version not found",
            details={"version": ""},
        )
    return version


def _options(context: CalculationGraphContext) -> dict[str, object]:
    """Retourne les options de calcul injectees dans le contexte."""
    return _required(context, "calculation_options")


def _aspect_school_code(context: CalculationGraphContext) -> str:
    """Normalise le code d'ecole d'aspects pour le graphe."""
    return str(_options(context)["aspect_school_code"])


def _effective_house_system(context: CalculationGraphContext) -> str:
    """Retourne le house system effectif, avec override swisseph si present."""
    return str(context.values.get("effective_house_system", HOUSE_SYSTEM_CODE))


def _celestial_catalog(context: CalculationGraphContext) -> CelestialRuntimeCatalog:
    """Construit le catalogue celeste depuis le referentiel courant."""
    return CelestialRuntimeCatalog.from_runtime_reference(_runtime_reference(context))


def _planet_codes(runtime_reference: AstrologyRuntimeReference) -> list[str]:
    """Extrait et valide les codes planetaires."""
    planets_data = runtime_reference.planets.items
    if not planets_data:
        _raise_invalid_reference(runtime_reference.reference_version, "planets", "missing_or_empty")
    planet_codes = [item.code for item in planets_data if item.code]
    if not planet_codes:
        _raise_invalid_reference(runtime_reference.reference_version, "planets", "missing_code")
    return planet_codes


def _sign_codes(runtime_reference: AstrologyRuntimeReference) -> list[str]:
    """Extrait et valide les codes de signes."""
    signs_data = runtime_reference.signs.items
    if not signs_data:
        _raise_invalid_reference(runtime_reference.reference_version, "signs", "missing_or_empty")
    sign_codes = [item.code for item in signs_data if item.code]
    if not sign_codes:
        _raise_invalid_reference(runtime_reference.reference_version, "signs", "missing_code")
    return sign_codes


def _house_numbers(runtime_reference: AstrologyRuntimeReference) -> list[int]:
    """Extrait et valide les numeros de maisons."""
    houses_data = runtime_reference.houses.items
    if not houses_data:
        _raise_invalid_reference(runtime_reference.reference_version, "houses", "missing_or_empty")
    house_numbers = [item.number for item in houses_data]
    if not house_numbers:
        _raise_invalid_reference(runtime_reference.reference_version, "houses", "missing_number")
    return house_numbers


def _run_timeout(context: CalculationGraphContext) -> None:
    """Execute le callback de timeout si la facade en a fourni un."""
    timeout_check = context.values.get("timeout_check")
    if timeout_check is not None:
        timeout_check()


def _required(context: CalculationGraphContext, key: str):
    """Retourne une valeur obligatoire avec un typage souple pour les adapters."""
    return context.get_required(key)
