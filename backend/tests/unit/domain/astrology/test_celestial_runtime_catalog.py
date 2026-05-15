"""Tests du catalogue celeste runtime derive du referentiel."""

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_celestial_runtime_catalog_derives_codes_from_runtime_reference() -> None:
    """Les classifications viennent des planetes et angles du referentiel."""
    catalog = CelestialRuntimeCatalog.from_runtime_reference(complete_reference())

    assert catalog.light_body_codes == frozenset({"sun", "moon"})
    assert catalog.outer_planet_codes == frozenset({"uranus", "neptune", "pluto"})
    assert catalog.angle_point_codes == frozenset({"asc", "dsc", "mc", "ic"})
    assert catalog.angular_house_numbers == frozenset({1, 4, 7, 10})
    assert catalog.succedent_house_numbers == frozenset({2, 5, 8, 11})
    assert catalog.body_type_for_code("ASC") == "angle"
    assert catalog.body_type_for_code("mars") == "personal_planet"
