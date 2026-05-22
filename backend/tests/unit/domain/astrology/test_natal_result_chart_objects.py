"""Tests d'integration de `chart_objects` dans le resultat natal."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
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


def test_chart_objects_stay_out_of_public_dump_and_openapi_schema() -> None:
    """La projection runtime interne ne modifie pas la sortie publique."""
    result = _result()
    schemas = app.openapi().get("components", {}).get("schemas", {})

    assert "chart_objects" not in result.model_dump(mode="json")
    assert "chart_objects" not in str(schemas)
