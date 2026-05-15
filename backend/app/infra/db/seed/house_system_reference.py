"""Seed SQL canonique des systèmes de maisons astrologiques."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import AstralHouseSystemModel

HOUSE_SYSTEM_SEED_DATA = {
    "placidus": {
        "name": "Placidus",
        "description": (
            "Quadrant house system widely used in modern Western astrology. Houses are "
            "calculated from time-based divisions of the diurnal arc."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": False,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 10,
    },
    "whole_sign": {
        "name": "Whole Sign",
        "description": (
            "Ancient house system where each house corresponds to one full zodiac sign, "
            "starting from the Ascendant sign."
        ),
        "astronomical_family": "sign_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": False,
        "sort_order": 20,
    },
    "equal": {
        "name": "Equal House",
        "description": (
            "House system where all houses are exactly 30 degrees, starting from the "
            "Ascendant degree."
        ),
        "astronomical_family": "ascendant_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": True,
        "sort_order": 30,
    },
    "porphyry": {
        "name": "Porphyry",
        "description": (
            "Quadrant house system dividing each quadrant between Ascendant, Midheaven, "
            "Descendant and Imum Coeli into three equal parts."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": True,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 40,
    },
}


def sync_house_system_seed_data(session: Session) -> None:
    """Garantit les lignes SQL canoniques des systèmes de maisons."""
    for code, payload in HOUSE_SYSTEM_SEED_DATA.items():
        house_system = session.scalar(
            select(AstralHouseSystemModel).where(AstralHouseSystemModel.code == code)
        )
        if house_system is None:
            session.add(AstralHouseSystemModel(code=code, **payload))
            continue
        for field_name, value in payload.items():
            setattr(house_system, field_name, value)


def ensure_house_system_reference_data(session: Session) -> None:
    """Compatibilite applicative pour garantir le referentiel des maisons."""
    sync_house_system_seed_data(session)
