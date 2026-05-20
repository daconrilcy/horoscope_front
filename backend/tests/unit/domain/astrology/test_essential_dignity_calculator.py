"""Tests du calculateur de dignites essentielles."""

from dataclasses import replace

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.dignities.essential_dignity_calculator import (
    EssentialDignityCalculator,
)
from app.domain.astrology.runtime.runtime_reference import TriplicityRulerReferenceData
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


def test_essential_dignity_calculator_uses_day_triplicity_ruler_for_day_chart() -> None:
    """La triplicite active le maitre diurne sans activer le maitre nocturne."""
    reference = _reference_with_fire_day_and_night_triplicity()
    day_ruler = PlanetDignityInput("jupiter", 125, "leo", 10, 1, False)
    night_ruler = PlanetDignityInput("mars", 125, "leo", 10, 1, False)

    day_matches = _essential_matches(day_ruler, reference, sect="day")
    night_matches = _essential_matches(night_ruler, reference, sect="day")

    assert "triplicity" in {match.dignity_type_code for match in day_matches}
    assert "triplicity" not in {match.dignity_type_code for match in night_matches}


def test_essential_dignity_calculator_uses_night_triplicity_ruler_for_night_chart() -> None:
    """La triplicite active le maitre nocturne pour le meme element."""
    reference = _reference_with_fire_day_and_night_triplicity()
    day_ruler = PlanetDignityInput("jupiter", 125, "leo", 2, 1, False)
    night_ruler = PlanetDignityInput("mars", 125, "leo", 2, 1, False)

    day_matches = _essential_matches(day_ruler, reference, sect="night")
    night_matches = _essential_matches(night_ruler, reference, sect="night")

    assert "triplicity" not in {match.dignity_type_code for match in day_matches}
    assert "triplicity" in {match.dignity_type_code for match in night_matches}


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


def _reference_with_fire_day_and_night_triplicity():
    """Retourne une reference de test avec maitres diurne et nocturne du feu."""
    reference = complete_reference()
    dignity_reference = reference.dignity_reference
    triplicity_rulers = tuple(
        ruler
        for ruler in dignity_reference.triplicity_rulers
        if not (ruler.element_code == "fire" and ruler.sect_code in {"day", "night"})
    )
    return replace(
        reference,
        dignity_reference=replace(
            dignity_reference,
            triplicity_rulers=(
                *triplicity_rulers,
                TriplicityRulerReferenceData("fire", "day", "jupiter", "principal", "traditional"),
                TriplicityRulerReferenceData("fire", "night", "mars", "principal", "traditional"),
            ),
        ),
    )


def _essential_matches(planet: PlanetDignityInput, reference, *, sect: str):
    """Calcule les dignites essentielles d'une planete avec la fixture donnee."""
    return EssentialDignityCalculator().calculate(
        planet,
        signs=reference.signs,
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        sect=sect,
        tradition="traditional",
    )
