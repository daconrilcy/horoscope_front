"""Tests du contrat runtime unifie des objets du theme natal."""

from __future__ import annotations

import pytest

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.natal_calculation import NatalAstralPointPosition, PlanetPosition
from app.domain.astrology.planetary_conditions.contracts import (
    AdvancedPlanetaryConditionsResult,
    ConditionConfidence,
    ConditionSeverity,
    PlanetaryConditionsBundle,
    PlanetaryMotionCondition,
    PlanetaryMotionDirection,
    PlanetarySolarPhaseRelation,
    PlanetarySpeedState,
    PlanetVisibilityCondition,
    PlanetVisibilityKey,
    SolarPhaseRelationKey,
    SolarProximityCondition,
    SolarProximityConditionKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData


def _planet_positions() -> tuple[PlanetPosition, ...]:
    """Construit des positions planetaires couvrant luminaire et planete."""
    return (
        PlanetPosition(
            planet_code="sun",
            longitude=84.5,
            sign_code="gemini",
            house_number=10,
            speed_longitude=0.95,
            is_retrograde=False,
        ),
        PlanetPosition(
            planet_code="mars",
            longitude=122.0,
            sign_code="leo",
            house_number=11,
            speed_longitude=-0.2,
            is_retrograde=True,
        ),
    )


def _astral_points() -> tuple[NatalAstralPointPosition, ...]:
    """Construit des points astraux deja normalises par le pipeline natal."""
    return (
        NatalAstralPointPosition(
            code="north_node",
            variant_code="true",
            longitude=27.5,
            sign="aries",
            degree_in_sign=27.5,
            house=2,
            calculation_source="simplified:SE_TRUE_NODE",
            is_physical_body=False,
        ),
        NatalAstralPointPosition(
            code="south_node",
            variant_code="true",
            longitude=207.5,
            sign="libra",
            degree_in_sign=27.5,
            house=8,
            calculation_source="derived:north_node/true+180",
            is_physical_body=False,
        ),
    )


def _houses() -> tuple[HouseRuntimeData, ...]:
    """Construit douze maisons runtime avec cuspides stables."""
    return tuple(
        HouseRuntimeData(number=number, cusp_longitude=float((number - 1) * 30))
        for number in range(1, 13)
    )


def _advanced_conditions() -> AdvancedPlanetaryConditionsResult:
    """Construit les conditions avancees deja calculees pour la projection."""
    return AdvancedPlanetaryConditionsResult(
        conditions_by_planet={
            "sun": PlanetaryConditionsBundle(
                planet_key="sun",
                motion=PlanetaryMotionCondition(
                    planet_key="sun",
                    speed_deg_per_day=0.95,
                    absolute_speed_deg_per_day=0.95,
                    direction=PlanetaryMotionDirection.DIRECT,
                    speed_state=PlanetarySpeedState.NORMAL,
                    is_retrograde=False,
                    is_stationary=False,
                    normalized_speed_ratio=1.0,
                ),
                visibility=PlanetVisibilityCondition(
                    planet_key="sun",
                    visibility_key=PlanetVisibilityKey.VISIBLE,
                    is_visible=True,
                    confidence=ConditionConfidence.HIGH,
                    reason="sun_visible",
                ),
            ),
            "mars": PlanetaryConditionsBundle(
                planet_key="mars",
                motion=PlanetaryMotionCondition(
                    planet_key="mars",
                    speed_deg_per_day=-0.2,
                    absolute_speed_deg_per_day=0.2,
                    direction=PlanetaryMotionDirection.RETROGRADE,
                    speed_state=PlanetarySpeedState.SLOW,
                    is_retrograde=True,
                    is_stationary=False,
                    normalized_speed_ratio=0.5,
                ),
                solar_proximity=SolarProximityCondition(
                    planet_key="mars",
                    condition_key=SolarProximityConditionKey.COMBUST,
                    sun_distance_deg=6.0,
                    orb_deg=8.5,
                    severity=ConditionSeverity.MAJOR,
                    is_active=True,
                ),
                solar_phase_relation=PlanetarySolarPhaseRelation(
                    planet_key="mars",
                    relation_key=SolarPhaseRelationKey.OCCIDENTAL,
                    angular_distance_deg=6.0,
                    is_oriental=False,
                    is_occidental=True,
                ),
                visibility=PlanetVisibilityCondition(
                    planet_key="mars",
                    visibility_key=PlanetVisibilityKey.INVISIBLE,
                    is_visible=False,
                    confidence=ConditionConfidence.HIGH,
                    reason="combust",
                ),
            ),
        }
    )


def _objects_by_code() -> dict[str, ChartObjectRuntimeData]:
    """Indexe la projection runtime par code objet."""
    objects = build_chart_object_runtime_data(
        planet_positions=_planet_positions(),
        astral_points=_astral_points(),
        houses=_houses(),
    )
    return {item.code: item for item in objects}


def test_contract_declares_required_enums_and_fields() -> None:
    """Le contrat expose les enums et champs requis par CS-217."""
    assert {item.value for item in ChartObjectType} == {
        "planet",
        "luminary",
        "astral_point",
        "angle",
        "house_cusp",
        "fixed_star",
        "arabic_part",
        "calculated_point",
    }
    assert {item.value for item in ChartObjectSourceType} == {
        "ephemeris",
        "house_system",
        "catalog",
        "derived",
        "user_option",
    }
    assert set(ChartObjectCapabilities.__dataclass_fields__) == {
        "supports_aspects",
        "supports_dignities",
        "supports_house_position",
        "supports_visibility",
        "supports_motion",
        "supports_interpretation",
        "supports_dominance",
        "supports_rulership",
        "supports_fixed_star_conjunction",
    }
    assert set(ChartObjectPayloads.__dataclass_fields__) >= {
        "motion",
        "visibility",
        "dignity",
        "dominance",
        "planetary_conditions",
        "fixed_star",
        "house_position",
        "rulership",
        "house_cusp",
        "angle",
    }


def test_builder_projects_planets_luminaries_points_angles_and_cusps() -> None:
    """La projection unifie les collections historiques sans les recalculer."""
    by_code = _objects_by_code()

    assert by_code["sun"].object_type == ChartObjectType.LUMINARY
    assert by_code["mars"].object_type == ChartObjectType.PLANET
    assert by_code["north_node"].object_type == ChartObjectType.ASTRAL_POINT
    assert by_code["south_node"].source.source_type == ChartObjectSourceType.DERIVED
    assert by_code["asc"].object_type == ChartObjectType.ANGLE
    assert by_code["asc"].payloads.angle is not None
    assert by_code["asc"].payloads.angle.associated_house == 1
    assert by_code["asc"].payloads.house_position is not None
    assert by_code["asc"].payloads.house_position.house_number == 1
    assert by_code["asc"].payloads.house_position.house_modality == "angular"
    assert by_code["mc"].payloads.angle is not None
    assert by_code["mc"].payloads.angle.associated_house == 10
    assert by_code["house_12_cusp"].object_type == ChartObjectType.HOUSE_CUSP
    assert by_code["house_12_cusp"].payloads.house_cusp is not None
    assert by_code["house_12_cusp"].payloads.house_cusp.house_number == 12


def test_objects_are_filterable_by_capabilities() -> None:
    """Les futurs calculateurs peuvent selectionner les objets par capacites."""
    objects = tuple(_objects_by_code().values())

    aspect_codes = {item.code for item in objects if item.capabilities.supports_aspects}
    house_position_codes = {
        item.code for item in objects if item.capabilities.supports_house_position
    }
    dignity_codes = {item.code for item in objects if item.capabilities.supports_dignities}
    dominance_codes = {item.code for item in objects if item.capabilities.supports_dominance}
    motion_codes = {item.code for item in objects if item.capabilities.supports_motion}

    assert {"sun", "mars", "north_node", "asc", "mc"} <= aspect_codes
    assert {"sun", "mars", "north_node", "house_1_cusp"} <= house_position_codes
    assert dignity_codes == {"sun", "mars"}
    assert dominance_codes == {"sun", "mars"}
    assert {item.code for item in objects if item.capabilities.supports_rulership} == {
        "sun",
        "mars",
    }
    assert motion_codes == set()
    assert all(
        item.payloads.house_position is not None
        for item in objects
        if item.capabilities.supports_house_position
    )


def test_builder_maps_advanced_motion_and_visibility_payloads() -> None:
    """La projection rattache les conditions avancees deja calculees aux planetes."""
    objects = build_chart_object_runtime_data(
        planet_positions=_planet_positions(),
        astral_points=_astral_points(),
        houses=_houses(),
        advanced_planetary_conditions=_advanced_conditions(),
    )
    by_code = {item.code: item for item in objects}

    assert by_code["mars"].capabilities.supports_motion is True
    assert by_code["mars"].payloads.motion is not None
    assert by_code["mars"].payloads.motion.direction is PlanetaryMotionDirection.RETROGRADE
    assert by_code["mars"].capabilities.supports_visibility is True
    assert by_code["mars"].payloads.visibility is not None
    assert by_code["mars"].payloads.visibility.visibility_key is PlanetVisibilityKey.INVISIBLE
    assert by_code["mars"].payloads.visibility.is_combust is True
    assert by_code["sun"].payloads.visibility is not None
    assert by_code["sun"].payloads.visibility.is_cazimi is None
    assert by_code["north_node"].capabilities.supports_motion is False
    assert by_code["north_node"].payloads.motion is None
    assert by_code["asc"].capabilities.supports_visibility is False
    assert by_code["asc"].payloads.visibility is None


def test_declared_payload_capability_requires_payload() -> None:
    """Une capacite annoncee sans payload explicite echoue immediatement."""
    with pytest.raises(ValueError, match="motion payload"):
        ChartObjectRuntimeData(
            code="broken",
            object_type=ChartObjectType.PLANET,
            display_name="Broken",
            longitude=None,
            latitude=None,
            zodiac_position=None,
            source=ChartObjectSourceRuntimeData(
                source_type=ChartObjectSourceType.EPHEMERIS,
                source_key="broken",
            ),
            capabilities=ChartObjectCapabilities(supports_motion=True),
            classifications=("planet",),
            payloads=ChartObjectPayloads(),
        )
    with pytest.raises(ValueError, match="visibility payload"):
        ChartObjectRuntimeData(
            code="broken",
            object_type=ChartObjectType.PLANET,
            display_name="Broken",
            longitude=None,
            latitude=None,
            zodiac_position=None,
            source=ChartObjectSourceRuntimeData(
                source_type=ChartObjectSourceType.EPHEMERIS,
                source_key="broken",
            ),
            capabilities=ChartObjectCapabilities(supports_visibility=True),
            classifications=("planet",),
            payloads=ChartObjectPayloads(),
        )
