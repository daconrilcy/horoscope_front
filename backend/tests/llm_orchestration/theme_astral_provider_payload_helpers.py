# Commentaire global: ces helpers partagent les fixtures du payload provider theme_astral.
"""Fabriques de test partagees pour le payload provider theme_astral."""

from __future__ import annotations

from app.domain.astrology.interpretation.natal_fact_graph import NatalFactFamily
from app.domain.astrology.interpretation.natal_theme_taxonomy import BasicThemeCode
from tests.unit.domain.astrology.basic_natal_reading_plan_helpers import (
    build_plan,
    fact,
    theme,
)


def build_basic_reading_plan() -> object:
    """Construit un plan Basic representatif avec plusieurs sections publiques."""
    facts = (
        fact("sun.aries", NatalFactFamily.LUMINARY, ("sun",)),
        fact("moon.cancer", NatalFactFamily.LUMINARY, ("moon",)),
        fact("mercury.gemini", NatalFactFamily.PLANET_POSITION, ("mercury",)),
        fact("venus.taurus", NatalFactFamily.PLANET_POSITION, ("venus",)),
        fact("mars.leo", NatalFactFamily.PLANET_POSITION, ("mars",)),
        fact("jupiter.libra", NatalFactFamily.PLANET_POSITION, ("jupiter",)),
        fact("saturn.capricorn", NatalFactFamily.PLANET_POSITION, ("saturn",)),
        fact("node.virgo", NatalFactFamily.NODE, ("north_node",)),
    )
    themes = (
        theme(BasicThemeCode.CORE_IDENTITY, ("sun.aries",), objects=("sun",)),
        theme(BasicThemeCode.EMOTIONAL_PATTERN, ("moon.cancer",), objects=("moon",)),
        theme(BasicThemeCode.MENTAL_STYLE, ("mercury.gemini",), objects=("mercury",)),
        theme(BasicThemeCode.RESOURCES_AND_VALUES, ("venus.taurus",), objects=("venus",)),
        theme(BasicThemeCode.ACTION_AND_DRIVE, ("mars.leo",), objects=("mars",)),
        theme(BasicThemeCode.RELATIONSHIP_PATTERN, ("jupiter.libra",), objects=("jupiter",)),
        theme(BasicThemeCode.GROWTH_DIRECTION, ("node.virgo",), objects=("north_node",)),
        theme(BasicThemeCode.TENSION_TO_INTEGRATE, ("saturn.capricorn",), objects=("saturn",)),
    )
    return build_plan(facts, themes)
