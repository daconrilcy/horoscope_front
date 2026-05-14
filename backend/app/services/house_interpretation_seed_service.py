"""Synchronise le vocabulaire éditorial des interprétations de maisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AstralSystemModel,
    HouseInterpretationProfileModel,
    HouseModel,
    ReferenceVersionModel,
)

SOURCE_KEY = "house_interpretation_profiles"
DEFAULT_LANGUAGE = "en"
JSON_FIELD_NAMES = (
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_keywords_json",
    "material_keywords_json",
    "relationship_keywords_json",
    "career_keywords_json",
    "health_keywords_json",
    "spiritual_keywords_json",
    "body_parts_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
)


def _house_interpretation_source_path() -> Path:
    """Retourne le chemin du JSON documentaire des profils de maisons."""
    repo_root = Path(__file__).resolve().parents[3]
    source_path = repo_root / "docs" / "recherches astro" / "house_interpretation_vocabulary.json"
    if source_path.exists():
        return source_path
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "recherches astro"
        / "house_interpretation_vocabulary.json"
    )


def load_house_interpretation_profiles_source() -> list[dict[str, Any]]:
    """Charge et valide la source JSON des profils éditoriaux de maisons."""
    source_path = _house_interpretation_source_path()
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict):
        raise ValueError("house interpretation source must be an object")
    rows = raw.get(SOURCE_KEY)
    if not isinstance(rows, list) or len(rows) != 12:
        raise ValueError("house interpretation source must contain 12 profiles")
    return rows


def _encode_json_list(source_row: dict[str, Any], field_name: str) -> str:
    """Encode une liste JSON éditoriale avec une validation minimale."""
    values = source_row.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing {field_name} for house profile")
    return json.dumps([str(value) for value in values], ensure_ascii=False)


def sync_house_interpretation_profiles(db: Session, reference_version_id: int) -> None:
    """Insère ou met à jour les profils de maisons pour une version de référence."""
    reference_version = db.get(ReferenceVersionModel, reference_version_id)
    if reference_version is None:
        raise ValueError(f"unknown reference_version_id: {reference_version_id}")

    houses_by_number = {house.number: house.id for house in db.scalars(select(HouseModel)).all()}
    if len(houses_by_number) != 12:
        raise ValueError("house interpretation seed requires 12 astral houses")
    systems_by_name = {
        system.name: system.id for system in db.scalars(select(AstralSystemModel)).all()
    }

    for source_row in load_house_interpretation_profiles_source():
        house_number = int(source_row["house_id"])
        house_id = houses_by_number.get(house_number)
        if house_id is None:
            raise ValueError(f"unknown house number in interpretation source: {house_number}")
        language = str(source_row.get("language") or DEFAULT_LANGUAGE)
        system_name = str(source_row["tradition"])
        astral_system_id = systems_by_name.get(system_name)
        if astral_system_id is None:
            raise ValueError(f"unknown astral system in interpretation source: {system_name}")
        profile = db.scalar(
            select(HouseInterpretationProfileModel).where(
                HouseInterpretationProfileModel.reference_version_id == reference_version_id,
                HouseInterpretationProfileModel.house_id == house_id,
                HouseInterpretationProfileModel.language == language,
                HouseInterpretationProfileModel.astral_system_id == astral_system_id,
            )
        )
        values = {
            "title": str(source_row["title"]),
            "summary": str(source_row["summary"]),
            "micro_note": str(source_row["micro_note"]),
            **{
                field_name: _encode_json_list(source_row, field_name)
                for field_name in JSON_FIELD_NAMES
            },
        }
        if profile is None:
            db.add(
                HouseInterpretationProfileModel(
                    reference_version_id=reference_version_id,
                    house_id=house_id,
                    language=language,
                    astral_system_id=astral_system_id,
                    **values,
                )
            )
            continue
        if reference_version.is_locked:
            continue
        for field_name, value in values.items():
            setattr(profile, field_name, value)
    db.flush()


__all__ = [
    "load_house_interpretation_profiles_source",
    "sync_house_interpretation_profiles",
]
