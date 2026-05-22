"""Tests d'integration de `chart_objects` dans le resultat natal."""

from __future__ import annotations

import pytest

from app.domain.astrology import natal_calculation
from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.planetary_conditions.contracts import (
    PlanetaryMotionDirection,
    PlanetVisibilityKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import ChartObjectType
from app.main import app
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _result():
    """Construit un theme natal stable pour les assertions de contrat runtime."""
    return build_natal_result(
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


def test_natal_result_exposes_internal_chart_objects_field() -> None:
    """Le contrat natal expose `chart_objects` sans schema public."""
    field = NatalResult.model_fields["chart_objects"]

    assert field.default_factory is not None
    assert "chart_objects" not in NatalResult.model_json_schema()["properties"]


def test_build_natal_result_populates_chart_objects_without_replacing_collections() -> None:
    """Le pipeline ajoute la projection unifiee et preserve les collections historiques."""
    result = _result()
    by_code = {item.code: item for item in result.chart_objects}

    assert result.planet_positions
    assert result.astral_points
    assert len(result.houses) == 12
    assert result.house_rulers
    assert result.dignities
    assert result.dominant_planets.planets
    assert result.chart_objects
    assert set(by_code) >= {"sun", "moon", "north_node", "south_node", "asc", "mc"}
    assert by_code["sun"].object_type == ChartObjectType.LUMINARY
    assert by_code["moon"].object_type == ChartObjectType.LUMINARY
    assert by_code["north_node"].object_type == ChartObjectType.ASTRAL_POINT
    assert by_code["north_node"].capabilities.supports_aspects is False
    assert by_code["asc"].capabilities.supports_aspects is False
    assert by_code["house_1_cusp"].object_type == ChartObjectType.HOUSE_CUSP
    assert (
        len(
            [
                item
                for item in result.chart_objects
                if item.object_type == ChartObjectType.HOUSE_CUSP
            ]
        )
        == 12
    )


def test_simplified_engine_does_not_advertise_missing_motion_payloads() -> None:
    """Le moteur simplifie n'annonce pas de capacite motion sans donnees motion."""
    result = _result()
    planets = [
        item
        for item in result.chart_objects
        if item.object_type in {ChartObjectType.LUMINARY, ChartObjectType.PLANET}
    ]

    assert planets
    assert all(not item.capabilities.supports_motion for item in planets)
    assert all(item.payloads.motion is None for item in planets)


def test_natal_chart_objects_expose_visibility_payloads_from_advanced_conditions() -> None:
    """Les objets planetaires exposent la visibilite issue des conditions avancees."""
    result = _result()
    by_code = {item.code: item for item in result.chart_objects}

    assert result.advanced_planetary_conditions is not None
    assert by_code["sun"].capabilities.supports_visibility is True
    assert by_code["sun"].payloads.visibility is not None
    assert by_code["sun"].payloads.visibility.visibility_key is PlanetVisibilityKey.VISIBLE
    assert by_code["sun"].payloads.visibility.is_cazimi is None
    assert by_code["sun"].payloads.visibility.is_oriental is None
    assert by_code["sun"].payloads.visibility.is_occidental is None
    assert by_code["moon"].capabilities.supports_visibility is True
    assert by_code["moon"].payloads.visibility is not None
    assert by_code["north_node"].capabilities.supports_visibility is False
    assert by_code["north_node"].payloads.visibility is None
    assert by_code["house_1_cusp"].capabilities.supports_visibility is False
    assert by_code["house_1_cusp"].payloads.visibility is None


def test_natal_chart_objects_expose_dignity_and_dominance_payloads() -> None:
    """Le pipeline natal enrichit les objets eligibles apres les calculs historiques."""
    result = _result()
    by_code = {item.code: item for item in result.chart_objects}
    dignity_by_code = {item.planet_code: item for item in result.dignities}
    dominance_by_code = {item.planet_code: item for item in result.dominant_planets.planets}

    assert by_code["sun"].capabilities.supports_dignities is True
    assert by_code["sun"].payloads.dignity is not None
    assert by_code["sun"].payloads.dignity.total_score == dignity_by_code["sun"].total_score
    assert by_code["mars"].payloads.dominance is not None
    assert (
        by_code["mars"].payloads.dominance.contribution_score
        == dominance_by_code["mars"].total_score
    )
    assert by_code["north_node"].capabilities.supports_dignities is False
    assert by_code["north_node"].payloads.dignity is None
    assert by_code["house_1_cusp"].capabilities.supports_dominance is False
    assert by_code["house_1_cusp"].payloads.dominance is None
    assert result.dominant_planets.top_planet_code is not None


def test_natal_chart_objects_expose_house_position_and_rulership_payloads() -> None:
    """Le pipeline natal enrichit les objets internes avec maisons et maitrises."""
    result = _result()
    by_code = {item.code: item for item in result.chart_objects}
    rules_by_code = {
        item.ruler_planet: tuple(
            ruler.house_number
            for ruler in result.house_rulers
            if ruler.ruler_planet == item.ruler_planet
        )
        for item in result.house_rulers
    }

    assert by_code["sun"].payloads.house_position is not None
    assert by_code["sun"].payloads.house_position.house_modality in {
        "angular",
        "succedent",
        "cadent",
    }
    assert by_code["sun"].payloads.rulership is not None
    assert by_code["sun"].payloads.rulership.rules_houses == rules_by_code["sun"]
    assert by_code["sun"].payloads.rulership.dispositor_code is not None
    assert by_code["moon"].payloads.rulership is not None
    assert by_code["north_node"].payloads.rulership is None
    assert by_code["house_1_cusp"].payloads.rulership is None


def test_natal_chart_objects_expose_motion_payloads_when_positions_have_speeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le pipeline natal rattache la motion quand des vitesses fiables existent."""

    def _positions_with_speeds(
        julian_day: float,
        planet_codes: list[str],
        sign_codes: list[str],
    ) -> list[dict[str, object]]:
        """Produit des positions test avec vitesses existantes sans ephemeride externe."""
        del julian_day
        positions = []
        for index, planet_code in enumerate(planet_codes):
            longitude = float((index * 31) % 360)
            positions.append(
                {
                    "planet_code": planet_code,
                    "longitude": longitude,
                    "sign_code": sign_codes[int(longitude // 30) % len(sign_codes)],
                    "speed_longitude": -0.2 if planet_code == "mars" else 1.0,
                    "is_retrograde": planet_code == "mars",
                }
            )
        return positions

    monkeypatch.setattr(
        natal_calculation,
        "calculate_planet_positions",
        _positions_with_speeds,
    )

    result = _result()
    by_code = {item.code: item for item in result.chart_objects}

    assert by_code["sun"].capabilities.supports_motion is True
    assert by_code["sun"].payloads.motion is not None
    assert by_code["sun"].payloads.motion.direction is PlanetaryMotionDirection.DIRECT
    assert by_code["mars"].capabilities.supports_motion is True
    assert by_code["mars"].payloads.motion is not None
    assert by_code["mars"].payloads.motion.direction is PlanetaryMotionDirection.RETROGRADE
    assert by_code["north_node"].capabilities.supports_motion is False
    assert by_code["north_node"].payloads.motion is None


def test_chart_objects_stay_out_of_public_dump_and_openapi_schema() -> None:
    """La projection runtime interne ne modifie pas la sortie publique."""
    result = _result()
    schemas = app.openapi().get("components", {}).get("schemas", {})

    assert "chart_objects" not in result.model_dump(mode="json")
    assert "chart_objects" not in str(schemas)
