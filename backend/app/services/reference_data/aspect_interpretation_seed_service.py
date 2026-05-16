"""Synchronise le vocabulaire éditorial des interprétations d'aspects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AstralAspectInterpretationProfileModel,
    AstralSystemModel,
    LanguageModel,
    ReferenceVersionModel,
)

DEFAULT_LANGUAGE = "en"
EXPECTED_PROFILE_COUNT = 20
SOURCE_UNIQUE_FIELDS = (
    "reference_version_id",
    "aspect_code",
    "astral_system_code",
    "language_id",
)
JSON_FIELD_NAMES = (
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_keywords_json",
    "relationship_keywords_json",
    "career_keywords_json",
    "spiritual_keywords_json",
    "energetic_dynamics_json",
    "growth_patterns_json",
    "conflict_patterns_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
)


def _aspect_interpretation_source_path() -> Path:
    """Retourne le chemin du JSON documentaire des profils d'aspects."""
    candidate_relative_paths = (
        Path("docs") / "db_seeder" / "astrology" / "astral_aspect_interpretation_profiles.json",
        Path("docs") / "recherches astro" / "astral_aspect_interpretation_profiles.json",
    )
    for parent in Path(__file__).resolve().parents:
        for relative_path in candidate_relative_paths:
            source_path = parent / relative_path
            if source_path.exists():
                return source_path
    raise FileNotFoundError("missing astrology seed astral_aspect_interpretation_profiles.json")


def load_aspect_interpretation_profiles_source() -> list[dict[str, Any]]:
    """Charge et valide la source JSON des profils éditoriaux d'aspects."""
    source_path = _aspect_interpretation_source_path()
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict):
        raise ValueError("aspect interpretation source must be an object")
    table_name = raw.get("name")
    if table_name != "astral_aspect_interpretation_profiles":
        raise ValueError("aspect interpretation source targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or len(rows) != EXPECTED_PROFILE_COUNT:
        raise ValueError("aspect interpretation source must contain 20 profiles")
    _validate_unique_profile_keys(rows)
    return rows


def _source_profile_key(source_row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Construit la clé métier du profil source pour valider le JSON."""
    values = [str(source_row.get(field_name) or "") for field_name in SOURCE_UNIQUE_FIELDS]
    if not values[-1] and source_row.get("language"):
        values[-1] = str(source_row["language"])
    return tuple(values)


def _validate_unique_profile_keys(rows: list[dict[str, Any]]) -> None:
    """Refuse les doublons de clé métier avant l'écriture SQL."""
    seen_keys: set[tuple[str, str, str, str]] = set()
    duplicate_keys: set[tuple[str, str, str, str]] = set()
    for row in rows:
        key = _source_profile_key(row)
        if any(not value for value in key):
            raise ValueError("aspect interpretation source contains an incomplete unique key")
        if key in seen_keys:
            duplicate_keys.add(key)
            continue
        seen_keys.add(key)
    if duplicate_keys:
        formatted_keys = ", ".join("/".join(key) for key in sorted(duplicate_keys))
        raise ValueError(f"duplicate aspect interpretation profile key: {formatted_keys}")


def _encode_json_list(source_row: dict[str, Any], field_name: str) -> str:
    """Encode une liste JSON éditoriale avec une validation minimale."""
    values = source_row.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing {field_name} for aspect profile")
    return json.dumps([str(value) for value in values], ensure_ascii=False)


def sync_aspect_interpretation_profiles(db: Session, reference_version_id: int) -> None:
    """Insère ou met à jour les profils d'aspects pour une version de référence."""
    reference_version = db.get(ReferenceVersionModel, reference_version_id)
    if reference_version is None:
        raise ValueError(f"unknown reference_version_id: {reference_version_id}")

    aspects_by_code = {aspect.code: aspect.id for aspect in db.scalars(select(AspectModel)).all()}
    systems_by_name = {
        system.name: system.id for system in db.scalars(select(AstralSystemModel)).all()
    }
    language_ids_by_code = {
        language.code: language.id for language in db.scalars(select(LanguageModel)).all()
    }
    if len(aspects_by_code) < EXPECTED_PROFILE_COUNT:
        raise ValueError("aspect interpretation seed requires the canonical astral aspects")

    for source_row in load_aspect_interpretation_profiles_source():
        aspect_code = str(source_row["aspect_code"])
        aspect_id = aspects_by_code.get(aspect_code)
        if aspect_id is None:
            raise ValueError(f"unknown aspect code in interpretation source: {aspect_code}")
        system_name = str(source_row["astral_system_code"])
        astral_system_id = systems_by_name.get(system_name)
        if astral_system_id is None:
            raise ValueError(f"unknown astral system in interpretation source: {system_name}")
        language_id = _resolve_language_id(source_row, language_ids_by_code)

        profile = db.scalar(
            select(AstralAspectInterpretationProfileModel).where(
                AstralAspectInterpretationProfileModel.reference_version_id == reference_version_id,
                AstralAspectInterpretationProfileModel.aspect_id == aspect_id,
                AstralAspectInterpretationProfileModel.astral_system_id == astral_system_id,
                AstralAspectInterpretationProfileModel.language_id == language_id,
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
                AstralAspectInterpretationProfileModel(
                    reference_version_id=reference_version_id,
                    aspect_id=aspect_id,
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


def _resolve_language_id(source_row: dict[str, Any], language_ids_by_code: dict[str, int]) -> int:
    """Résout la langue source depuis `language_id` ou l'ancien code `language`."""
    raw_language_id = source_row.get("language_id")
    if isinstance(raw_language_id, int) and raw_language_id > 0:
        return raw_language_id
    language_code = str(source_row.get("language") or DEFAULT_LANGUAGE)
    language_id = language_ids_by_code.get(language_code)
    if language_id is None:
        raise ValueError(f"unknown language in aspect interpretation source: {language_code}")
    return language_id


__all__ = [
    "load_aspect_interpretation_profiles_source",
    "sync_aspect_interpretation_profiles",
]
