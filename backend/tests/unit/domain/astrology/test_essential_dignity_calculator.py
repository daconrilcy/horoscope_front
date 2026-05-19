"""Tests du calculateur de dignites essentielles."""

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.dignities.essential_dignity_calculator import (
    EssentialDignityCalculator,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_essential_dignity_calculator_reads_runtime_rules() -> None:
    """Une dignite essentielle vient des regles runtime, pas d'un mapping local."""
    reference = complete_reference()
    planet = PlanetDignityInput(
        planet_code="sun",
        longitude=120,
        sign_code="leo",
        house_number=10,
        speed_longitude=1,
        is_retrograde=False,
    )

    matches = EssentialDignityCalculator().calculate(
        planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="day",
        tradition="traditional",
    )

    assert matches[0].dignity_type_code == "domicile"
    assert matches[0].score_value == 5
    assert matches[0].reason == "sun in leo: domicile"


def test_essential_dignity_calculator_matches_major_rule_types() -> None:
    """Les dignites majeures configurees sont detectees depuis les regles runtime."""
    reference = complete_reference()

    cases = (
        (PlanetDignityInput("sun", 0, "aries", 10, 1, False), "exaltation"),
        (PlanetDignityInput("sun", 300, "aquarius", 10, 1, False), "detriment"),
        (PlanetDignityInput("sun", 180, "libra", 10, 1, False), "fall"),
    )

    for planet, expected in cases:
        matches = EssentialDignityCalculator().calculate(
            planet,
            signs=reference.signs,
            dignity_reference=reference.dignity_reference,
            score_profile="traditional_standard",
            sect="day",
            tradition="traditional",
        )

        assert expected in {match.dignity_type_code for match in matches}


def test_essential_dignity_calculator_marks_peregrine_without_positive_dignity() -> None:
    """Une planete seulement affaiblie reste peregrine faute de dignite positive."""
    reference = complete_reference()
    planet = PlanetDignityInput("sun", 300, "aquarius", 10, 1, False)

    matches = EssentialDignityCalculator().calculate(
        planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="day",
        tradition="traditional",
    )

    assert {match.dignity_type_code for match in matches} == {"detriment", "peregrine"}


def test_essential_dignity_calculator_marks_peregrine_when_no_rule_matches() -> None:
    """Une planete sans dignite detectee recoit le type peregrine configure."""
    reference = complete_reference()
    planet = PlanetDignityInput(
        planet_code="moon",
        longitude=210,
        sign_code="scorpio",
        house_number=3,
        speed_longitude=1,
        is_retrograde=False,
    )

    matches = EssentialDignityCalculator().calculate(
        planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="night",
        tradition="traditional",
    )

    assert matches == matches
    assert matches[0].dignity_type_code == "peregrine"


def test_essential_dignity_calculator_matches_participating_triplicity_all_sect() -> None:
    """Les maitres participants seedes avec secte `all` sont detectes."""
    reference = complete_reference()
    planet = PlanetDignityInput(
        planet_code="saturn",
        longitude=125,
        sign_code="leo",
        house_number=10,
        speed_longitude=1,
        is_retrograde=False,
    )

    matches = EssentialDignityCalculator().calculate(
        planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="day",
        tradition="traditional",
    )

    assert any(match.dignity_type_code == "triplicity" for match in matches)


def test_essential_dignity_calculator_matches_term_and_face() -> None:
    """Les bornes et faces proviennent du runtime et sont scorées."""
    reference = complete_reference()
    term_planet = PlanetDignityInput("jupiter", 2, "aries", 10, 1, False)
    face_planet = PlanetDignityInput("mars", 5, "aries", 10, 1, False)

    term_matches = EssentialDignityCalculator().calculate(
        term_planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="day",
        tradition="traditional",
    )
    face_matches = EssentialDignityCalculator().calculate(
        face_planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect="day",
        tradition="traditional",
    )

    assert any(match.dignity_type_code == "term" for match in term_matches)
    assert any(match.dignity_type_code == "face" for match in face_matches)
