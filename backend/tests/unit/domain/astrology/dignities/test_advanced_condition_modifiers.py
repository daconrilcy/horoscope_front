"""Tests des modificateurs accidentels issus des conditions avancees."""

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.dignities.advanced_condition_modifier_profiles import (
    ADVANCED_CONDITION_MODIFIER_PROFILES,
)
from app.domain.astrology.dignities.advanced_condition_modifiers import (
    calculate_advanced_condition_modifiers,
)
from app.domain.astrology.dignities.contracts import AccidentalDignityModifier
from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    ConditionSeverity,
    MoonPhaseCondition,
    MoonPhaseKey,
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
    WaxingWaningState,
)


def test_modifier_contract_is_immutable_with_required_fields() -> None:
    """Le contrat public du modificateur reste immutable et explicite."""
    modifier = AccidentalDignityModifier(
        key="cazimi_bonus",
        category="solar_condition",
        score_delta=5,
        reason="solar_proximity:cazimi",
        source="advanced_condition_modifier",
    )

    with pytest.raises(FrozenInstanceError):
        modifier.score_delta = 0  # type: ignore[misc]

    assert not hasattr(modifier, "__dict__")
    assert set(modifier.__dataclass_fields__) == {
        "key",
        "category",
        "score_delta",
        "reason",
        "source",
    }


def test_profiles_centralize_expected_deltas_and_categories() -> None:
    """Le profil V1 porte les deltas et categories sans constante dispersee."""
    expected = {
        "cazimi_bonus": (5, "solar_condition"),
        "combust_penalty": (-5, "solar_condition"),
        "under_beams_penalty": (-2, "solar_condition"),
        "retrograde_penalty": (-3, "motion_condition"),
        "stationary_bonus": (2, "motion_condition"),
        "very_fast_bonus": (1, "motion_condition"),
        "very_slow_penalty": (-1, "motion_condition"),
        "invisible_penalty": (-4, "visibility_condition"),
        "emerging_bonus": (2, "visibility_condition"),
        "oriental_superior_bonus": (1, "solar_phase_condition"),
        "occidental_superior_penalty": (-1, "solar_phase_condition"),
        "full_moon_bonus": (2, "lunar_condition"),
        "new_moon_penalty": (-2, "lunar_condition"),
    }

    observed = {
        key: (profile.score_delta, profile.category)
        for key, profile in ADVANCED_CONDITION_MODIFIER_PROFILES.items()
    }

    assert observed == expected


def test_cazimi_has_priority_over_combust_and_sun_has_no_combust_penalty() -> None:
    """La proximite solaire applique les cas exclusifs attendus."""
    cazimi = _bundle(
        "venus",
        solar_proximity=_solar_proximity("venus", SolarProximityConditionKey.CAZIMI),
    )
    combust_sun = _bundle(
        "sun",
        solar_proximity=_solar_proximity("sun", SolarProximityConditionKey.COMBUST),
    )
    combust_venus = _bundle(
        "venus",
        solar_proximity=_solar_proximity("venus", SolarProximityConditionKey.COMBUST),
    )

    assert _keys(calculate_advanced_condition_modifiers(bundle=cazimi, moon_phase=None)) == [
        "cazimi_bonus"
    ]
    assert calculate_advanced_condition_modifiers(bundle=combust_sun, moon_phase=None) == ()
    assert _keys(calculate_advanced_condition_modifiers(bundle=combust_venus, moon_phase=None)) == [
        "combust_penalty"
    ]


def test_under_beams_uses_solar_proximity_without_visibility_double_count() -> None:
    """Under beams vient de la proximite solaire et pas d'un second canal."""
    bundle = _bundle(
        "mercury",
        solar_proximity=_solar_proximity("mercury", SolarProximityConditionKey.UNDER_BEAMS),
        visibility=_visibility("mercury", PlanetVisibilityKey.UNDER_BEAMS),
    )

    modifiers = calculate_advanced_condition_modifiers(bundle=bundle, moon_phase=None)

    assert _keys(modifiers) == ["under_beams_penalty"]
    assert sum(modifier.score_delta for modifier in modifiers) == -2


def test_motion_modifiers_allow_stationary_retrograde_and_speed_extremes() -> None:
    """Le mouvement peut cumuler direction, stationnarite et vitesse."""
    bundle = _bundle(
        "saturn",
        motion=_motion(
            "saturn",
            direction=PlanetaryMotionDirection.RETROGRADE,
            speed_state=PlanetarySpeedState.VERY_SLOW,
            is_retrograde=True,
            is_stationary=True,
        ),
    )
    fast_bundle = _bundle(
        "mars",
        motion=_motion(
            "mars",
            direction=PlanetaryMotionDirection.DIRECT,
            speed_state=PlanetarySpeedState.VERY_FAST,
        ),
    )

    assert _keys(calculate_advanced_condition_modifiers(bundle=bundle, moon_phase=None)) == [
        "retrograde_penalty",
        "stationary_bonus",
        "very_slow_penalty",
    ]
    assert _keys(calculate_advanced_condition_modifiers(bundle=fast_bundle, moon_phase=None)) == [
        "very_fast_bonus"
    ]


def test_motion_modifiers_allow_stationary_direction_with_retrograde_flag() -> None:
    """Les flags de mouvement restent pris en compte quand la direction est stationnaire."""
    bundle = _bundle(
        "saturn",
        motion=_motion(
            "saturn",
            direction=PlanetaryMotionDirection.STATIONARY,
            speed_state=PlanetarySpeedState.VERY_SLOW,
            is_retrograde=True,
            is_stationary=True,
        ),
    )

    assert _keys(calculate_advanced_condition_modifiers(bundle=bundle, moon_phase=None)) == [
        "retrograde_penalty",
        "stationary_bonus",
        "very_slow_penalty",
    ]


def test_visibility_v1_only_scores_invisible_and_emerging() -> None:
    """La visibilite V1 limite les deltas aux deux etats prevus."""
    invisible = _bundle("mars", visibility=_visibility("mars", PlanetVisibilityKey.INVISIBLE))
    emerging = _bundle("jupiter", visibility=_visibility("jupiter", PlanetVisibilityKey.EMERGING))
    visible = _bundle("venus", visibility=_visibility("venus", PlanetVisibilityKey.VISIBLE))

    assert _keys(calculate_advanced_condition_modifiers(bundle=invisible, moon_phase=None)) == [
        "invisible_penalty"
    ]
    assert _keys(calculate_advanced_condition_modifiers(bundle=emerging, moon_phase=None)) == [
        "emerging_bonus"
    ]
    assert calculate_advanced_condition_modifiers(bundle=visible, moon_phase=None) == ()


def test_solar_phase_v1_scores_only_superior_planets() -> None:
    """La phase solaire V1 est bornee aux planetes superieures."""
    oriental_mars = _bundle(
        "mars",
        solar_phase_relation=_solar_phase("mars", SolarPhaseRelationKey.ORIENTAL),
    )
    occidental_jupiter = _bundle(
        "jupiter",
        solar_phase_relation=_solar_phase("jupiter", SolarPhaseRelationKey.OCCIDENTAL),
    )
    oriental_venus = _bundle(
        "venus",
        solar_phase_relation=_solar_phase("venus", SolarPhaseRelationKey.ORIENTAL),
    )

    assert _keys(calculate_advanced_condition_modifiers(bundle=oriental_mars, moon_phase=None)) == [
        "oriental_superior_bonus"
    ]
    assert _keys(
        calculate_advanced_condition_modifiers(bundle=occidental_jupiter, moon_phase=None)
    ) == ["occidental_superior_penalty"]
    assert calculate_advanced_condition_modifiers(bundle=oriental_venus, moon_phase=None) == ()


def test_lunar_phase_scores_only_moon_and_tolerates_partial_conditions() -> None:
    """La phase lunaire globale ne touche que la Lune et accepte les None."""
    moon = _bundle("moon")
    venus = _bundle("venus")
    full_moon = _moon_phase(MoonPhaseKey.FULL_MOON)
    new_moon = _moon_phase(MoonPhaseKey.NEW_MOON)

    assert _keys(calculate_advanced_condition_modifiers(bundle=moon, moon_phase=full_moon)) == [
        "full_moon_bonus"
    ]
    assert _keys(calculate_advanced_condition_modifiers(bundle=moon, moon_phase=new_moon)) == [
        "new_moon_penalty"
    ]
    assert calculate_advanced_condition_modifiers(bundle=venus, moon_phase=full_moon) == ()
    assert calculate_advanced_condition_modifiers(bundle=moon, moon_phase=None) == ()
    assert calculate_advanced_condition_modifiers(bundle=_bundle("mars"), moon_phase=None) == ()


def _keys(modifiers: tuple[AccidentalDignityModifier, ...]) -> list[str]:
    """Retourne les cles de modificateurs dans l'ordre calcule."""
    return [modifier.key for modifier in modifiers]


def _bundle(
    planet_key: str,
    *,
    solar_proximity: SolarProximityCondition | None = None,
    motion: PlanetaryMotionCondition | None = None,
    visibility: PlanetVisibilityCondition | None = None,
    solar_phase_relation: PlanetarySolarPhaseRelation | None = None,
) -> PlanetaryConditionsBundle:
    """Construit un bundle partiel pour les tests du moteur."""
    return PlanetaryConditionsBundle(
        planet_key=planet_key,
        solar_proximity=solar_proximity,
        motion=motion,
        visibility=visibility,
        solar_phase_relation=solar_phase_relation,
    )


def _solar_proximity(
    planet_key: str,
    condition_key: SolarProximityConditionKey,
    *,
    is_active: bool = True,
) -> SolarProximityCondition:
    """Construit une proximite solaire factuelle deja calculee."""
    return SolarProximityCondition(
        planet_key=planet_key,
        condition_key=condition_key,
        sun_distance_deg=1.0,
        orb_deg=1.0,
        severity=ConditionSeverity.MAJOR,
        is_active=is_active,
    )


def _motion(
    planet_key: str,
    *,
    direction: PlanetaryMotionDirection,
    speed_state: PlanetarySpeedState,
    is_retrograde: bool = False,
    is_stationary: bool = False,
) -> PlanetaryMotionCondition:
    """Construit un mouvement planetaire factuel deja calcule."""
    return PlanetaryMotionCondition(
        planet_key=planet_key,
        speed_deg_per_day=-0.1 if is_retrograde else 0.1,
        absolute_speed_deg_per_day=0.1,
        direction=direction,
        speed_state=speed_state,
        is_retrograde=is_retrograde,
        is_stationary=is_stationary,
        normalized_speed_ratio=0.1,
    )


def _visibility(
    planet_key: str,
    visibility_key: PlanetVisibilityKey,
) -> PlanetVisibilityCondition:
    """Construit une visibilite factuelle deja calculee."""
    return PlanetVisibilityCondition(
        planet_key=planet_key,
        visibility_key=visibility_key,
        is_visible=visibility_key is PlanetVisibilityKey.VISIBLE,
        confidence=ConditionConfidence.HIGH,
        reason="test_fact",
    )


def _solar_phase(
    planet_key: str,
    relation_key: SolarPhaseRelationKey,
) -> PlanetarySolarPhaseRelation:
    """Construit une relation solaire factuelle deja calculee."""
    return PlanetarySolarPhaseRelation(
        planet_key=planet_key,
        relation_key=relation_key,
        angular_distance_deg=80.0,
        is_oriental=relation_key is SolarPhaseRelationKey.ORIENTAL,
        is_occidental=relation_key is SolarPhaseRelationKey.OCCIDENTAL,
    )


def _moon_phase(phase_key: MoonPhaseKey) -> MoonPhaseCondition:
    """Construit une phase lunaire globale deja calculee."""
    return MoonPhaseCondition(
        phase_key=phase_key,
        sun_moon_angle_deg=180.0,
        illumination_ratio=1.0,
        waxing_or_waning=WaxingWaningState.EXACT,
        phase_index=4,
    )
