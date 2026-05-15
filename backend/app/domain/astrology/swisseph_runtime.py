"""Isole le chargement paresseux de SwissEph pour les providers astrology."""

from __future__ import annotations

from types import ModuleType


def load_swisseph() -> ModuleType:
    """Retourne le module SwissEph installe dans l'environnement courant."""
    import swisseph as swe  # type: ignore[import-untyped]

    return swe
