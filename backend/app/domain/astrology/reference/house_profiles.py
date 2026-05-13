"""Profils astrologiques stables des maisons.

Ces contrats de reference decrivent la qualite astrologique d'une maison sans
exposer de poids, priorite ou categorie produit.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HouseAstrologyProfile:
    """Profil astrologique stable d'une maison astrale."""

    house_id: int
    house_number: int
    name: str
    house_kind: str
    natural_theme: str | None = None
