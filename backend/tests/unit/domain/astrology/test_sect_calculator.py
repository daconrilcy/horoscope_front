"""Tests du calcul de secte natal."""

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

    assert SectCalculator().calculate((_planet("sun", 10),), dignity_reference) == "day"


def test_sect_calculator_returns_night_for_sun_below_horizon() -> None:
    """Le Soleil en maisons 1 a 6 produit une secte nocturne."""
    dignity_reference = complete_reference().dignity_reference

    assert SectCalculator().calculate((_planet("sun", 2),), dignity_reference) == "night"


def test_sect_calculator_requires_sun() -> None:
    """L'absence du Soleil bloque explicitement le calcul."""
    with pytest.raises(ValueError):
        SectCalculator().calculate((_planet("moon", 4),), complete_reference().dignity_reference)
