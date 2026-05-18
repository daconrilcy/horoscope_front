"""Tests du builder runtime des signes natals."""

from app.domain.astrology.builders.sign_runtime_builder import build_sign_runtime_data
from app.domain.astrology.natal_calculation import PlanetPosition
from app.domain.astrology.runtime.sign_runtime_data import SignDominanceReason
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.factories.celestial_catalog_factory import make_celestial_catalog


def test_sign_runtime_builder_returns_twelve_ordered_signs() -> None:
    """Le builder conserve l'ordre des signes fourni par le referentiel."""
    reference = complete_reference()

    runtime = build_sign_runtime_data(
        signs=reference.signs,
        planets=[
            PlanetPosition(
                planet_code="sun",
                longitude=12.0,
                sign_code="aries",
                house_number=1,
            ),
            PlanetPosition(
                planet_code="moon",
                longitude=18.0,
                sign_code="aries",
                house_number=1,
            ),
            PlanetPosition(
                planet_code="mars",
                longitude=24.0,
                sign_code="aries",
                house_number=1,
            ),
        ],
        dignities=reference.dignities,
        celestial_catalog=make_celestial_catalog(),
    )

    assert [item.sign for item in runtime] == list(reference.signs.codes)
    aries = runtime[0]
    assert aries.sign == "aries"
    assert aries.dominant is True
    assert SignDominanceReason.STELLIUM_PRESENT in aries.reasons
    assert aries.active_dignities[0].planet == "mars"


def test_sign_runtime_builder_uses_reference_profiles_when_available() -> None:
    """Les elements et modalites viennent du referentiel et non d'une constante locale."""
    reference = complete_reference()

    runtime = build_sign_runtime_data(
        signs=reference.signs,
        planets=[
            PlanetPosition(
                planet_code="sun",
                longitude=12.0,
                sign_code="aries",
                house_number=1,
            ),
        ],
        dignities=reference.dignities,
        celestial_catalog=make_celestial_catalog(),
    )

    assert runtime[0].element == "fire"
    assert runtime[0].modality == "cardinal"
    assert runtime[0].polarity == "yang"
    assert runtime[1].element == "earth"
    assert SignDominanceReason.REFERENCE_PROFILE in runtime[0].reasons
    assert SignDominanceReason.REFERENCE_PROFILE in runtime[1].reasons
