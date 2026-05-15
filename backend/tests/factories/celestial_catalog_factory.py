"""Factory de catalogue celeste runtime pour les tests unitaires."""

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from tests.factories.astrology_runtime_reference_factory import complete_reference


def make_celestial_catalog() -> CelestialRuntimeCatalog:
    """Construit le catalogue celeste depuis une reference runtime complete."""
    return CelestialRuntimeCatalog.from_runtime_reference(complete_reference())
