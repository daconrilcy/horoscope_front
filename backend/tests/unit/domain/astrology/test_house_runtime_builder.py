"""Tests golden du builder runtime des maisons enrichies."""

from app.core.config import HouseSystemType
from app.domain.astrology.builders.house_runtime_builder import build_house_runtime_data
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.natal_calculation import HouseResult, PlanetPosition

RULERS = {
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


def _houses_with_interception() -> list[HouseResult]:
    """Crée un jeu Placidus stable avec interception Cancer en maison 2."""
    cusps = {
        1: 42.0,
        2: 75.0,
        3: 142.0,
        4: 170.0,
        5: 198.0,
        6: 228.0,
        7: 252.0,
        8: 285.0,
        9: 322.0,
        10: 350.0,
        11: 18.0,
        12: 38.0,
    }
    return [HouseResult(number=number, cusp_longitude=cusps[number]) for number in range(1, 13)]


def _whole_sign_houses() -> list[HouseResult]:
    """Crée douze maisons Whole Sign alignées sur les signes."""
    return [
        HouseResult(number=number, cusp_longitude=float((number - 1) * 30))
        for number in range(1, 13)
    ]


def test_runtime_builder_golden_placidus_with_interception_and_three_signs() -> None:
    """Golden Placidus: une maison contenant trois signes expose Cancer intercepté."""
    houses = build_house_runtime_data(
        houses=_houses_with_interception(),
        planets=[
            PlanetPosition(
                planet_code="sun",
                longitude=80.0,
                sign_code="gemini",
                house_number=2,
            ),
        ],
        house_rulers=[
            HouseRulerResult(
                house_number=2,
                cusp_sign="gemini",
                ruler_planet="mercury",
                ruler_planet_sign="virgo",
                ruler_planet_house=5,
            ),
        ],
        house_system="placidus",
        sign_rulerships=RULERS,
    )

    house_2 = next(house for house in houses if house.number == 2)
    assert house_2.contained_signs == ["gemini", "cancer", "leo"]
    assert house_2.intercepted_signs == ["cancer"]
    assert house_2.ruler is not None
    assert house_2.house_kind == "succedent"
    assert house_2.ruler.planet == "mercury"
    assert house_2.occupants[0].planet == "sun"
    assert house_2.axis.opposite_house == 8
    assert house_2.strength.reasons == [
        "baseline_house",
        "succedent_house",
        "occupants_present",
        "luminary_present",
        "ruler_in_own_sign",
    ]


def test_runtime_builder_golden_whole_sign_without_interception() -> None:
    """Golden Whole Sign: les interceptions sont impossibles."""
    houses = build_house_runtime_data(
        houses=_whole_sign_houses(),
        planets=[],
        house_rulers=[],
        house_system="whole_sign",
        sign_rulerships=RULERS,
    )

    assert all(house.intercepted_signs == [] for house in houses)


def test_runtime_builder_whole_sign_enum_without_interception() -> None:
    """Le chemin runtime avec enum Whole Sign bloque aussi les interceptions."""
    houses = build_house_runtime_data(
        houses=_houses_with_interception(),
        planets=[],
        house_rulers=[],
        house_system=HouseSystemType.WHOLE_SIGN,
        sign_rulerships=RULERS,
    )

    assert all(house.intercepted_signs == [] for house in houses)


def test_runtime_builder_golden_stellium_house_is_dominant() -> None:
    """Golden stellium: trois occupants avec luminaire rendent la maison dominante."""
    houses = build_house_runtime_data(
        houses=_houses_with_interception(),
        planets=[
            PlanetPosition(
                planet_code="sun",
                longitude=80.0,
                sign_code="gemini",
                house_number=2,
            ),
            PlanetPosition(
                planet_code="moon",
                longitude=92.0,
                sign_code="cancer",
                house_number=2,
            ),
            PlanetPosition(
                planet_code="mars",
                longitude=118.0,
                sign_code="cancer",
                house_number=2,
            ),
        ],
        house_rulers=[],
        house_system="placidus",
        sign_rulerships=RULERS,
    )

    house_2 = next(house for house in houses if house.number == 2)
    assert len(house_2.occupants) == 3
    assert house_2.strength.dominant is True
    assert "stellium_present" in house_2.strength.reasons


def test_runtime_builder_golden_empty_house_remains_non_dominant() -> None:
    """Golden maison vide: aucun occupant ne crée de dominance artificielle."""
    houses = build_house_runtime_data(
        houses=_houses_with_interception(),
        planets=[
            PlanetPosition(
                planet_code="sun",
                longitude=80.0,
                sign_code="gemini",
                house_number=2,
            )
        ],
        house_rulers=[],
        house_system="placidus",
        sign_rulerships=RULERS,
    )

    house_6 = next(house for house in houses if house.number == 6)
    assert house_6.occupants == []
    assert house_6.strength.dominant is False
    assert house_6.strength.reasons == ["baseline_house", "cadent_house"]
