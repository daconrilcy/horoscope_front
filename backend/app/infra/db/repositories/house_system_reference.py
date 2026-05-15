"""Seed SQL canonique des systèmes de maisons astrologiques."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import AstralHouseSystemModel


def _house_system_payload(row: dict[str, object]) -> dict[str, object]:
    """Normalise une ligne documentaire pour le modèle SQL des systèmes de maisons."""
    return {
        "name": str(row["name"]),
        "description": None if row.get("description") is None else str(row["description"]),
        "astronomical_family": str(row["astronomical_family"]),
        "supports_polar_regions": bool(row["supports_polar_regions"]),
        "is_quadrant_based": bool(row["is_quadrant_based"]),
        "requires_precise_birth_time": bool(row["requires_precise_birth_time"]),
        "sort_order": int(row["sort_order"]),
    }


def sync_house_system_seed_data(session: Session) -> None:
    """Garantit les lignes SQL canoniques des systèmes de maisons depuis le JSON."""
    from app.infra.db.repositories.astrology_reference_sources import load_astral_house_system_rows

    for row in load_astral_house_system_rows():
        code = str(row["code"])
        payload = _house_system_payload(row)
        house_system = session.scalar(
            select(AstralHouseSystemModel).where(AstralHouseSystemModel.code == code)
        )
        if house_system is None:
            session.add(AstralHouseSystemModel(id=int(row["id"]), code=code, **payload))
            continue
        for field_name, value in payload.items():
            setattr(house_system, field_name, value)


def ensure_house_system_reference_data(session: Session) -> None:
    """Compatibilite applicative pour garantir le referentiel des maisons."""
    sync_house_system_seed_data(session)
