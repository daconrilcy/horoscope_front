"""Tests des contrats immutables de dignites planetaires."""

from dataclasses import FrozenInstanceError

import pytest

from app.domain.astrology.dignities.contracts import (
    ChartSectResult,
    EssentialDignityMatch,
    PlanetDignityInput,
    PlanetDignityResult,
)


def test_dignity_contracts_are_immutable_and_typed() -> None:
    """Les contrats domaine ne transportent pas de dictionnaire libre mutable."""
    match = EssentialDignityMatch(
        dignity_type_code="domicile",
        score_value=5,
        source="essential_rule",
        reason="sun in leo: domicile",
        sign_code="leo",
        degree_start=0,
        degree_end=30,
    )
    result = PlanetDignityResult(
        planet_code="sun",
        score_profile="traditional_standard",
        tradition="traditional",
        reference_version="1.0.0",
        sect="day",
        chart_sect=ChartSectResult(
            chart_sect="day",
            sun_horizon_position="above_horizon",
            sun_above_horizon=True,
            calculation_basis="sun_house_horizon_rule",
            reference_system="traditional",
        ),
        essential_score=5,
        accidental_score=0,
        total_score=5,
        functional_strength_score=1,
        expression_quality_score=0.7,
        intensity_score=0.6,
        essential_breakdown=(match,),
        accidental_breakdown=(),
    )

    with pytest.raises(FrozenInstanceError):
        result.total_score = 0  # type: ignore[misc]

    assert isinstance(result.essential_breakdown, tuple)
    assert not hasattr(result, "__dict__")
    assert result.chart_sect.chart_sect == result.sect


def test_planet_dignity_input_exposes_degree_in_sign() -> None:
    """La position locale dans le signe reste derivee de la longitude."""
    planet = PlanetDignityInput(
        planet_code="mars",
        longitude=52.5,
        sign_code="taurus",
        house_number=10,
        speed_longitude=0.4,
        is_retrograde=False,
    )

    assert planet.degree_in_sign == pytest.approx(22.5)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {
                "chart_sect": "dawn",
                "sun_horizon_position": "above_horizon",
                "sun_above_horizon": True,
                "calculation_basis": "sun_house_horizon_rule",
                "reference_system": "traditional",
            },
            "chart_sect must be day or night",
        ),
        (
            {
                "chart_sect": "day",
                "sun_horizon_position": "below_horizon",
                "sun_above_horizon": True,
                "calculation_basis": "sun_house_horizon_rule",
                "reference_system": "traditional",
            },
            "chart_sect and sun_horizon_position are inconsistent",
        ),
        (
            {
                "chart_sect": "night",
                "sun_horizon_position": "below_horizon",
                "sun_above_horizon": True,
                "calculation_basis": "sun_house_horizon_rule",
                "reference_system": "traditional",
            },
            "chart_sect and sun_above_horizon are inconsistent",
        ),
    ],
)
def test_chart_sect_result_rejects_invalid_contract(
    payload: dict[str, object], message: str
) -> None:
    """Le contrat de secte refuse les valeurs hors domaine public."""
    with pytest.raises(ValueError, match=message):
        ChartSectResult(**payload)  # type: ignore[arg-type]
