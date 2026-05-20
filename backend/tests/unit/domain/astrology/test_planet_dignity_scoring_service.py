"""Tests du service de scoring des dignites planetaires."""

from dataclasses import replace

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    DignityConditionValue,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _reference_with_planet_sect_rules():
    """Ajoute les regles runtime de secte planetaire necessaires au test."""
    reference = complete_reference()
    dignity_reference = reference.dignity_reference
    rules = tuple(
        AccidentalDignityRuleReferenceData(
            dignity_type_code="in_sect",
            planet_code=planet_code,
            condition_schema_code="sect_condition",
            conditions=(DignityConditionValue("chart_sect_code", sect_code),),
            system_code="traditional",
        )
        for planet_code, sect_code in (
            ("sun", "day"),
            ("jupiter", "day"),
            ("saturn", "day"),
            ("moon", "night"),
            ("venus", "night"),
            ("mars", "night"),
            ("mercury", "all"),
        )
    )
    return replace(
        reference,
        dignity_reference=replace(
            dignity_reference,
            accidental_rules=(*dignity_reference.accidental_rules, *rules),
        ),
    )


def test_planet_dignity_scoring_service_aggregates_fact_scores() -> None:
    """Le service agrege essentiels, accidentels et poids sans interpretation."""
    reference = complete_reference()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 10, 1, False),
        PlanetDignityInput("moon", 210, "scorpio", 3, 1, False),
    )

    results = PlanetDignityScoringService().calculate(planets, reference)
    sun = next(result for result in results if result.planet_code == "sun")

    assert sun.score_profile == "traditional_standard"
    assert sun.tradition == "traditional"
    assert sun.sect == "day"
    assert sun.chart_sect.chart_sect == "day"
    assert sun.chart_sect.sun_horizon_position == "above_horizon"
    assert all(result.chart_sect is sun.chart_sect for result in results)
    assert sun.essential_score == 5
    assert sun.accidental_score == 8
    assert sun.total_score == 13


def test_planet_dignity_scoring_service_derives_night_sect_conditions() -> None:
    """Les planetes nocturnes deviennent en secte dans un theme nocturne."""
    reference = _reference_with_planet_sect_rules()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 2, 1, False),
        PlanetDignityInput("moon", 210, "scorpio", 3, 1, False),
        PlanetDignityInput("mars", 15, "aries", 6, 1, False),
        PlanetDignityInput("jupiter", 130, "leo", 11, 1, False),
    )

    results = PlanetDignityScoringService().calculate(planets, reference)
    by_planet = {result.planet_code: result for result in results}

    assert by_planet["sun"].chart_sect.chart_sect == "night"
    assert by_planet["moon"].sect_condition.planet_sect_condition == "in_sect"
    assert by_planet["moon"].sect_condition.intrinsic_sect == "nocturnal"
    assert by_planet["mars"].sect_condition.planet_sect_condition == "in_sect"
    assert by_planet["jupiter"].sect_condition.planet_sect_condition == "out_of_sect"


def test_planet_dignity_scoring_service_derives_day_sect_and_mercury_common() -> None:
    """Les regles runtime classent le jour et Mercure commun sans mapping local."""
    reference = _reference_with_planet_sect_rules()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 10, 1, False),
        PlanetDignityInput("mercury", 80, "gemini", 1, 1, False),
        PlanetDignityInput("moon", 210, "scorpio", 3, 1, False),
    )

    results = PlanetDignityScoringService().calculate(planets, reference)
    sun = next(result for result in results if result.planet_code == "sun")
    mercury = next(result for result in results if result.planet_code == "mercury")
    moon = next(result for result in results if result.planet_code == "moon")

    assert sun.sect_condition.planet_sect_condition == "in_sect"
    assert sun.sect_condition.intrinsic_sect == "diurnal"
    assert moon.sect_condition.planet_sect_condition == "out_of_sect"
    assert moon.sect_condition.intrinsic_sect == "nocturnal"
    assert mercury.sect_condition.intrinsic_sect == "common"
    assert mercury.sect_condition.planet_sect_condition == "variable_by_condition"
    assert mercury.sect_condition.is_in_sect is False
    assert mercury.sect_condition.is_out_of_sect is False


def test_planet_dignity_scoring_service_marks_missing_runtime_profile_unknown() -> None:
    """Une planete sans profil runtime explicite ne reçoit pas de fallback local."""
    reference = _reference_with_planet_sect_rules()
    planets = (
        PlanetDignityInput("sun", 120, "leo", 10, 1, False),
        PlanetDignityInput("uranus", 80, "gemini", 1, 1, False),
    )

    results = PlanetDignityScoringService().calculate(planets, reference)
    uranus = next(result for result in results if result.planet_code == "uranus")

    assert uranus.sect_condition.intrinsic_sect == "unknown"
    assert uranus.sect_condition.planet_sect_condition == "unknown"
    assert uranus.sect_condition.is_in_sect is False
    assert uranus.sect_condition.is_out_of_sect is False
