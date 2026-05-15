"""Tests golden du builder runtime des maisons enrichies."""

from dataclasses import replace

from app.core.config import HouseSystemType
from app.domain.astrology.builders.house_runtime_builder import build_house_runtime_data
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation.house_strength_contracts import (
    HouseStrengthLevel,
    HouseStrengthReason,
)
from app.domain.astrology.natal_calculation import (
    HouseResult,
    NatalCalculationError,
    PlanetPosition,
    _extract_house_axes,
)
from app.domain.astrology.runtime.house_runtime_data import HouseAxisRuntimeData
from app.domain.astrology.runtime.runtime_reference import HouseAxisReferenceData
from tests.factories.astrology_runtime_reference_factory import complete_reference

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

HOUSE_AXIS_REFERENCES = {
    1: HouseAxisRuntimeData(opposite_house=7, theme="self_relationship"),
    2: HouseAxisRuntimeData(opposite_house=8, theme="resources_sharing"),
    3: HouseAxisRuntimeData(opposite_house=9, theme="local_distant"),
    4: HouseAxisRuntimeData(opposite_house=10, theme="private_public"),
    5: HouseAxisRuntimeData(opposite_house=11, theme="creation_collective"),
    6: HouseAxisRuntimeData(opposite_house=12, theme="control_surrender"),
    7: HouseAxisRuntimeData(opposite_house=1, theme="self_relationship"),
    8: HouseAxisRuntimeData(opposite_house=2, theme="resources_sharing"),
    9: HouseAxisRuntimeData(opposite_house=3, theme="local_distant"),
    10: HouseAxisRuntimeData(opposite_house=4, theme="private_public"),
    11: HouseAxisRuntimeData(opposite_house=5, theme="creation_collective"),
    12: HouseAxisRuntimeData(opposite_house=6, theme="control_surrender"),
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
        house_axes=HOUSE_AXIS_REFERENCES,
    )

    house_2 = next(house for house in houses if house.number == 2)
    assert house_2.contained_signs == ["gemini", "cancer", "leo"]
    assert house_2.intercepted_signs == ["cancer"]
    assert house_2.ruler is not None
    assert house_2.house_kind == "succedent"
    assert house_2.ruler.planet == "mercury"
    assert house_2.occupants[0].planet == "sun"
    assert house_2.axis.opposite_house == 8
    assert house_2.axis.theme == "resources_sharing"
    assert house_2.strength.level is HouseStrengthLevel.MODERATE
    assert house_2.strength.reasons == (
        HouseStrengthReason.BASELINE_HOUSE,
        HouseStrengthReason.SUCCEDENT_HOUSE,
        HouseStrengthReason.OCCUPANTS_PRESENT,
        HouseStrengthReason.LUMINARY_PRESENT,
        HouseStrengthReason.RULER_IN_OWN_SIGN,
    )


def test_runtime_builder_golden_whole_sign_without_interception() -> None:
    """Golden Whole Sign: les interceptions sont impossibles."""
    houses = build_house_runtime_data(
        houses=_whole_sign_houses(),
        planets=[],
        house_rulers=[],
        house_system="whole_sign",
        sign_rulerships=RULERS,
        house_axes=HOUSE_AXIS_REFERENCES,
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
        house_axes=HOUSE_AXIS_REFERENCES,
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
        house_axes=HOUSE_AXIS_REFERENCES,
    )

    house_2 = next(house for house in houses if house.number == 2)
    assert len(house_2.occupants) == 3
    assert house_2.strength.dominant is True
    assert HouseStrengthReason.STELLIUM_PRESENT in house_2.strength.reasons


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
        house_axes=HOUSE_AXIS_REFERENCES,
    )

    house_6 = next(house for house in houses if house.number == 6)
    assert house_6.occupants == []
    assert house_6.strength.dominant is False
    assert house_6.strength.reasons == (
        HouseStrengthReason.BASELINE_HOUSE,
        HouseStrengthReason.CADENT_HOUSE,
    )


def test_runtime_builder_rejects_missing_house_axis() -> None:
    """Un axe absent du referentiel provoque une erreur explicite."""
    incomplete_axes = dict(HOUSE_AXIS_REFERENCES)
    del incomplete_axes[6]

    try:
        build_house_runtime_data(
            houses=_houses_with_interception(),
            planets=[],
            house_rulers=[],
            house_system="placidus",
            sign_rulerships=RULERS,
            house_axes=incomplete_axes,
        )
    except ValueError as error:
        assert str(error) == "missing house axis reference for house 6"
    else:
        raise AssertionError("expected missing house axis error")


def test_reference_house_axes_extraction_rejects_incomplete_payload() -> None:
    """La validation de calcul natal refuse un referentiel sans les douze axes."""
    reference = replace(
        complete_reference(),
        house_axes=(
            HouseAxisReferenceData(
                house_number=1,
                opposite_house=7,
                theme="self_relationship",
            ),
        ),
    )

    try:
        _extract_house_axes("test-version", reference)
    except NatalCalculationError as error:
        assert error.code == "invalid_reference_data"
        assert error.details == {
            "reference_version": "test-version",
            "field": "house_axes",
            "reason": "missing_house",
        }
    else:
        raise AssertionError("expected incomplete house axes reference error")


def test_reference_house_axes_extraction_rejects_coerced_numbers() -> None:
    """Les numeros d'axes doivent etre des entiers stricts, pas des valeurs coercibles."""
    reference = replace(
        complete_reference(),
        house_axes=(
            HouseAxisReferenceData(
                house_number=True,
                opposite_house=7,
                theme="self_relationship",
            ),
        ),
    )

    try:
        _extract_house_axes("test-version", reference)
    except NatalCalculationError as error:
        assert error.details["reason"] == "invalid_house_numbers"
    else:
        raise AssertionError("expected invalid house axis number error")
