# Tests de coherence des projections historiques du theme natal.
"""Verifie que les surfaces conservees restent coherentes avec chart_objects."""

from __future__ import annotations

import pytest

from app.domain.astrology import natal_calculation
from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _result() -> NatalResult:
    """Construit un theme natal stable pour les projections CS-224."""
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


def test_planet_positions_match_chart_objects_projection() -> None:
    """Les positions planetaires publiques restent alignees sur chart_objects."""
    result = _result()
    chart_objects_by_code = {item.code: item for item in result.chart_objects}

    for position in result.planet_positions:
        chart_object = chart_objects_by_code[position.planet_code]
        assert chart_object.longitude == position.longitude
        assert chart_object.zodiac_position is not None
        assert chart_object.zodiac_position.sign_code == position.sign_code
        assert chart_object.payloads.house_position is not None
        assert chart_object.payloads.house_position.house_number == position.house_number


def test_dignities_match_chart_object_dignity_payloads() -> None:
    """Les dignites publiques restent projetees dans les payloads objet."""
    result = _result()
    chart_objects_by_code = {item.code: item for item in result.chart_objects}

    for dignity in result.dignities:
        payload = chart_objects_by_code[dignity.planet_code].payloads.dignity
        assert payload is not None
        assert payload.essential_score == dignity.essential_score
        assert payload.accidental_score == dignity.accidental_score
        assert payload.total_score == dignity.total_score
        assert payload.source == "dignities.planet_dignity_scoring_service"


def test_fixed_star_contacts_are_carried_by_chart_object_payloads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Les contacts fixed star restent portes par le payload canonique."""

    def _positions_near_regulus(
        julian_day: float,
        planet_codes: list[str],
        sign_codes: list[str],
    ) -> list[dict[str, object]]:
        """Produit une conjonction stable entre Mars et Regulus."""
        del julian_day
        positions: list[dict[str, object]] = []
        for index, planet_code in enumerate(planet_codes):
            longitude = 150.42 if planet_code == "mars" else float((index * 31) % 360)
            positions.append(
                {
                    "planet_code": planet_code,
                    "longitude": longitude,
                    "sign_code": sign_codes[int(longitude // 30) % len(sign_codes)],
                }
            )
        return positions

    monkeypatch.setattr(natal_calculation, "calculate_planet_positions", _positions_near_regulus)

    result = _result()
    mars_payload = {item.code: item for item in result.chart_objects}[
        "mars"
    ].payloads.fixed_star_conjunctions

    assert len(mars_payload) == 1
    assert mars_payload[0].target_code == "mars"
    assert mars_payload[0].fixed_star_code == "regulus"
    assert mars_payload[0].source == "fixed_star_conjunction_calculator"
    assert "fixed_star_conjunctions" not in NatalResult.model_fields
