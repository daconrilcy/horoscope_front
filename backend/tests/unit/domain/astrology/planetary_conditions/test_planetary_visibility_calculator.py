"""Tests du calculateur pur de visibilite planetaire."""

import pytest

from app.domain.astrology.planetary_conditions import (
    ConditionConfidence,
    ConditionSeverity,
    PlanetarySolarPhaseRelation,
    PlanetVisibilityKey,
    PlanetVisibilityThresholds,
    SolarPhaseRelationKey,
    SolarProximityCondition,
    SolarProximityConditionKey,
    calculate_planet_visibility_condition,
    calculate_planet_visibility_conditions,
)


def test_sun_returns_nominal_visible_condition() -> None:
    """Le Soleil reste visible sans etre classe en conjonction solaire."""
    condition = calculate_planet_visibility_condition(
        planet_key="sun",
        solar_proximity_condition=_proximity(
            "sun",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=0.0,
        ),
        solar_phase_relation=_relation("sun", SolarPhaseRelationKey.CONJUNCT_SOLAR),
    )

    assert condition.planet_key == "sun"
    assert condition.visibility_key is PlanetVisibilityKey.VISIBLE
    assert condition.is_visible is True
    assert condition.confidence is ConditionConfidence.HIGH
    assert condition.reason == "sun_visible"


def test_cazimi_returns_visible_solar_conjunction() -> None:
    """Le cazimi gagne sur les autres restrictions solaires."""
    condition = calculate_planet_visibility_condition(
        planet_key="venus",
        solar_proximity_condition=_proximity(
            "venus",
            SolarProximityConditionKey.CAZIMI,
            sun_distance_deg=0.4,
        ),
        solar_phase_relation=_relation("venus", SolarPhaseRelationKey.OCCIDENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.CONJUNCT_SOLAR
    assert condition.is_visible is True
    assert condition.confidence is ConditionConfidence.EXACT
    assert condition.reason == "solar_conjunction"


def test_distance_under_conjunction_tolerance_returns_solar_conjunction() -> None:
    """La tolerance de conjonction suffit sans recalculer les longitudes."""
    condition = calculate_planet_visibility_condition(
        planet_key="mercury",
        solar_proximity_condition=_proximity(
            "mercury",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=0.5,
        ),
        solar_phase_relation=_relation("mercury", SolarPhaseRelationKey.ORIENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.CONJUNCT_SOLAR
    assert condition.reason == "solar_conjunction"


def test_combust_returns_invisible() -> None:
    """La combustion rend la planete invisible dans le contrat simplifie."""
    condition = calculate_planet_visibility_condition(
        planet_key="mars",
        solar_proximity_condition=_proximity(
            "mars",
            SolarProximityConditionKey.COMBUST,
            sun_distance_deg=6.0,
        ),
        solar_phase_relation=_relation("mars", SolarPhaseRelationKey.ORIENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.INVISIBLE
    assert condition.is_visible is False
    assert condition.confidence is ConditionConfidence.HIGH
    assert condition.reason == "combust"


def test_under_beams_returns_under_beams_even_with_emerging_distance() -> None:
    """Le fait amont under beams garde priorite sur la fenetre d'emergence."""
    condition = calculate_planet_visibility_condition(
        planet_key="mercury",
        solar_proximity_condition=_proximity(
            "mercury",
            SolarProximityConditionKey.UNDER_BEAMS,
            sun_distance_deg=16.0,
        ),
        solar_phase_relation=_relation("mercury", SolarPhaseRelationKey.ORIENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.UNDER_BEAMS
    assert condition.is_visible is False
    assert condition.confidence is ConditionConfidence.HIGH
    assert condition.reason == "under_beams"


def test_oriental_planet_in_emerging_window_returns_emerging() -> None:
    """Une planete orientale sortant des rayons devient emerging."""
    condition = calculate_planet_visibility_condition(
        planet_key="jupiter",
        solar_proximity_condition=_proximity(
            "jupiter",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=16.0,
        ),
        solar_phase_relation=_relation("jupiter", SolarPhaseRelationKey.ORIENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.EMERGING
    assert condition.is_visible is True
    assert condition.confidence is ConditionConfidence.MEDIUM
    assert condition.reason == "planet_exiting_solar_beams"


def test_occidental_planet_in_emerging_window_returns_visible() -> None:
    """La fenetre d'emergence ne s'applique pas aux planetes occidentales."""
    condition = calculate_planet_visibility_condition(
        planet_key="saturn",
        solar_proximity_condition=_proximity(
            "saturn",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=16.0,
        ),
        solar_phase_relation=_relation("saturn", SolarPhaseRelationKey.OCCIDENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.VISIBLE
    assert condition.is_visible is True
    assert condition.reason == "outside_visibility_restrictions"


def test_outside_restrictions_returns_visible() -> None:
    """Une planete hors restrictions solaires reste visible."""
    condition = calculate_planet_visibility_condition(
        planet_key="saturn",
        solar_proximity_condition=_proximity(
            "saturn",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=24.0,
        ),
        solar_phase_relation=_relation("saturn", SolarPhaseRelationKey.ORIENTAL),
    )

    assert condition.visibility_key is PlanetVisibilityKey.VISIBLE
    assert condition.is_visible is True
    assert condition.confidence is ConditionConfidence.HIGH


def test_custom_thresholds_change_classification() -> None:
    """Les seuils fournis controlent la conjonction et la fenetre d'emergence."""
    thresholds = PlanetVisibilityThresholds(
        conjunction_tolerance_deg=1.0,
        under_beams_limit_deg=20.0,
        emerging_limit_deg=24.0,
    )
    conjunct = calculate_planet_visibility_condition(
        planet_key="venus",
        solar_proximity_condition=_proximity(
            "venus",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=0.75,
        ),
        solar_phase_relation=_relation("venus", SolarPhaseRelationKey.OCCIDENTAL),
        thresholds=thresholds,
    )
    emerging = calculate_planet_visibility_condition(
        planet_key="jupiter",
        solar_proximity_condition=_proximity(
            "jupiter",
            SolarProximityConditionKey.NONE,
            sun_distance_deg=22.0,
        ),
        solar_phase_relation=_relation("jupiter", SolarPhaseRelationKey.ORIENTAL),
        thresholds=thresholds,
    )

    assert conjunct.visibility_key is PlanetVisibilityKey.CONJUNCT_SOLAR
    assert emerging.visibility_key is PlanetVisibilityKey.EMERGING


def test_batch_calculator_returns_visibility_for_each_proximity_key() -> None:
    """Le calcul de lot conserve l'ordre et les cles des proximites fournies."""
    conditions = calculate_planet_visibility_conditions(
        solar_proximity_conditions={
            "sun": _proximity("sun", SolarProximityConditionKey.NONE, sun_distance_deg=0.0),
            "venus": _proximity("venus", SolarProximityConditionKey.CAZIMI, sun_distance_deg=0.1),
            "mars": _proximity("mars", SolarProximityConditionKey.COMBUST, sun_distance_deg=5.0),
            "jupiter": _proximity(
                "jupiter",
                SolarProximityConditionKey.NONE,
                sun_distance_deg=16.0,
            ),
        },
        solar_phase_relations={
            "sun": _relation("sun", SolarPhaseRelationKey.CONJUNCT_SOLAR),
            "venus": _relation("venus", SolarPhaseRelationKey.CONJUNCT_SOLAR),
            "mars": _relation("mars", SolarPhaseRelationKey.OCCIDENTAL),
            "jupiter": _relation("jupiter", SolarPhaseRelationKey.ORIENTAL),
        },
    )

    assert tuple(conditions) == ("sun", "venus", "mars", "jupiter")
    assert conditions["sun"].visibility_key is PlanetVisibilityKey.VISIBLE
    assert conditions["venus"].visibility_key is PlanetVisibilityKey.CONJUNCT_SOLAR
    assert conditions["mars"].visibility_key is PlanetVisibilityKey.INVISIBLE
    assert conditions["jupiter"].visibility_key is PlanetVisibilityKey.EMERGING


def test_batch_calculator_fails_explicitly_when_relation_is_missing() -> None:
    """Une relation solaire absente ne produit pas de condition inconnue silencieuse."""
    with pytest.raises(KeyError, match="venus"):
        calculate_planet_visibility_conditions(
            solar_proximity_conditions={
                "venus": _proximity(
                    "venus",
                    SolarProximityConditionKey.NONE,
                    sun_distance_deg=20.0,
                )
            },
            solar_phase_relations={},
        )


def test_nominal_cases_do_not_return_unknown_or_heliacal_placeholders() -> None:
    """Les placeholders contractuels ne sortent pas des cas nominaux CS-213."""
    produced_keys = {
        calculate_planet_visibility_condition(
            planet_key=planet_key,
            solar_proximity_condition=proximity,
            solar_phase_relation=relation,
        ).visibility_key
        for planet_key, proximity, relation in (
            (
                "venus",
                _proximity("venus", SolarProximityConditionKey.CAZIMI, sun_distance_deg=0.1),
                _relation("venus", SolarPhaseRelationKey.CONJUNCT_SOLAR),
            ),
            (
                "mars",
                _proximity("mars", SolarProximityConditionKey.COMBUST, sun_distance_deg=5.0),
                _relation("mars", SolarPhaseRelationKey.ORIENTAL),
            ),
            (
                "mercury",
                _proximity(
                    "mercury",
                    SolarProximityConditionKey.UNDER_BEAMS,
                    sun_distance_deg=12.0,
                ),
                _relation("mercury", SolarPhaseRelationKey.ORIENTAL),
            ),
            (
                "jupiter",
                _proximity("jupiter", SolarProximityConditionKey.NONE, sun_distance_deg=16.0),
                _relation("jupiter", SolarPhaseRelationKey.ORIENTAL),
            ),
            (
                "saturn",
                _proximity("saturn", SolarProximityConditionKey.NONE, sun_distance_deg=24.0),
                _relation("saturn", SolarPhaseRelationKey.OCCIDENTAL),
            ),
        )
    }

    assert PlanetVisibilityKey.UNKNOWN not in produced_keys
    assert PlanetVisibilityKey.HELIACAL_RISING not in produced_keys
    assert PlanetVisibilityKey.HELIACAL_SETTING not in produced_keys


def _proximity(
    planet_key: str,
    condition_key: SolarProximityConditionKey,
    *,
    sun_distance_deg: float,
) -> SolarProximityCondition:
    """Construit un fait de proximite solaire deja calcule."""
    return SolarProximityCondition(
        planet_key=planet_key,
        condition_key=condition_key,
        sun_distance_deg=sun_distance_deg,
        orb_deg=None,
        severity=ConditionSeverity.NONE,
        is_active=condition_key is not SolarProximityConditionKey.NONE,
    )


def _relation(
    planet_key: str,
    relation_key: SolarPhaseRelationKey,
) -> PlanetarySolarPhaseRelation:
    """Construit un fait de relation solaire deja calcule."""
    return PlanetarySolarPhaseRelation(
        planet_key=planet_key,
        relation_key=relation_key,
        angular_distance_deg=0.0,
        is_oriental=relation_key is SolarPhaseRelationKey.ORIENTAL,
        is_occidental=relation_key is SolarPhaseRelationKey.OCCIDENTAL,
    )
