"""Tests d'integration des conditions planetaires avancees dans NatalResult."""

from __future__ import annotations

from app.domain.astrology.interpretation.advanced_conditions import (
    AdvancedConditionInterpretationProfile,
)
from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.planetary_conditions import AdvancedPlanetaryConditionsResult
from app.main import app
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_natal_result_exposes_optional_advanced_planetary_conditions_field() -> None:
    """Le contrat natal expose le bloc runtime sans le rendre obligatoire."""
    field = NatalResult.model_fields["advanced_planetary_conditions"]

    assert field.annotation == (AdvancedPlanetaryConditionsResult | None)
    assert field.default is None
    assert "advanced_planetary_conditions" not in NatalResult.model_json_schema()["properties"]


def test_natal_result_exposes_internal_interpretation_profiles_field() -> None:
    """Le contrat natal expose les profils symboliques sans schema public."""
    field = NatalResult.model_fields["interpretation_profiles_by_planet"]

    assert field.default_factory is not None
    assert "interpretation_profiles_by_planet" not in NatalResult.model_json_schema()["properties"]


def test_build_natal_result_populates_advanced_planetary_conditions() -> None:
    """Le pipeline natal renseigne les conditions avancees depuis les positions."""
    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )

    advanced = result.advanced_planetary_conditions
    assert advanced is not None
    assert set(advanced.conditions_by_planet) >= {"sun", "moon"}
    assert advanced.conditions_by_planet["sun"].planet_key == "sun"
    assert advanced.conditions_by_planet["moon"].planet_key == "moon"
    assert advanced.moon_phase is not None
    assert isinstance(advanced, AdvancedPlanetaryConditionsResult)
    assert set(result.interpretation_profiles_by_planet) >= {"sun", "moon"}
    assert any(result.interpretation_profiles_by_planet.values())
    assert all(
        isinstance(profile, AdvancedConditionInterpretationProfile)
        for profiles in result.interpretation_profiles_by_planet.values()
        for profile in profiles
    )
    assert "advanced_planetary_conditions" not in result.model_dump(mode="json")
    assert "interpretation_profiles_by_planet" not in result.model_dump(mode="json")


def test_advanced_planetary_conditions_stays_out_of_openapi_schema() -> None:
    """Le bloc runtime ne modifie pas les schemas publics generes."""
    schemas = app.openapi().get("components", {}).get("schemas", {})

    assert "advanced_planetary_conditions" not in str(schemas)
    assert "interpretation_profiles_by_planet" not in str(schemas)
