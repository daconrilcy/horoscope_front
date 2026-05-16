"""Synchronise les traductions astrologiques depuis les JSON documentaires."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AstralAspectInterpretationProfileModel,
    AstralAspectInterpretationProfileTranslationModel,
    AstralAspectTranslationModel,
    AstralHouseInterpretationProfileTranslationModel,
    AstralHouseTranslationModel,
    AstralPlanetInterpretationProfileModel,
    AstralPlanetInterpretationProfileTranslationModel,
    AstralPlanetTranslationModel,
    AstralSignTranslationModel,
    HouseInterpretationProfileModel,
    LanguageModel,
)

TRANSLATION_DIR = Path("docs") / "db_seeder" / "astrology" / "translation"
DEFAULT_SOURCE_LANGUAGE = "en"


def translation_source_path(file_name: str) -> Path:
    """Retourne le chemin robuste d'un seed de traduction astrologique."""
    candidate_relative_path = TRANSLATION_DIR / file_name
    for parent in Path(__file__).resolve().parents:
        source_path = parent / candidate_relative_path
        if source_path.exists():
            return source_path
    raise FileNotFoundError(f"missing astrology translation seed: {file_name}")


def sync_astral_translation_seed_data(
    db: Session,
    reference_version_id: int | None = None,
) -> None:
    """Synchronise toutes les traductions astrologiques connues."""
    language_ids = _language_ids_by_code(db)
    _sync_name_translation_rows(
        db,
        language_ids,
        file_name="astral_sign_translations.json",
        expected_name="astral_sign_translations",
        source_fk_field="astral_sign_id",
        model_class=AstralSignTranslationModel,
        model_fk_field="astral_sign_id",
    )
    _sync_name_translation_rows(
        db,
        language_ids,
        file_name="astral_house_translations.json",
        expected_name="astral_house_translations",
        source_fk_field="astral_house_id",
        model_class=AstralHouseTranslationModel,
        model_fk_field="house_id",
    )
    _sync_name_translation_rows(
        db,
        language_ids,
        file_name="astral_planet_translations.json",
        expected_name="astral_planet_translations",
        source_fk_field="astral_planet_id",
        model_class=AstralPlanetTranslationModel,
        model_fk_field="planet_id",
    )
    _sync_name_translation_rows(
        db,
        language_ids,
        file_name="astral_aspect_translations.json",
        expected_name="astral_aspect_translations",
        source_fk_field="astral_aspect_id",
        model_class=AstralAspectTranslationModel,
        model_fk_field="aspect_id",
    )
    _sync_house_interpretation_translations(db, language_ids, reference_version_id)
    _sync_aspect_interpretation_translations(db, language_ids, reference_version_id)
    _sync_planet_interpretation_translations(db, language_ids, reference_version_id)


def _language_ids_by_code(db: Session) -> dict[str, int]:
    """Construit le mapping code langue vers identifiant SQL."""
    rows = db.scalars(select(LanguageModel)).all()
    language_ids = {row.code: row.id for row in rows}
    missing = {"en", "fr", "es", "de", "it"} - language_ids.keys()
    if missing:
        raise ValueError(f"missing languages for translations: {sorted(missing)}")
    return language_ids


def _load_payload(file_name: str, expected_name: str) -> dict[str, Any]:
    """Charge et valide le nom logique d'un JSON de traduction."""
    with translation_source_path(file_name).open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != expected_name:
        raise ValueError(f"{file_name} targets an unexpected table")
    return raw


def _sync_name_translation_rows(
    db: Session,
    language_ids: dict[str, int],
    *,
    file_name: str,
    expected_name: str,
    source_fk_field: str,
    model_class: type[
        AstralSignTranslationModel
        | AstralHouseTranslationModel
        | AstralPlanetTranslationModel
        | AstralAspectTranslationModel
    ],
    model_fk_field: str,
) -> None:
    """Synchronise les traductions simples de libellés."""
    payload = _load_payload(file_name, expected_name)
    rows = payload.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{file_name} must contain data rows")

    for row in rows:
        source_id = _required_int(row, source_fk_field)
        language_id = _required_language_id(language_ids, row)
        model = db.scalar(
            select(model_class).where(
                getattr(model_class, model_fk_field) == source_id,
                model_class.language_id == language_id,
            )
        )
        if model is None:
            db.add(
                model_class(
                    **{
                        model_fk_field: source_id,
                        "language_id": language_id,
                        "translated_name": str(row["translated_name"]),
                    }
                )
            )
            continue
        model.translated_name = str(row["translated_name"])


def _sync_house_interpretation_translations(
    db: Session,
    language_ids: dict[str, int],
    reference_version_id: int | None,
) -> None:
    """Synchronise les traductions de profils éditoriaux de maisons."""
    payload = _load_payload(
        "astral_house_interpretation_profile_translations.json",
        "astral_house_interpretation_profile_translations",
    )
    rows = _profile_translation_rows(payload)
    for row in rows:
        target_version_id = reference_version_id or _required_int(row, "reference_version_id")
        source_profile = db.scalar(
            select(HouseInterpretationProfileModel).where(
                HouseInterpretationProfileModel.reference_version_id == target_version_id,
                HouseInterpretationProfileModel.house_id == _required_int(row, "house_id"),
                HouseInterpretationProfileModel.language_id
                == language_ids[DEFAULT_SOURCE_LANGUAGE],
            )
        )
        if source_profile is None:
            continue
        _sync_profile_translation_map(
            db,
            language_ids,
            row,
            model_class=AstralHouseInterpretationProfileTranslationModel,
            source_profile_id=source_profile.id,
        )


def _sync_aspect_interpretation_translations(
    db: Session,
    language_ids: dict[str, int],
    reference_version_id: int | None,
) -> None:
    """Synchronise les traductions de profils éditoriaux d'aspects."""
    payload = _load_payload(
        "astral_aspect_interpretation_profile_translations.json",
        "astral_aspect_interpretation_profile_translations",
    )
    rows = _profile_translation_rows(payload)
    aspect_ids_by_code = {row.code: row.id for row in db.scalars(select(AspectModel)).all()}
    for row in rows:
        aspect_id = aspect_ids_by_code.get(str(row["aspect_code"]))
        if aspect_id is None:
            raise ValueError(f"unknown aspect code in translation seed: {row['aspect_code']}")
        target_version_id = reference_version_id or _required_int(row, "reference_version_id")
        source_profile = db.scalar(
            select(AstralAspectInterpretationProfileModel).where(
                AstralAspectInterpretationProfileModel.reference_version_id == target_version_id,
                AstralAspectInterpretationProfileModel.aspect_id == aspect_id,
                AstralAspectInterpretationProfileModel.language_id
                == language_ids[DEFAULT_SOURCE_LANGUAGE],
            )
        )
        if source_profile is None:
            continue
        _sync_profile_translation_map(
            db,
            language_ids,
            row,
            model_class=AstralAspectInterpretationProfileTranslationModel,
            source_profile_id=source_profile.id,
        )


def _sync_planet_interpretation_translations(
    db: Session,
    language_ids: dict[str, int],
    reference_version_id: int | None,
) -> None:
    """Synchronise les traductions de profils éditoriaux de planètes."""
    payload = _load_payload(
        "astral_planet_interpretation_profile_translations.json",
        "astral_planet_interpretation_profile_translations",
    )
    rows = _profile_translation_rows(payload)
    source_language_id = language_ids.get(DEFAULT_SOURCE_LANGUAGE)
    if source_language_id is None:
        source_language = db.scalar(
            select(LanguageModel).where(LanguageModel.code == DEFAULT_SOURCE_LANGUAGE)
        )
        if source_language is None:
            return
        source_language_id = source_language.id

    for row in rows:
        reference_version_ids = (
            [reference_version_id]
            if reference_version_id is not None
            else [int(value) for value in row.get("reference_version_ids", [])]
        )
        for target_version_id in reference_version_ids:
            source_profile = db.scalar(
                select(AstralPlanetInterpretationProfileModel).where(
                    AstralPlanetInterpretationProfileModel.reference_version_id
                    == target_version_id,
                    AstralPlanetInterpretationProfileModel.planet_id
                    == _required_int(row, "planet_id"),
                    AstralPlanetInterpretationProfileModel.astral_system_id
                    == _required_int(row, "astral_system_id"),
                    AstralPlanetInterpretationProfileModel.language_id == source_language_id,
                )
            )
            if source_profile is None:
                continue
            _sync_profile_translation_map(
                db,
                language_ids,
                row,
                model_class=AstralPlanetInterpretationProfileTranslationModel,
                source_profile_id=source_profile.id,
            )


def _profile_translation_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extrait la liste `data.profiles` d'un seed de traduction éditoriale."""
    data = payload.get("data")
    rows = data.get("profiles") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{payload.get('name')} must contain data.profiles rows")
    return rows


def _sync_profile_translation_map(
    db: Session,
    language_ids: dict[str, int],
    source_row: dict[str, Any],
    *,
    model_class: type[
        AstralHouseInterpretationProfileTranslationModel
        | AstralPlanetInterpretationProfileTranslationModel
        | AstralAspectInterpretationProfileTranslationModel
    ],
    source_profile_id: int,
) -> None:
    """Synchronise les traductions d'un profil source pour toutes les locales."""
    translations = source_row.get("translations")
    if not isinstance(translations, dict):
        raise ValueError("profile translation row must contain translations")

    for locale, translated_values in translations.items():
        if not isinstance(translated_values, dict):
            raise ValueError("profile translation values must be objects")
        language_id = language_ids.get(str(locale))
        if language_id is None:
            raise ValueError(f"unknown translation locale: {locale}")
        model = db.scalar(
            select(model_class).where(
                model_class.source_profile_id == source_profile_id,
                model_class.language_id == language_id,
            )
        )
        payload = {
            "title": str(translated_values["title"]),
            "summary": _optional_string(translated_values.get("summary")),
            "micro_note": _optional_string(translated_values.get("micro_note")),
        }
        if model is None:
            db.add(
                model_class(
                    source_profile_id=source_profile_id,
                    language_id=language_id,
                    **payload,
                )
            )
            continue
        for field_name, value in payload.items():
            setattr(model, field_name, value)


def _required_language_id(language_ids: dict[str, int], row: dict[str, Any]) -> int:
    """Résout la langue d'une ligne de seed."""
    locale = str(row["locale"])
    language_id = language_ids.get(locale)
    if language_id is None:
        raise ValueError(f"unknown translation locale: {locale}")
    return language_id


def _required_int(row: dict[str, Any], field_name: str) -> int:
    """Lit un entier obligatoire dans une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, int):
        raise ValueError(f"missing integer field: {field_name}")
    return value


def _optional_string(value: object) -> str | None:
    """Convertit une valeur optionnelle en chaîne ou `None`."""
    return None if value is None else str(value)


__all__ = ["sync_astral_translation_seed_data", "translation_source_path"]
