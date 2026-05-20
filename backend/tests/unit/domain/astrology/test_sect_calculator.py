"""Tests du calcul de secte natal."""

from dataclasses import replace

import pytest

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.dignities.sect_calculator import SectCalculator
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _planet(code: str, house: int) -> PlanetDignityInput:
    """Construit une position minimale de test."""
    return PlanetDignityInput(
        planet_code=code,
        longitude=0,
        sign_code="aries",
        house_number=house,
        speed_longitude=None,
        is_retrograde=False,
    )


def test_sect_calculator_returns_day_for_sun_above_horizon() -> None:
    """Le Soleil en maisons 7 a 12 produit une secte diurne."""
    dignity_reference = complete_reference().dignity_reference

    result = SectCalculator().calculate((_planet("sun", 10),), dignity_reference)

    assert result.chart_sect == "day"
    assert result.sun_horizon_position == "above_horizon"
    assert result.sun_above_horizon is True
    assert result.calculation_basis == "sun_house_horizon_rule"
    assert result.reference_system == "traditional"


def test_sect_calculator_returns_night_for_sun_below_horizon() -> None:
    """Le Soleil en maisons 1 a 6 produit une secte nocturne."""
    dignity_reference = complete_reference().dignity_reference

    result = SectCalculator().calculate((_planet("sun", 2),), dignity_reference)

    assert result.chart_sect == "night"
    assert result.sun_horizon_position == "below_horizon"
    assert result.sun_above_horizon is False
    assert result.calculation_basis == "sun_house_horizon_rule"
    assert result.reference_system == "traditional"


def test_sect_calculator_requires_sun() -> None:
    """L'absence du Soleil bloque explicitement le calcul."""
    with pytest.raises(ValueError):
        SectCalculator().calculate((_planet("moon", 4),), complete_reference().dignity_reference)


@pytest.mark.parametrize("dignity_type_code", ["above_horizon", "below_horizon"])
def test_sect_calculator_requires_horizon_runtime_rules(dignity_type_code: str) -> None:
    """L'absence des regles horizon runtime bloque explicitement le calcul."""
    dignity_reference = complete_reference().dignity_reference
    without_horizon_rule = replace(
        dignity_reference,
        accidental_rules=tuple(
            rule
            for rule in dignity_reference.accidental_rules
            if rule.dignity_type_code != dignity_type_code
        ),
    )

    with pytest.raises(ValueError, match=f"missing horizon dignity rule: {dignity_type_code}"):
        SectCalculator().calculate((_planet("sun", 10),), without_horizon_rule)
