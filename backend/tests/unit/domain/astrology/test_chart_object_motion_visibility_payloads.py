"""Tests des payloads motion et visibilite des objets runtime."""

from __future__ import annotations

import pytest

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.natal_calculation import PlanetPosition
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
    ChartObjectMotionPayload,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    ChartObjectVisibilityPayload,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData


def _planet_position(planet_code: str = "mars") -> PlanetPosition:
    """Construit une position planetaire minimale pour le builder runtime."""
    return PlanetPosition(
        planet_code=planet_code,
        longitude=122.0,
        sign_code="leo",
        house_number=11,
        speed_longitude=-0.2,
        is_retrograde=True,
    )


def _houses() -> tuple[HouseRuntimeData, ...]:
    """Construit les maisons necessaires a la projection chart-object."""
    return tuple(
        HouseRuntimeData(number=number, cusp_longitude=float((number - 1) * 30))
        for number in range(1, 13)
    )


def _motion_condition(
    direction: PlanetaryMotionDirection,
) -> PlanetaryMotionCondition:
    """Cree une condition de mouvement deja calculee."""
    return PlanetaryMotionCondition(
        planet_key="mars",
        speed_deg_per_day=-0.2
        if direction is PlanetaryMotionDirection.RETROGRADE
        else 0.0
        if direction is PlanetaryMotionDirection.STATIONARY
        else 0.5,
        absolute_speed_deg_per_day=0.2
        if direction is PlanetaryMotionDirection.RETROGRADE
        else 0.0
        if direction is PlanetaryMotionDirection.STATIONARY
        else 0.5,
        direction=direction,
        speed_state=PlanetarySpeedState.SLOW,
        is_retrograde=direction is PlanetaryMotionDirection.RETROGRADE,
        is_stationary=direction is PlanetaryMotionDirection.STATIONARY,
        normalized_speed_ratio=0.5,
    )


def _bundle(
    *,
    motion: PlanetaryMotionCondition | None = None,
    proximity_key: SolarProximityConditionKey = SolarProximityConditionKey.COMBUST,
    visibility_key: PlanetVisibilityKey = PlanetVisibilityKey.INVISIBLE,
) -> PlanetaryConditionsBundle:
    """Assemble un bundle de conditions avancees sans recalcul."""
    return PlanetaryConditionsBundle(
        planet_key="mars",
        motion=motion,
        solar_proximity=SolarProximityCondition(
            planet_key="mars",
            condition_key=proximity_key,
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
            visibility_key=visibility_key,
            is_visible=False,
            confidence=ConditionConfidence.HIGH,
            reason="combust",
        ),
    )


def _chart_object(
    *,
    capabilities: ChartObjectCapabilities,
    payloads: ChartObjectPayloads,
) -> ChartObjectRuntimeData:
    """Construit un objet runtime minimal pour tester le validateur."""
    return ChartObjectRuntimeData(
        code="mars",
        object_type=ChartObjectType.PLANET,
        display_name="Mars",
        longitude=None,
        latitude=None,
        zodiac_position=None,
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key="mars",
        ),
        capabilities=capabilities,
        classifications=("planet",),
        payloads=payloads,
    )


@pytest.mark.parametrize(
    ("direction", "expected_direct", "expected_retrograde", "expected_stationary"),
    (
        (PlanetaryMotionDirection.DIRECT, True, False, False),
        (PlanetaryMotionDirection.RETROGRADE, False, True, False),
        (PlanetaryMotionDirection.STATIONARY, False, False, True),
    ),
)
def test_motion_payload_maps_precomputed_condition(
    direction: PlanetaryMotionDirection,
    expected_direct: bool,
    expected_retrograde: bool,
    expected_stationary: bool,
) -> None:
    """Le payload motion reprend la condition canonique sans la recalculer."""
    result = build_chart_object_runtime_data(
        planet_positions=(_planet_position(),),
        astral_points=(),
        houses=_houses(),
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={"mars": _bundle(motion=_motion_condition(direction))}
        ),
    )

    motion = result[0].payloads.motion

    assert motion is not None
    assert result[0].capabilities.supports_motion is True
    assert motion.direction is direction
    assert motion.is_direct is expected_direct
    assert motion.is_retrograde is expected_retrograde
    assert motion.is_stationary is expected_stationary
    assert motion.source == "planetary_conditions.motion"


@pytest.mark.parametrize(
    ("proximity_key", "visibility_key", "expected_flags"),
    (
        (
            SolarProximityConditionKey.CAZIMI,
            PlanetVisibilityKey.CONJUNCT_SOLAR,
            (True, False, False),
        ),
        (
            SolarProximityConditionKey.COMBUST,
            PlanetVisibilityKey.INVISIBLE,
            (False, True, False),
        ),
        (
            SolarProximityConditionKey.UNDER_BEAMS,
            PlanetVisibilityKey.UNDER_BEAMS,
            (False, False, True),
        ),
    ),
)
def test_visibility_payload_maps_precomputed_solar_facts(
    proximity_key: SolarProximityConditionKey,
    visibility_key: PlanetVisibilityKey,
    expected_flags: tuple[bool, bool, bool],
) -> None:
    """Le payload visibility reprend les faits solaires existants."""
    result = build_chart_object_runtime_data(
        planet_positions=(_planet_position(),),
        astral_points=(),
        houses=_houses(),
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={
                "mars": _bundle(
                    proximity_key=proximity_key,
                    visibility_key=visibility_key,
                )
            }
        ),
    )

    visibility = result[0].payloads.visibility

    assert visibility is not None
    assert result[0].capabilities.supports_visibility is True
    assert visibility.visibility_key is visibility_key
    assert visibility.is_visible is False
    assert visibility.solar_proximity_key is proximity_key
    assert (
        visibility.is_cazimi,
        visibility.is_combust,
        visibility.is_under_beams,
    ) == expected_flags
    assert visibility.is_occidental is True


def test_sun_visibility_payload_keeps_solar_flags_non_applicable() -> None:
    """Le Soleil ne porte pas de flags cazimi combustion under beams sur lui-meme."""
    result = build_chart_object_runtime_data(
        planet_positions=(_planet_position("sun"),),
        astral_points=(),
        houses=_houses(),
        advanced_planetary_conditions=AdvancedPlanetaryConditionsResult(
            conditions_by_planet={
                "sun": PlanetaryConditionsBundle(
                    planet_key="sun",
                    visibility=PlanetVisibilityCondition(
                        planet_key="sun",
                        visibility_key=PlanetVisibilityKey.VISIBLE,
                        is_visible=True,
                        confidence=ConditionConfidence.HIGH,
                        reason="sun_visible",
                    ),
                    solar_proximity=SolarProximityCondition(
                        planet_key="sun",
                        condition_key=SolarProximityConditionKey.NONE,
                        sun_distance_deg=0.0,
                        orb_deg=None,
                        severity=ConditionSeverity.NONE,
                        is_active=False,
                    ),
                    solar_phase_relation=PlanetarySolarPhaseRelation(
                        planet_key="sun",
                        relation_key=SolarPhaseRelationKey.CONJUNCT_SOLAR,
                        angular_distance_deg=0.0,
                        is_oriental=None,
                        is_occidental=None,
                    ),
                )
            }
        ),
    )

    visibility = result[0].payloads.visibility

    assert visibility is not None
    assert visibility.visibility_key is PlanetVisibilityKey.VISIBLE
    assert visibility.solar_separation_deg is None
    assert visibility.solar_proximity_key is None
    assert visibility.is_cazimi is None
    assert visibility.is_combust is None
    assert visibility.is_under_beams is None
    assert visibility.is_oriental is None
    assert visibility.is_occidental is None


def test_runtime_validator_rejects_payload_without_capability() -> None:
    """Un payload present sans capacite annoncee est incoherent."""
    with pytest.raises(ValueError, match="motion capability"):
        _chart_object(
            capabilities=ChartObjectCapabilities(),
            payloads=ChartObjectPayloads(
                motion=ChartObjectMotionPayload(
                    speed_longitude=1.0,
                    is_retrograde=False,
                    direction=PlanetaryMotionDirection.DIRECT,
                    is_direct=True,
                    is_stationary=False,
                    source="planetary_conditions.motion",
                )
            ),
        )

    with pytest.raises(ValueError, match="visibility capability"):
        _chart_object(
            capabilities=ChartObjectCapabilities(),
            payloads=ChartObjectPayloads(
                visibility=ChartObjectVisibilityPayload(
                    visibility_key=PlanetVisibilityKey.VISIBLE,
                    is_visible=True,
                    confidence=ConditionConfidence.HIGH,
                    reason="outside_visibility_restrictions",
                )
            ),
        )
