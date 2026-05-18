"""Synchronise le vocabulaire éditorial des interprétations de planètes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AstralPlanetInterpretationProfileModel,
    AstralSystemModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)

DEFAULT_LANGUAGE = "en"
EXPECTED_SOURCE_ROW_COUNT = 20
EXPECTED_PROFILE_COUNT = 10
JSON_FIELD_NAMES = (
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_expression_json",
    "relational_expression_json",
    "vocational_expression_json",
    "spiritual_expression_json",
    "energetic_dynamics_json",
    "growth_patterns_json",
    "conflict_patterns_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
)


def _planet_interpretation_source_path() -> Path:
    """Retourne le chemin du JSON documentaire des profils de planètes."""
    candidate_relative_paths = (
        Path("docs") / "db_seeder" / "astrology" / "astral_planet_interpretation_profiles.json",
        Path("docs") / "recherches astro" / "astral_planet_interpretation_profiles.json",
    )
    for parent in Path(__file__).resolve().parents:
        for relative_path in candidate_relative_paths:
            source_path = parent / relative_path
            if source_path.exists():
                return source_path
    raise FileNotFoundError("missing astrology seed astral_planet_interpretation_profiles.json")


def load_planet_interpretation_profiles_source() -> list[dict[str, Any]]:
    """Charge et valide la source JSON des profils éditoriaux de planètes."""
    source_path = _planet_interpretation_source_path()
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict):
        raise ValueError("planet interpretation source must be an object")
    if raw.get("name") != "astral_planet_interpretation_profiles":
        raise ValueError("planet interpretation source targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or len(rows) != EXPECTED_SOURCE_ROW_COUNT:
        raise ValueError(
            f"planet interpretation source must contain {EXPECTED_SOURCE_ROW_COUNT} source rows"
        )
    return rows


def _deduplicate_profile_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Déduplique les lignes source strictement identiques à clé DB équivalente."""
    unique_rows: dict[tuple[int, int, int], dict[str, Any]] = {}
    for row in rows:
        key = (int(row["planet_id"]), int(row["astral_system_id"]), int(row["language_id"]))
        existing = unique_rows.get(key)
        if existing is None:
            unique_rows[key] = row
            continue
        if json.dumps(existing, sort_keys=True) != json.dumps(row, sort_keys=True):
            raise ValueError(f"conflicting planet interpretation source row for key={key!r}")
    if len(unique_rows) != EXPECTED_PROFILE_COUNT:
        raise ValueError(
            f"planet interpretation source must contain {EXPECTED_PROFILE_COUNT} unique profiles"
        )
    return list(unique_rows.values())


def _encode_json_list(source_row: dict[str, Any], field_name: str) -> str:
    """Encode une liste JSON éditoriale avec une validation minimale."""
    values = source_row.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing {field_name} for planet profile")
    return json.dumps([str(value) for value in values], ensure_ascii=False)


def sync_planet_interpretation_profiles(db: Session, reference_version_id: int) -> None:
    """Insère ou met à jour les profils de planètes pour une version de référence."""
    reference_version = db.get(ReferenceVersionModel, reference_version_id)
    if reference_version is None:
        raise ValueError(f"unknown reference_version_id: {reference_version_id}")

    planets_by_id = {planet.id: planet.id for planet in db.scalars(select(PlanetModel)).all()}
    systems_by_id = {system.id: system.id for system in db.scalars(select(AstralSystemModel)).all()}
    language_ids_by_code = {
        language.code: language.id for language in db.scalars(select(LanguageModel)).all()
    }
    language_ids_by_id = set(language_ids_by_code.values())
    if not planets_by_id:
        raise ValueError("planet interpretation seed requires the canonical astral planets")

    matching_rows = [
        row
        for row in load_planet_interpretation_profiles_source()
        if int(row.get("reference_version_id", reference_version_id)) == reference_version_id
    ]
    if not matching_rows:
        db.flush()
        return
    for source_row in _deduplicate_profile_rows(matching_rows):
        planet_id = int(source_row["planet_id"])
        if planet_id not in planets_by_id:
            raise ValueError(f"unknown planet id in interpretation source: {planet_id}")
        astral_system_id = int(source_row["astral_system_id"])
        if astral_system_id not in systems_by_id:
            raise ValueError(
                f"unknown astral system id in interpretation source: {astral_system_id}"
            )
        language_id = _resolve_language_id(source_row, language_ids_by_code, language_ids_by_id)

        profile = db.scalar(
            select(AstralPlanetInterpretationProfileModel).where(
                AstralPlanetInterpretationProfileModel.reference_version_id == reference_version_id,
                AstralPlanetInterpretationProfileModel.planet_id == planet_id,
                AstralPlanetInterpretationProfileModel.astral_system_id == astral_system_id,
                AstralPlanetInterpretationProfileModel.language_id == language_id,
            )
        )
        values = {
            "title": str(source_row["title"]),
            "summary": str(source_row["summary"]),
            "micro_note": None
            if source_row.get("micro_note") is None
            else str(source_row["micro_note"]),
            **{
                field_name: _encode_json_list(source_row, field_name)
                for field_name in JSON_FIELD_NAMES
            },
        }
        if profile is None:
            db.add(
                AstralPlanetInterpretationProfileModel(
                    reference_version_id=reference_version_id,
                    planet_id=planet_id,
                    astral_system_id=astral_system_id,
                    language_id=language_id,
                    **values,
                )
            )
            continue
        if reference_version.is_locked:
            continue
        for field_name, value in values.items():
            setattr(profile, field_name, value)
    db.flush()


def _resolve_language_id(
    source_row: dict[str, Any],
    language_ids_by_code: dict[str, int],
    language_ids_by_id: set[int],
) -> int:
    """Résout la langue source depuis `language_id` ou l'ancien code `language`."""
    raw_language_id = source_row.get("language_id")
    if isinstance(raw_language_id, int) and raw_language_id in language_ids_by_id:
        return raw_language_id
    language_code = str(source_row.get("language") or DEFAULT_LANGUAGE)
    language_id = language_ids_by_code.get(language_code)
    if language_id is None:
        raise ValueError(f"unknown language in planet interpretation source: {language_code}")
    return language_id


__all__ = [
    "load_planet_interpretation_profiles_source",
    "sync_planet_interpretation_profiles",
]
