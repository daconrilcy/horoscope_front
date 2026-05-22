"""Tests des profils symboliques des conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.interpretation.advanced_conditions import (
    ADVANCED_CONDITION_PROFILE_CATALOG,
    AdvancedConditionInterpretationProfile,
    InterpretationIntensity,
    InterpretationPolarity,
    resolve_advanced_condition_profiles,
)
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


def test_profile_contract_is_immutable_and_uses_required_fields() -> None:
    """Le contrat de profil reste explicite, court et immutable."""
    profile = AdvancedConditionInterpretationProfile(
        condition_key="combust",
        polarity=InterpretationPolarity.NEGATIVE,
        intensity=InterpretationIntensity.HIGH,
        keywords=("hidden",),
        themes=("solar domination",),
        manifestations=("low visibility",),
        psychological_axes=("pressure",),
        behavioral_axes=("restraint",),
    )

    with pytest.raises(FrozenInstanceError):
        profile.condition_key = "cazimi"  # type: ignore[misc]

    assert not hasattr(profile, "__dict__")
    assert set(profile.__dataclass_fields__) == {
        "condition_key",
        "planet_key",
        "tradition_key",
        "polarity",
        "intensity",
        "keywords",
        "themes",
        "manifestations",
        "psychological_axes",
        "behavioral_axes",
        "notes",
    }


def test_profile_contract_rejects_invalid_optional_notes() -> None:
    """Les notes optionnelles restent des fragments courts quand elles existent."""
    with pytest.raises(ValueError, match="notes"):
        AdvancedConditionInterpretationProfile(
            condition_key="combust",
            polarity=InterpretationPolarity.NEGATIVE,
            intensity=InterpretationIntensity.HIGH,
            keywords=("hidden",),
            themes=("solar domination",),
            manifestations=("low visibility",),
            psychological_axes=("pressure",),
            behavioral_axes=("restraint",),
            notes=("",),
        )

    with pytest.raises(ValueError, match="notes"):
        AdvancedConditionInterpretationProfile(
            condition_key="combust",
            polarity=InterpretationPolarity.NEGATIVE,
            intensity=InterpretationIntensity.HIGH,
            keywords=("hidden",),
            themes=("solar domination",),
            manifestations=("low visibility",),
            psychological_axes=("pressure",),
            behavioral_axes=("restraint",),
            notes=("x" * 41,),
        )


def test_catalog_contains_required_minimal_condition_keys_and_fragments() -> None:
    """Le catalogue couvre les cles minimales avec des fragments bornes."""
    expected = {
        "combust",
        "cazimi",
        "retrograde",
        "stationary",
        "under_beams",
        "invisible",
        "emerging",
        "oriental",
        "occidental",
        "full_moon",
        "new_moon",
    }

    observed = {profile.condition_key for profile in ADVANCED_CONDITION_PROFILE_CATALOG}
    assert expected <= observed
    for profile in ADVANCED_CONDITION_PROFILE_CATALOG:
        fragments = (
            *profile.keywords,
            *profile.themes,
            *profile.manifestations,
            *profile.psychological_axes,
            *profile.behavioral_axes,
            *profile.notes,
        )
        assert all(0 < len(fragment) <= 40 for fragment in fragments)


def test_catalog_keywords_cover_combust_and_retrograde_contracts() -> None:
    """Les mots-cles requis par le brief restent portes par les profils generiques."""
    combust = _profiles_for("combust")[0]
    cazimi = _profiles_for("cazimi")[0]
    retrograde = _profiles_for("retrograde")[0]
    stationary = _profiles_for("stationary")[0]
    emerging = _profiles_for("emerging")[0]
    full_moon = _profiles_for("full_moon")[0]
    new_moon = _profiles_for("new_moon")[0]

    assert {"hidden", "burned", "overpowered"} <= set(combust.keywords)
    assert {"empowered", "protected", "purified"} <= set(cazimi.keywords)
    assert {"internalized", "revisiting", "reprocessing"} <= set(retrograde.keywords)
    assert {"amplified", "concentrated", "blocked momentum"} <= set(stationary.keywords)
    assert {"reappearing", "awakening", "returning visibility"} <= set(emerging.keywords)
    assert {"culmination", "awareness", "illumination"} <= set(full_moon.keywords)
    assert {"seed", "beginning", "internalization"} <= set(new_moon.keywords)


def test_resolution_prefers_planet_tradition_then_planet_then_tradition_then_global() -> None:
    """La priorite de resolution ne melange pas les niveaux disponibles."""
    mercury_combust = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "mercury",
            solar_proximity=_solar_proximity("mercury", SolarProximityConditionKey.COMBUST),
        ),
        moon_phase=None,
        tradition_key="medieval",
    )
    mars_retrograde = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "mars",
            motion=_motion("mars", PlanetaryMotionDirection.RETROGRADE),
        ),
        moon_phase=None,
        tradition_key="medieval",
    )
    venus_retrograde = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "venus",
            motion=_motion("venus", PlanetaryMotionDirection.RETROGRADE),
        ),
        moon_phase=None,
    )

    assert [(profile.planet_key, profile.tradition_key) for profile in mercury_combust] == [
        ("mercury", "medieval")
    ]
    assert [profile.tradition_key for profile in mars_retrograde] == ["medieval"]
    assert [profile.tradition_key for profile in venus_retrograde] == [None]


def test_resolution_collects_multiple_families_and_deduplicates_under_beams() -> None:
    """Une planete peut exposer plusieurs profils sans doublonner une cle."""
    profiles = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "venus",
            solar_proximity=_solar_proximity("venus", SolarProximityConditionKey.UNDER_BEAMS),
            motion=_motion("venus", PlanetaryMotionDirection.STATIONARY),
            visibility=_visibility("venus", PlanetVisibilityKey.UNDER_BEAMS),
            solar_phase_relation=_solar_phase("venus", SolarPhaseRelationKey.OCCIDENTAL),
        ),
        moon_phase=None,
    )

    assert [profile.condition_key for profile in profiles] == [
        "under_beams",
        "stationary",
        "occidental",
    ]


def test_resolution_tolerates_absent_and_unsupported_conditions() -> None:
    """Les faits absents ou non requis ne produisent ni erreur ni profil."""
    profiles = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "venus",
            solar_proximity=_solar_proximity(
                "venus",
                SolarProximityConditionKey.NONE,
                is_active=False,
            ),
            motion=_motion("venus", PlanetaryMotionDirection.DIRECT),
            visibility=_visibility("venus", PlanetVisibilityKey.VISIBLE),
            solar_phase_relation=_solar_phase("venus", SolarPhaseRelationKey.CONJUNCT_SOLAR),
        ),
        moon_phase=_moon_phase(MoonPhaseKey.FULL_MOON),
    )

    assert profiles == ()


def test_resolution_skips_missing_profiles_without_blocking_other_profiles() -> None:
    """Une cle sans entree statique ne bloque pas les autres familles."""
    profiles = resolve_advanced_condition_profiles(
        bundle=_bundle(
            "mars",
            visibility=_visibility("mars", PlanetVisibilityKey.HELIACAL_RISING),
            solar_phase_relation=_solar_phase("mars", SolarPhaseRelationKey.ORIENTAL),
        ),
        moon_phase=None,
    )

    assert [profile.condition_key for profile in profiles] == ["oriental"]


def test_moon_phase_profiles_apply_only_to_moon() -> None:
    """Les profils de phase lunaire restent rattaches au bundle lunaire."""
    moon_profiles = resolve_advanced_condition_profiles(
        bundle=_bundle("moon"),
        moon_phase=_moon_phase(MoonPhaseKey.FULL_MOON),
    )
    new_moon_profiles = resolve_advanced_condition_profiles(
        bundle=_bundle("moon"),
        moon_phase=_moon_phase(MoonPhaseKey.NEW_MOON),
    )
    venus_profiles = resolve_advanced_condition_profiles(
        bundle=_bundle("venus"),
        moon_phase=_moon_phase(MoonPhaseKey.NEW_MOON),
    )

    assert [profile.condition_key for profile in moon_profiles] == ["full_moon"]
    assert [profile.condition_key for profile in new_moon_profiles] == ["new_moon"]
    assert venus_profiles == ()


def _profiles_for(condition_key: str) -> tuple[AdvancedConditionInterpretationProfile, ...]:
    """Retourne les profils du catalogue pour une cle donnee."""
    return tuple(
        profile
        for profile in ADVANCED_CONDITION_PROFILE_CATALOG
        if profile.condition_key == condition_key
        and profile.planet_key is None
        and profile.tradition_key is None
    )


def _bundle(
    planet_key: str,
    *,
    solar_proximity: SolarProximityCondition | None = None,
    motion: PlanetaryMotionCondition | None = None,
    visibility: PlanetVisibilityCondition | None = None,
    solar_phase_relation: PlanetarySolarPhaseRelation | None = None,
) -> PlanetaryConditionsBundle:
    """Construit un bundle partiel de faits deja calcules."""
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
    """Construit une proximite solaire contractuelle."""
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
    direction: PlanetaryMotionDirection,
) -> PlanetaryMotionCondition:
    """Construit un mouvement planetaire contractuel."""
    return PlanetaryMotionCondition(
        planet_key=planet_key,
        speed_deg_per_day=-0.1 if direction is PlanetaryMotionDirection.RETROGRADE else 0.0,
        absolute_speed_deg_per_day=0.1,
        direction=direction,
        speed_state=PlanetarySpeedState.SLOW,
        is_retrograde=direction is PlanetaryMotionDirection.RETROGRADE,
        is_stationary=direction is PlanetaryMotionDirection.STATIONARY,
        normalized_speed_ratio=0.1,
    )


def _visibility(
    planet_key: str,
    visibility_key: PlanetVisibilityKey,
) -> PlanetVisibilityCondition:
    """Construit une visibilite planetaire contractuelle."""
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
    """Construit une relation solaire contractuelle."""
    return PlanetarySolarPhaseRelation(
        planet_key=planet_key,
        relation_key=relation_key,
        angular_distance_deg=80.0,
        is_oriental=relation_key is SolarPhaseRelationKey.ORIENTAL,
        is_occidental=relation_key is SolarPhaseRelationKey.OCCIDENTAL,
    )


def _moon_phase(phase_key: MoonPhaseKey) -> MoonPhaseCondition:
    """Construit une phase lunaire contractuelle."""
    return MoonPhaseCondition(
        phase_key=phase_key,
        sun_moon_angle_deg=180.0,
        illumination_ratio=1.0,
        waxing_or_waning=WaxingWaningState.EXACT,
        phase_index=4,
    )
