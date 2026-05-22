"""Tests des contrats purs de conditions planetaires avancees."""

from dataclasses import FrozenInstanceError, fields, is_dataclass
from math import inf, nan
from types import MappingProxyType
from typing import Any, get_args, get_origin, get_type_hints

import pytest

from app.domain.astrology.planetary_conditions import (
    AdvancedPlanetaryConditionsResult,
    ConditionConfidence,
    ConditionSeverity,
    MoonPhaseCondition,
    MoonPhaseKey,
    PlanetaryConditionFamily,
    PlanetaryConditionsBundle,
    PlanetaryConditionSignal,
    PlanetaryMotionCondition,
    PlanetaryMotionDirection,
    PlanetaryMotionProfile,
    PlanetarySolarPhaseRelation,
    PlanetarySpeedState,
    PlanetVisibilityCondition,
    PlanetVisibilityKey,
    PlanetVisibilityThresholds,
    SolarPhaseRelationKey,
    SolarPhaseRelationThresholds,
    SolarProximityCondition,
    SolarProximityConditionKey,
    SolarProximityThresholds,
    WaxingWaningState,
)

PUBLIC_CONTRACTS = (
    SolarProximityThresholds,
    SolarPhaseRelationThresholds,
    SolarProximityCondition,
    PlanetarySolarPhaseRelation,
    PlanetaryMotionCondition,
    PlanetaryMotionProfile,
    PlanetVisibilityThresholds,
    PlanetVisibilityCondition,
    MoonPhaseCondition,
    PlanetaryConditionSignal,
    PlanetaryConditionsBundle,
    AdvancedPlanetaryConditionsResult,
)


def test_public_enums_expose_stable_snake_case_values() -> None:
    """Les valeurs publiques des enums restent stables et explicites."""
    assert [item.value for item in ConditionSeverity] == [
        "none",
        "minor",
        "moderate",
        "major",
        "extreme",
    ]
    assert [item.value for item in ConditionConfidence] == [
        "unknown",
        "low",
        "medium",
        "high",
        "exact",
    ]
    assert [item.value for item in SolarProximityConditionKey] == [
        "none",
        "cazimi",
        "combust",
        "under_beams",
    ]
    assert [item.value for item in SolarPhaseRelationKey] == [
        "unknown",
        "oriental",
        "occidental",
        "conjunct_solar",
    ]
    assert [item.value for item in PlanetaryMotionDirection] == [
        "direct",
        "retrograde",
        "stationary",
        "unknown",
    ]
    assert [item.value for item in PlanetarySpeedState] == [
        "unknown",
        "very_slow",
        "slow",
        "normal",
        "fast",
        "very_fast",
    ]
    assert [item.value for item in PlanetVisibilityKey] == [
        "unknown",
        "visible",
        "conjunct_solar",
        "invisible",
        "under_beams",
        "emerging",
        "heliacal_rising",
        "heliacal_setting",
    ]
    assert [item.value for item in MoonPhaseKey] == [
        "unknown",
        "new_moon",
        "waxing_crescent",
        "first_quarter",
        "waxing_gibbous",
        "full_moon",
        "waning_gibbous",
        "last_quarter",
        "waning_crescent",
        "balsamic",
    ]
    assert [item.value for item in WaxingWaningState] == [
        "unknown",
        "waxing",
        "waning",
        "exact",
    ]
    assert [item.value for item in PlanetaryConditionFamily] == [
        "solar_proximity",
        "solar_phase",
        "motion",
        "visibility",
        "lunar_phase",
    ]


def test_all_public_contracts_are_importable_frozen_and_slotted() -> None:
    """Tous les contrats publics suivent le standard domaine immuable."""
    for contract in PUBLIC_CONTRACTS:
        assert is_dataclass(contract)
        assert contract.__dataclass_params__.frozen is True
        assert hasattr(contract, "__slots__")

    proximity = _solar_proximity("venus")
    with pytest.raises(FrozenInstanceError):
        proximity.planet_key = "mars"  # type: ignore[misc]
    assert not hasattr(proximity, "__dict__")


def test_solar_proximity_thresholds_expose_defaults_and_validate_order() -> None:
    """Les seuils solaires restent explicites, immuables et ordonnes."""
    thresholds = SolarProximityThresholds()

    assert thresholds.cazimi_max_distance_deg == 17.0 / 60.0
    assert thresholds.combust_max_distance_deg == 8.5
    assert thresholds.under_beams_max_distance_deg == 15.0
    with pytest.raises(FrozenInstanceError):
        thresholds.combust_max_distance_deg = 7.0  # type: ignore[misc]
    with pytest.raises(ValueError, match="0 <= cazimi <= combust <= under_beams"):
        SolarProximityThresholds(
            cazimi_max_distance_deg=9.0,
            combust_max_distance_deg=8.5,
            under_beams_max_distance_deg=15.0,
        )


def test_solar_phase_relation_thresholds_expose_default_and_validate_bounds() -> None:
    """La tolerance de relation solaire reste bornee et immuable."""
    thresholds = SolarPhaseRelationThresholds()

    assert thresholds.conjunction_tolerance_deg == 0.5
    with pytest.raises(FrozenInstanceError):
        thresholds.conjunction_tolerance_deg = 1.0  # type: ignore[misc]
    with pytest.raises(ValueError, match="greater than or equal to zero"):
        SolarPhaseRelationThresholds(conjunction_tolerance_deg=-0.1)
    with pytest.raises(ValueError, match="must be finite"):
        SolarPhaseRelationThresholds(conjunction_tolerance_deg=nan)
    with pytest.raises(ValueError, match="less than 180"):
        SolarPhaseRelationThresholds(conjunction_tolerance_deg=180.0)
    with pytest.raises(ValueError, match="less than 180"):
        SolarPhaseRelationThresholds(conjunction_tolerance_deg=180.1)


def test_planet_visibility_thresholds_expose_defaults_and_validate_order() -> None:
    """Les seuils de visibilite restent finis, immuables et ordonnes."""
    thresholds = PlanetVisibilityThresholds()

    assert thresholds.conjunction_tolerance_deg == 0.5
    assert thresholds.under_beams_limit_deg == 15.0
    assert thresholds.emerging_limit_deg == 18.0
    with pytest.raises(FrozenInstanceError):
        thresholds.emerging_limit_deg = 20.0  # type: ignore[misc]
    with pytest.raises(ValueError, match="must be finite"):
        PlanetVisibilityThresholds(conjunction_tolerance_deg=nan)
    with pytest.raises(ValueError, match="0 <= conjunction <= under_beams <= emerging"):
        PlanetVisibilityThresholds(
            conjunction_tolerance_deg=0.5,
            under_beams_limit_deg=19.0,
            emerging_limit_deg=18.0,
        )


def test_planetary_motion_profile_exposes_defaults_and_validates_thresholds() -> None:
    """Le profil de mouvement reste immuable et valide ses seuils configurables."""
    profile = PlanetaryMotionProfile(
        planet_key="mars",
        mean_speed_deg_per_day=0.524,
        stationary_threshold_abs=0.0262,
    )

    assert profile.planet_key == "mars"
    assert profile.mean_speed_deg_per_day == 0.524
    assert profile.stationary_threshold_abs == 0.0262
    assert profile.very_slow_ratio_threshold == 0.4
    assert profile.slow_ratio_threshold == 0.8
    assert profile.fast_ratio_threshold == 1.2
    assert profile.very_fast_ratio_threshold == 1.6
    with pytest.raises(FrozenInstanceError):
        profile.mean_speed_deg_per_day = 0.1  # type: ignore[misc]
    with pytest.raises(ValueError, match="stationary threshold"):
        PlanetaryMotionProfile(
            planet_key="mars",
            mean_speed_deg_per_day=0.524,
            stationary_threshold_abs=-0.1,
        )
    with pytest.raises(ValueError, match="mean speed must be finite"):
        PlanetaryMotionProfile(
            planet_key="mars",
            mean_speed_deg_per_day=nan,
            stationary_threshold_abs=0.0262,
        )
    with pytest.raises(ValueError, match="stationary threshold must be finite"):
        PlanetaryMotionProfile(
            planet_key="mars",
            mean_speed_deg_per_day=0.524,
            stationary_threshold_abs=inf,
        )
    with pytest.raises(ValueError, match="speed ratio thresholds must be finite"):
        PlanetaryMotionProfile(
            planet_key="mars",
            mean_speed_deg_per_day=0.524,
            stationary_threshold_abs=0.0262,
            very_slow_ratio_threshold=nan,
        )
    with pytest.raises(ValueError, match="0 <= very_slow <= slow <= fast <= very_fast"):
        PlanetaryMotionProfile(
            planet_key="mars",
            mean_speed_deg_per_day=0.524,
            stationary_threshold_abs=0.0262,
            very_slow_ratio_threshold=0.9,
            slow_ratio_threshold=0.8,
        )


def test_planetary_motion_profile_allows_invalid_mean_speed_for_unknown_state() -> None:
    """Une vitesse moyenne invalide reste un fait exploitable par le calculateur."""
    profile = PlanetaryMotionProfile(
        planet_key="test",
        mean_speed_deg_per_day=0.0,
        stationary_threshold_abs=0.0,
    )

    assert profile.mean_speed_deg_per_day == 0.0


def test_contracts_can_be_instantiated_with_required_fields() -> None:
    """Chaque contrat accepte son payload factuel minimal sans calcul."""
    solar_phase = PlanetarySolarPhaseRelation(
        planet_key="venus",
        relation_key=SolarPhaseRelationKey.ORIENTAL,
        angular_distance_deg=34.2,
        is_oriental=True,
        is_occidental=False,
    )
    motion = PlanetaryMotionCondition(
        planet_key="mars",
        speed_deg_per_day=-0.3,
        absolute_speed_deg_per_day=0.3,
        direction=PlanetaryMotionDirection.RETROGRADE,
        speed_state=PlanetarySpeedState.SLOW,
        is_retrograde=True,
        is_stationary=False,
        normalized_speed_ratio=0.42,
    )
    visibility = PlanetVisibilityCondition(
        planet_key="mercury",
        visibility_key=PlanetVisibilityKey.HELIACAL_RISING,
        is_visible=True,
        confidence=ConditionConfidence.HIGH,
        reason="heliacal visibility fact",
    )
    moon_phase = MoonPhaseCondition(
        phase_key=MoonPhaseKey.FULL_MOON,
        sun_moon_angle_deg=180,
        illumination_ratio=1,
        waxing_or_waning=WaxingWaningState.EXACT,
        phase_index=5,
    )

    assert solar_phase.relation_key is SolarPhaseRelationKey.ORIENTAL
    assert motion.direction is PlanetaryMotionDirection.RETROGRADE
    assert visibility.confidence is ConditionConfidence.HIGH
    assert moon_phase.phase_key is MoonPhaseKey.FULL_MOON


def test_bundle_accepts_partial_conditions_without_false_calculation() -> None:
    """Un bundle peut exposer uniquement les faits disponibles pour une planete."""
    signal = _signal("venus")
    bundle = PlanetaryConditionsBundle(
        planet_key="venus",
        solar_proximity=_solar_proximity("venus"),
        signals=(signal,),
    )

    assert bundle.motion is None
    assert bundle.visibility is None
    assert bundle.signals == (signal,)
    assert isinstance(bundle.signals, tuple)


def test_result_accepts_multiple_planets_and_global_moon_phase() -> None:
    """Le resultat global regroupe plusieurs planetes sans ordre mutable."""
    venus_signal = _signal("venus")
    result = AdvancedPlanetaryConditionsResult(
        conditions_by_planet={
            "venus": PlanetaryConditionsBundle(planet_key="venus", signals=(venus_signal,)),
            "mars": PlanetaryConditionsBundle(planet_key="mars"),
        },
        moon_phase=MoonPhaseCondition(
            phase_key=MoonPhaseKey.WAXING_GIBBOUS,
            sun_moon_angle_deg=132.4,
            illumination_ratio=0.81,
            waxing_or_waning=WaxingWaningState.WAXING,
            phase_index=4,
        ),
        signals=(venus_signal,),
    )

    assert tuple(result.conditions_by_planet) == ("venus", "mars")
    assert result.moon_phase is not None
    assert result.signals == (venus_signal,)


def test_metadata_defaults_to_read_only_mapping() -> None:
    """La metadata technique ne fournit pas de dictionnaire mutable par defaut."""
    signal = _signal("saturn")
    explicit_signal = PlanetaryConditionSignal(
        planet_key="jupiter",
        condition_key="visible",
        condition_family=PlanetaryConditionFamily.VISIBILITY,
        severity=ConditionSeverity.MINOR,
        confidence=ConditionConfidence.HIGH,
        is_active=True,
        value=None,
        unit=None,
        metadata={"source": "test"},
    )

    assert isinstance(signal.metadata, MappingProxyType)
    assert isinstance(explicit_signal.metadata, MappingProxyType)
    with pytest.raises(TypeError):
        signal.metadata["source"] = "test"  # type: ignore[index]
    with pytest.raises(TypeError):
        explicit_signal.metadata["source"] = "changed"  # type: ignore[index]


def test_result_conditions_mapping_is_read_only() -> None:
    """Le mapping global ne reste pas mutable apres construction."""
    result = AdvancedPlanetaryConditionsResult(
        conditions_by_planet={"venus": PlanetaryConditionsBundle(planet_key="venus")}
    )

    assert isinstance(result.conditions_by_planet, MappingProxyType)
    with pytest.raises(TypeError):
        result.conditions_by_planet["mars"] = PlanetaryConditionsBundle(  # type: ignore[index]
            planet_key="mars"
        )


def test_signal_collections_are_normalized_to_tuples() -> None:
    """Les signaux recus sous forme mutable sont exposes en tuples."""
    signal = _signal("venus")
    mutable_signals = [signal]

    bundle = PlanetaryConditionsBundle(
        planet_key="venus",
        signals=mutable_signals,  # type: ignore[arg-type]
    )
    result = AdvancedPlanetaryConditionsResult(
        conditions_by_planet={"venus": bundle},
        signals=mutable_signals,  # type: ignore[arg-type]
    )
    mutable_signals.append(_signal("mars"))

    assert bundle.signals == (signal,)
    assert result.signals == (signal,)
    assert isinstance(bundle.signals, tuple)
    assert isinstance(result.signals, tuple)


def test_public_annotations_do_not_use_free_any_or_mutable_lists() -> None:
    """Les annotations publiques restent strictes et sans collections libres."""
    for contract in PUBLIC_CONTRACTS:
        type_hints = get_type_hints(contract)
        for field in fields(contract):
            annotation = type_hints[field.name]
            assert not _contains_any(annotation)
            assert not _contains_list(annotation)


def _solar_proximity(planet_key: str) -> SolarProximityCondition:
    """Construit une proximite solaire minimale pour les tests."""
    return SolarProximityCondition(
        planet_key=planet_key,
        condition_key=SolarProximityConditionKey.CAZIMI,
        sun_distance_deg=0.1,
        orb_deg=0.3,
        severity=ConditionSeverity.EXTREME,
        is_active=True,
    )


def _signal(planet_key: str) -> PlanetaryConditionSignal:
    """Construit un signal technique minimal pour les tests."""
    return PlanetaryConditionSignal(
        planet_key=planet_key,
        condition_key="cazimi",
        condition_family=PlanetaryConditionFamily.SOLAR_PROXIMITY,
        severity=ConditionSeverity.EXTREME,
        confidence=ConditionConfidence.EXACT,
        is_active=True,
        value=0.1,
        unit="degree",
    )


def _contains_any(annotation: object) -> bool:
    """Detecte recursivement l'usage public d'annotations libres."""
    if annotation is Any:
        return True
    return any(_contains_any(argument) for argument in get_args(annotation))


def _contains_list(annotation: object) -> bool:
    """Detecte recursivement les listes mutables dans les contrats publics."""
    if get_origin(annotation) is list or annotation is list:
        return True
    return any(_contains_list(argument) for argument in get_args(annotation))
