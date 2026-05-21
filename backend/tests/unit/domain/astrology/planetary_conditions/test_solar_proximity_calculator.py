"""Tests du calculateur pur de proximite solaire."""

from app.domain.astrology.planetary_conditions import (
    ConditionSeverity,
    SolarProximityConditionKey,
    SolarProximityThresholds,
    calculate_solar_proximity_condition,
    calculate_solar_proximity_conditions,
)


def test_calculator_returns_cazimi_with_highest_priority() -> None:
    """La proximite sous le seuil cazimi gagne sur les seuils plus larges."""
    condition = calculate_solar_proximity_condition(
        planet_key="venus",
        planet_longitude_deg=10.1,
        sun_longitude_deg=10.0,
    )

    assert condition.planet_key == "venus"
    assert condition.condition_key is SolarProximityConditionKey.CAZIMI
    assert condition.severity is ConditionSeverity.EXTREME
    assert condition.is_active is True
    assert condition.sun_distance_deg == 0.09999999999999964
    assert condition.orb_deg == 17.0 / 60.0


def test_calculator_returns_combust_under_beams_and_none() -> None:
    """Les seuils ordonnes produisent une seule condition active ou aucune."""
    combust = calculate_solar_proximity_condition(
        planet_key="mars",
        planet_longitude_deg=18.5,
        sun_longitude_deg=10.0,
    )
    under_beams = calculate_solar_proximity_condition(
        planet_key="mercury",
        planet_longitude_deg=25.0,
        sun_longitude_deg=10.0,
    )
    free = calculate_solar_proximity_condition(
        planet_key="saturn",
        planet_longitude_deg=25.0001,
        sun_longitude_deg=10.0,
    )

    assert combust.condition_key is SolarProximityConditionKey.COMBUST
    assert combust.severity is ConditionSeverity.MAJOR
    assert combust.orb_deg == 8.5
    assert under_beams.condition_key is SolarProximityConditionKey.UNDER_BEAMS
    assert under_beams.severity is ConditionSeverity.MODERATE
    assert under_beams.orb_deg == 15.0
    assert free.condition_key is SolarProximityConditionKey.NONE
    assert free.severity is ConditionSeverity.NONE
    assert free.is_active is False
    assert free.orb_deg is None


def test_calculator_uses_minimal_distance_across_zero() -> None:
    """La distance angulaire traverse correctement le passage 0/360."""
    first = calculate_solar_proximity_condition(
        planet_key="mercury",
        planet_longitude_deg=358.0,
        sun_longitude_deg=2.0,
    )
    second = calculate_solar_proximity_condition(
        planet_key="venus",
        planet_longitude_deg=1.0,
        sun_longitude_deg=359.0,
    )

    assert first.sun_distance_deg == 4.0
    assert first.condition_key is SolarProximityConditionKey.COMBUST
    assert second.sun_distance_deg == 2.0
    assert second.condition_key is SolarProximityConditionKey.COMBUST


def test_calculator_normalizes_longitudes_before_classification() -> None:
    """Les longitudes hors plage sont ramenees dans le cercle zodiacal."""
    condition = calculate_solar_proximity_condition(
        planet_key="jupiter",
        planet_longitude_deg=721.0,
        sun_longitude_deg=-1.0,
    )
    zero_wrapped = calculate_solar_proximity_condition(
        planet_key="mercury",
        planet_longitude_deg=360.0,
        sun_longitude_deg=0.0,
    )

    assert condition.sun_distance_deg == 2.0
    assert condition.condition_key is SolarProximityConditionKey.COMBUST
    assert zero_wrapped.sun_distance_deg == 0.0
    assert zero_wrapped.condition_key is SolarProximityConditionKey.CAZIMI


def test_default_threshold_bounds_are_inclusive() -> None:
    """Les bornes exactes du brief restent inclusives."""
    cazimi = calculate_solar_proximity_condition(
        planet_key="venus",
        planet_longitude_deg=17.0 / 60.0,
        sun_longitude_deg=0.0,
    )
    combust = calculate_solar_proximity_condition(
        planet_key="mars",
        planet_longitude_deg=8.5,
        sun_longitude_deg=0.0,
    )
    under_beams = calculate_solar_proximity_condition(
        planet_key="mercury",
        planet_longitude_deg=15.0,
        sun_longitude_deg=0.0,
    )
    free = calculate_solar_proximity_condition(
        planet_key="saturn",
        planet_longitude_deg=15.0001,
        sun_longitude_deg=0.0,
    )

    assert cazimi.condition_key is SolarProximityConditionKey.CAZIMI
    assert combust.condition_key is SolarProximityConditionKey.COMBUST
    assert under_beams.condition_key is SolarProximityConditionKey.UNDER_BEAMS
    assert free.condition_key is SolarProximityConditionKey.NONE


def test_sun_returns_inactive_none_condition() -> None:
    """Le Soleil ne recoit pas de proximite solaire active."""
    condition = calculate_solar_proximity_condition(
        planet_key="sun",
        planet_longitude_deg=42.0,
        sun_longitude_deg=42.0,
    )

    assert condition.planet_key == "sun"
    assert condition.condition_key is SolarProximityConditionKey.NONE
    assert condition.sun_distance_deg == 0.0
    assert condition.orb_deg is None
    assert condition.severity is ConditionSeverity.NONE
    assert condition.is_active is False


def test_planet_key_is_not_normalized_as_alias() -> None:
    """La cle planete fournie ne cree pas d'alias silencieux."""
    condition = calculate_solar_proximity_condition(
        planet_key="Sun",
        planet_longitude_deg=50.0,
        sun_longitude_deg=42.0,
    )

    assert condition.planet_key == "Sun"
    assert condition.condition_key is SolarProximityConditionKey.COMBUST
    assert condition.is_active is True


def test_custom_thresholds_change_classification_without_new_contract() -> None:
    """Les seuils personnalises restent portes par le contrat public."""
    thresholds = SolarProximityThresholds(
        cazimi_max_distance_deg=1.0,
        combust_max_distance_deg=3.0,
        under_beams_max_distance_deg=5.0,
    )
    condition = calculate_solar_proximity_condition(
        planet_key="venus",
        planet_longitude_deg=4.0,
        sun_longitude_deg=0.0,
        thresholds=thresholds,
    )

    assert condition.condition_key is SolarProximityConditionKey.UNDER_BEAMS
    assert condition.orb_deg == 5.0


def test_batch_calculator_returns_mapping_including_sun() -> None:
    """Le calcul de lot conserve toutes les cles fournies par l'appelant."""
    conditions = calculate_solar_proximity_conditions(
        planet_longitudes_deg={
            "sun": 10.0,
            "venus": 10.1,
            "mars": 20.0,
        },
        sun_longitude_deg=10.0,
    )

    assert tuple(conditions) == ("sun", "venus", "mars")
    assert conditions["sun"].condition_key is SolarProximityConditionKey.NONE
    assert conditions["venus"].condition_key is SolarProximityConditionKey.CAZIMI
    assert conditions["mars"].condition_key is SolarProximityConditionKey.UNDER_BEAMS
