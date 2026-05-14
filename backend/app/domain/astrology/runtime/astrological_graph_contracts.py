"""Contrats de readiness pour un futur graphe astrologique.

Ce module nomme les types de noeuds et relations sans introduire de moteur de
graphe complet ni de dependance produit.
"""

from __future__ import annotations

from enum import StrEnum


class AstrologicalGraphNodeType(StrEnum):
    """Types de noeuds attendus dans le graphe astrologique futur."""

    PLANET = "planet"
    SIGN = "sign"
    HOUSE = "house"
    ASPECT = "aspect"
    RULER = "ruler"
    PATTERN = "pattern"


class AstrologicalGraphEdgeType(StrEnum):
    """Types d'aretes attendus dans le graphe astrologique futur."""

    OCCUPIES = "occupies"
    RULES = "rules"
    ASPECTS = "aspects"
    PARTICIPATES_IN = "participates_in"
    MODIFIES = "modifies"
