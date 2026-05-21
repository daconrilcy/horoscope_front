"""Tests du calculateur pur de relation solaire oriental-occidental."""

from math import inf, nan

import pytest

from app.domain.astrology.planetary_conditions import (
    PlanetarySolarPhaseRelation,
    SolarPhaseRelationKey,
    SolarPhaseRelationThresholds,
    calculate_solar_phase_relation,
    calculate_solar_phase_relations,
)


def test_calculator_returns_conjunct_solar_for_exact_angle_and_sun() -> None:
    """La conjonction exacte et le Soleil produisent le meme fait contractuel."""
    exact = calculate_solar_phase_relation(
        planet_key="venus",
        planet_longitude_deg=42.0,
        sun_longitude_deg=42.0,
    )
    sun = calculate_solar_phase_relation(
        planet_key="sun",
        planet_longitude_deg=128.0,
        sun_longitude_deg=42.0,
    )

    assert isinstance(exact, PlanetarySolarPhaseRelation)
    assert exact.relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert exact.angular_distance_deg == 0.0
    assert exact.is_oriental is False
    assert exact.is_occidental is False
    assert sun.relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert sun.angular_distance_deg == 0.0


def test_calculator_applies_conjunction_tolerance_around_zero() -> None:
    """La tolerance agit symetriquement autour du passage zodiacal zero."""
    before_zero = calculate_solar_phase_relation(
        planet_key="mercury",
        planet_longitude_deg=359.6,
        sun_longitude_deg=0.0,
    )
    after_zero = calculate_solar_phase_relation(
        planet_key="venus",
        planet_longitude_deg=0.5,
        sun_longitude_deg=0.0,
    )
    outside = calculate_solar_phase_relation(
        planet_key="mars",
        planet_longitude_deg=359.49,
        sun_longitude_deg=0.0,
    )

    assert before_zero.relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert before_zero.angular_distance_deg == 359.6
    assert after_zero.relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert after_zero.angular_distance_deg == 0.5
    assert outside.relation_key is SolarPhaseRelationKey.ORIENTAL


def test_calculator_uses_relative_angle_from_sun_to_planet() -> None:
    """L'angle relatif conserve la direction `(planete - Soleil) % 360`."""
    occidental = calculate_solar_phase_relation(
        planet_key="mars",
        planet_longitude_deg=110.0,
        sun_longitude_deg=100.0,
    )
    oriental = calculate_solar_phase_relation(
        planet_key="jupiter",
        planet_longitude_deg=90.0,
        sun_longitude_deg=100.0,
    )

    assert occidental.angular_distance_deg == 10.0
    assert occidental.relation_key is SolarPhaseRelationKey.OCCIDENTAL
    assert occidental.is_occidental is True
    assert oriental.angular_distance_deg == 350.0
    assert oriental.relation_key is SolarPhaseRelationKey.ORIENTAL
    assert oriental.is_oriental is True


def test_exact_opposition_is_occidental() -> None:
    """L'opposition exacte appartient explicitement a l'hemicycle occidental."""
    relation = calculate_solar_phase_relation(
        planet_key="saturn",
        planet_longitude_deg=280.0,
        sun_longitude_deg=100.0,
    )

    assert relation.angular_distance_deg == 180.0
    assert relation.relation_key is SolarPhaseRelationKey.OCCIDENTAL
    assert relation.is_occidental is True
    assert relation.is_oriental is False


def test_calculator_normalizes_longitudes_before_classification() -> None:
    """Les longitudes hors cercle produisent le meme angle relatif canonique."""
    relation = calculate_solar_phase_relation(
        planet_key="venus",
        planet_longitude_deg=721.0,
        sun_longitude_deg=-1.0,
    )
    wrapped = calculate_solar_phase_relation(
        planet_key="mercury",
        planet_longitude_deg=-1.0,
        sun_longitude_deg=361.0,
    )

    assert relation.angular_distance_deg == 2.0
    assert relation.relation_key is SolarPhaseRelationKey.OCCIDENTAL
    assert wrapped.angular_distance_deg == 358.0
    assert wrapped.relation_key is SolarPhaseRelationKey.ORIENTAL


def test_custom_threshold_changes_only_conjunction_window() -> None:
    """Le seuil fourni controle seulement la fenetre de conjonction."""
    thresholds = SolarPhaseRelationThresholds(conjunction_tolerance_deg=2.0)
    relation = calculate_solar_phase_relation(
        planet_key="venus",
        planet_longitude_deg=358.5,
        sun_longitude_deg=0.0,
        thresholds=thresholds,
    )

    assert relation.relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert relation.relation_key is not SolarPhaseRelationKey.UNKNOWN


def test_non_finite_longitudes_are_rejected() -> None:
    """Les longitudes non finies ne deviennent pas des faits solaires."""
    with pytest.raises(ValueError, match="longitude must be finite"):
        calculate_solar_phase_relation(
            planet_key="venus",
            planet_longitude_deg=nan,
            sun_longitude_deg=0.0,
        )
    with pytest.raises(ValueError, match="longitude must be finite"):
        calculate_solar_phase_relation(
            planet_key="venus",
            planet_longitude_deg=0.0,
            sun_longitude_deg=inf,
        )


def test_batch_calculator_returns_mapping_for_each_input() -> None:
    """Le calcul de lot conserve toutes les cles planetaires fournies."""
    relations = calculate_solar_phase_relations(
        planet_longitudes_deg={
            "sun": 10.0,
            "venus": 10.4,
            "mars": 20.0,
            "jupiter": 350.0,
        },
        sun_longitude_deg=10.0,
    )

    assert tuple(relations) == ("sun", "venus", "mars", "jupiter")
    assert relations["sun"].relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert relations["venus"].relation_key is SolarPhaseRelationKey.CONJUNCT_SOLAR
    assert relations["mars"].relation_key is SolarPhaseRelationKey.OCCIDENTAL
    assert relations["jupiter"].relation_key is SolarPhaseRelationKey.ORIENTAL
