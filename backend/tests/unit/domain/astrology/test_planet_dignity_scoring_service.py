"""Tests du service de scoring des dignites planetaires."""

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


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
    assert sun.essential_score == 5
    assert sun.accidental_score == 8
    assert sun.total_score == 13
