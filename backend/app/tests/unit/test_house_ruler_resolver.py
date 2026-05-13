"""Tests unitaires du resolver des maîtres de maisons natales."""

import pytest
from pydantic import BaseModel

from app.domain.astrology.house_ruler_resolver import (
    HouseRulerResolutionError,
    HouseRulerResolver,
)
from app.domain.astrology.natal_calculation import HouseResult, PlanetPosition

COMPLETE_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


class PlanetStub(BaseModel):
    """Position planétaire minimale pour tester les cas dégradés."""

    planet_code: str
    sign_code: str
    house_number: int | None


def test_resolve_house_rulers_from_cusp_sign_and_planet_position() -> None:
    """Vérifie la chaîne cuspide -> signe -> maître -> placement."""
    houses = [
        HouseResult(number=7, cusp_longitude=42.5),
        HouseResult(number=10, cusp_longitude=121.0),
    ]
    planets = [
        PlanetPosition(
            planet_code="venus",
            longitude=132.0,
            sign_code="leo",
            house_number=10,
        ),
        PlanetPosition(
            planet_code="sun",
            longitude=250.0,
            sign_code="sagittarius",
            house_number=5,
        ),
    ]

    result = HouseRulerResolver(COMPLETE_RULERS).resolve(houses, planets)

    assert [item.model_dump() for item in result] == [
        {
            "house_number": 7,
            "cusp_sign": "taurus",
            "ruler_planet": "venus",
            "ruler_planet_sign": "leo",
            "ruler_planet_house": 10,
        },
        {
            "house_number": 10,
            "cusp_sign": "leo",
            "ruler_planet": "sun",
            "ruler_planet_sign": "sagittarius",
            "ruler_planet_house": 5,
        },
    ]


def test_resolve_rejects_missing_reference_mapping() -> None:
    """Refuse un calcul sans dignités planétaires canoniques."""
    with pytest.raises(HouseRulerResolutionError, match="missing sign rulerships"):
        HouseRulerResolver()


def test_resolve_rejects_partial_reference_mapping() -> None:
    """Refuse un référentiel partiel au lieu d'inventer un fallback local."""
    with pytest.raises(HouseRulerResolutionError, match="taurus"):
        HouseRulerResolver({"aries": "mars"})


def test_resolve_accepts_ruler_planet_without_house() -> None:
    """Préserve une maison de maître inconnue en mode de calcul dégradé."""
    houses = [HouseResult(number=7, cusp_longitude=42.5)]
    planets = [PlanetStub(planet_code="venus", sign_code="leo", house_number=None)]

    result = HouseRulerResolver(COMPLETE_RULERS).resolve(houses, planets)

    assert result[0].ruler_planet == "venus"
    assert result[0].ruler_planet_sign == "leo"
    assert result[0].ruler_planet_house is None


def test_resolve_rejects_invalid_house_number() -> None:
    """Bloque la sérialisation d'une maison hors du référentiel 1 à 12."""
    houses = [HouseResult(number=13, cusp_longitude=42.5)]
    planets = [PlanetStub(planet_code="venus", sign_code="leo", house_number=10)]

    with pytest.raises(HouseRulerResolutionError, match="invalid house number: 13"):
        HouseRulerResolver(COMPLETE_RULERS).resolve(houses, planets)
