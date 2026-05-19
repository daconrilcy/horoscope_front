"""Tests du calculateur de dignites accidentelles."""

from app.domain.astrology.dignities.accidental_dignity_calculator import (
    AccidentalDignityCalculator,
)
from app.domain.astrology.dignities.contracts import PlanetDignityInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _planet(
    code: str,
    longitude: float,
    house: int,
    is_retrograde: bool = False,
) -> PlanetDignityInput:
    """Construit une position planétaire factuelle."""
    return PlanetDignityInput(
        planet_code=code,
        longitude=longitude,
        sign_code="aries",
        house_number=house,
        speed_longitude=-0.1 if is_retrograde else 0.1,
        is_retrograde=is_retrograde,
    )


def test_accidental_dignity_calculator_detects_house_rule_from_runtime() -> None:
    """La maison angulaire est detectee depuis la regle accidentelle runtime."""
    reference = complete_reference()
    sun = _planet("sun", 0, 10)

    matches = AccidentalDignityCalculator().calculate(
        sun,
        all_planets=(sun,),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
    )

    assert {match.dignity_type_code for match in matches} == {
        "angular_house",
        "direct_motion",
        "swift_motion",
    }
    angular_match = next(match for match in matches if match.dignity_type_code == "angular_house")
    assert angular_match.score_value == 4


def test_accidental_dignity_calculator_detects_house_modalities_motion_and_joy() -> None:
    """Les maisons, mouvements et joie planetaire viennent des regles runtime."""
    reference = complete_reference()
    direct_succedent = _planet("venus", 40, 5, False)
    retro_cadent_joy = _planet("moon", 90, 3, True)

    direct_matches = AccidentalDignityCalculator().calculate(
        direct_succedent,
        all_planets=(direct_succedent,),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
    )
    retro_matches = AccidentalDignityCalculator().calculate(
        retro_cadent_joy,
        all_planets=(retro_cadent_joy,),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
    )

    assert {match.dignity_type_code for match in direct_matches} == {
        "succedent_house",
        "direct_motion",
        "swift_motion",
    }
    assert {match.dignity_type_code for match in retro_matches} == {
        "cadent_house",
        "retrograde",
        "planetary_joy",
        "slow_motion",
    }


def test_accidental_dignity_calculator_excludes_sun_from_solar_distance() -> None:
    """Le Soleil ne se score jamais lui-même en condition solaire."""
    reference = complete_reference()
    sun = _planet("sun", 0, 10)

    matches = AccidentalDignityCalculator().calculate(
        sun,
        all_planets=(sun,),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
    )

    assert not {
        "cazimi",
        "combust",
        "under_sunbeams",
        "free_from_sunbeams",
    } & {match.dignity_type_code for match in matches}


def test_accidental_dignity_calculator_prioritizes_exclusive_solar_conditions() -> None:
    """Une seule condition solaire exclusive est conservée selon la distance."""
    reference = complete_reference()
    sun = _planet("sun", 0, 10)
    cazimi_mercury = _planet("mercury", 0.1, 10)
    combust_mercury = _planet("mercury", 5, 10)
    beamed_mercury = _planet("mercury", 12, 10)

    for planet, expected in (
        (cazimi_mercury, "cazimi"),
        (combust_mercury, "combust"),
        (beamed_mercury, "under_sunbeams"),
    ):
        matches = AccidentalDignityCalculator().calculate(
            planet,
            all_planets=(sun, planet),
            dignity_reference=reference.dignity_reference,
            score_profile="traditional_standard",
            tradition="traditional",
        )
        solar_matches = [
            match.dignity_type_code
            for match in matches
            if match.dignity_type_code in {"cazimi", "combust", "under_sunbeams"}
        ]
        assert solar_matches == [expected]


def test_accidental_dignity_calculator_detects_advanced_runtime_sources() -> None:
    """Les sources CS-195 sont detectees dans le calcul accidentel reel."""
    reference = complete_reference()
    sun = PlanetDignityInput("sun", 10, "aries", 10, 0.01, False)
    venus = PlanetDignityInput("venus", 250, "taurus", 5, 0.02, False)

    sun_matches = AccidentalDignityCalculator().calculate(
        sun,
        all_planets=(sun, venus),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
        sect="day",
        signs=reference.signs,
    )
    venus_matches = AccidentalDignityCalculator().calculate(
        venus,
        all_planets=(sun, venus),
        dignity_reference=reference.dignity_reference,
        score_profile="traditional_standard",
        tradition="traditional",
        sect="day",
        signs=reference.signs,
    )

    assert {"stationary", "hayz"} <= {match.dignity_type_code for match in sun_matches}
    assert {"slow_motion", "occidental"} <= {match.dignity_type_code for match in venus_matches}
