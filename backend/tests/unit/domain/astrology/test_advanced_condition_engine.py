"""Tests du moteur de conditions planetaires avancees."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.advanced_conditions.contracts import (
    PlanetConditionAxisImpact,
)
from tests.unit.domain.astrology.advanced_condition_test_helpers import (
    advanced_engine_result,
    dignity,
    position,
)


def test_advanced_condition_contracts_are_immutable() -> None:
    """Les impacts d'axes avances ne sont pas mutables."""
    impact = PlanetConditionAxisImpact(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    with pytest.raises(FrozenInstanceError):
        impact.functional_strength_delta = 2.0


def test_advanced_condition_engine_enriches_profiles_without_replacing_them() -> None:
    """Le moteur ajoute breakdown et faits avances aux profils existants."""
    conditions, profiles = advanced_engine_result(
        (position("sun", "leo", house_number=10),),
        (
            dignity(
                "sun",
                "hayz",
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
        ),
    )

    assert {item.condition_code for item in conditions} == {"hayz", "sect_nature_unknown"}
    profile = profiles[0]
    assert profile.planet_code == "sun"
    assert any(item.dignity_family == "advanced" for item in profile.breakdown)
    assert any(item.dignity_type_code == "hayz" for item in profile.breakdown)
    assert any(item.value == "hayz" for item in profile.explanation_facts)
    assert profile.ranking_score > 1.0


def test_out_of_sect_advanced_condition_uses_planet_sect_condition() -> None:
    """La condition hors-secte ne depend plus du breakdown accidentel."""
    conditions, _profiles = advanced_engine_result(
        (position("mars", "aries"),),
        (
            dignity(
                "mars",
                intrinsic_sect="nocturnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert {item.condition_code for item in conditions} == {
        "malefic_aggravated_out_of_sect",
        "out_of_sect",
    }
    out_of_sect = next(item for item in conditions if item.condition_code == "out_of_sect")
    assert out_of_sect.reason == "mars is out of sect according to PlanetSectCondition."


def test_night_chart_diurnal_planet_out_of_sect_uses_planet_sect_condition() -> None:
    """Un theme nocturne avec planete diurne hors secte consomme le contrat CS-198."""
    conditions, _profiles = advanced_engine_result(
        (position("sun", "leo", house_number=4),),
        (
            dignity(
                "sun",
                chart_sect="night",
                intrinsic_sect="diurnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    assert {item.condition_code for item in conditions} == {
        "out_of_sect",
        "sect_nature_unknown",
    }


def test_hayz_still_requires_non_sect_hayz_factors() -> None:
    """Une planete en secte ne devient pas hayz sans les autres facteurs hayz."""
    conditions, _profiles = advanced_engine_result(
        (position("sun", "taurus"),),
        (
            dignity(
                "sun",
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
        ),
    )

    assert [item.condition_code for item in conditions] == ["sect_nature_unknown"]


def test_advanced_condition_engine_emits_sect_nature_mitigation_from_runtime() -> None:
    """Le moteur expose la mitigation CS-206 via les poids runtime avances."""
    conditions, profiles = advanced_engine_result(
        (position("jupiter", "sagittarius"),),
        (
            dignity(
                "jupiter",
                intrinsic_sect="diurnal",
                planet_sect_condition="in_sect",
                is_in_sect=True,
            ),
        ),
    )

    condition = next(
        item for item in conditions if item.condition_code == "benefic_supported_by_sect"
    )
    assert condition.condition_type_code == "sect_nature_mitigation"
    assert condition.calculation_facts["planet_nature"] == "benefic"
    assert condition.score_impact == 0.0
    assert condition.ranking_weight == 0.0
    profile = profiles[0]
    assert any(item.dignity_type_code == "benefic_supported_by_sect" for item in profile.breakdown)


def test_sect_nature_mitigation_weight_is_neutral_for_negative_states() -> None:
    """Le poids commun CS-206 ne transforme pas aggravation/faiblesse en soutien."""
    conditions, profiles = advanced_engine_result(
        (position("jupiter", "sagittarius"),),
        (
            dignity(
                "jupiter",
                chart_sect="night",
                intrinsic_sect="diurnal",
                planet_sect_condition="out_of_sect",
                is_out_of_sect=True,
            ),
        ),
    )

    condition = next(
        item for item in conditions if item.condition_code == "benefic_weakened_out_of_sect"
    )
    assert condition.score_impact == 0.0
    assert condition.ranking_weight == 0.0
    profile = profiles[0]
    breakdown = next(
        item for item in profile.breakdown if item.dignity_type_code == condition.condition_code
    )
    assert breakdown.support == 0.0
    assert breakdown.constraint == 0.0


def test_missing_planet_sect_condition_fails_explicitly() -> None:
    """Les conditions avancees dependantes de la secte exigent le contrat CS-198."""
    with pytest.raises(ValueError, match="PlanetSectCondition is required"):
        advanced_engine_result(
            (position("sun", "leo", house_number=10),),
            (dignity("sun", "hayz", include_sect_condition=False),),
        )
