"""Tests du score interprétatif de dominance des maisons."""

from app.domain.astrology.calculators.house_strength import calculate_house_strength
from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
)

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


def test_calculate_house_strength_marks_stellium_luminary_house_dominant() -> None:
    """Une maison angulaire avec stellium et luminaire devient dominante."""
    strength = calculate_house_strength(
        house_number=10,
        occupants=[
            HouseOccupantRuntimeData("sun", "aries", 12.0),
            HouseOccupantRuntimeData("mars", "aries", 15.0),
            HouseOccupantRuntimeData("venus", "taurus", 34.0),
        ],
        ruler=HouseRulerRuntimeData("mars", "aries", 12),
        sign_rulerships=RULERS,
    )

    assert strength.dominant is True
    assert strength.score == 1.0
    assert strength.reasons == [
        "baseline_house",
        "angular_house",
        "occupants_present",
        "stellium_present",
        "luminary_present",
        "ruler_in_own_sign",
        "mc_angle_proximity",
    ]


def test_calculate_house_strength_keeps_empty_cadent_house_non_dominant() -> None:
    """Une maison cadente vide reste faiblement priorisée."""
    strength = calculate_house_strength(
        house_number=6,
        occupants=[],
        ruler=HouseRulerRuntimeData("mercury", "pisces", 12),
        sign_rulerships=RULERS,
    )

    assert strength.dominant is False
    assert strength.score == 0.05
    assert strength.reasons == ["baseline_house", "cadent_house"]
