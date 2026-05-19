"""Synchronise les JSON de dignités astrologiques vers les tables SQL."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AstralAccidentalDignityCategoryModel,
    AstralAccidentalDignityConditionSchemaModel,
    AstralAccidentalDignityExpressionTendencyModel,
    AstralAccidentalDignityRuleModel,
    AstralAccidentalDignityScoreWeightModel,
    AstralAccidentalDignityTypeModel,
    AstralConditionOperatorModel,
    AstralDecanSystemCodeModel,
    AstralDiginityScoreProfileModel,
    AstralDignityFunctionalEffectModel,
    AstralDignityIntensityEffectModel,
    AstralElementModel,
    AstralEssentialDignityCategoryModel,
    AstralEssentialDignityExpressionTendencyModel,
    AstralEssentialDignityRuleModel,
    AstralEssentialDignityScoreWeightModel,
    AstralEssentialDignityTypeModel,
    AstralFaceDecanModel,
    AstralHeliacalConditionModel,
    AstralHorizonPositionModel,
    AstralHouseModalityModel,
    AstralPlanetMotionStateModel,
    AstralPlanetNatureModel,
    AstralRulerAssignmentsRoleModel,
    AstralSectModel,
    AstralSignGenderModel,
    AstralSignModel,
    AstralSourceModel,
    AstralSpeedRelationModel,
    AstralSystemModel,
    AstralTermBoundModel,
    AstralTermSystemCodeModel,
    AstralTriplicityRulerAssignmentModel,
    HouseModel,
    PlanetModel,
)

JsonRow = dict[str, Any]


def _astrology_path(file_name: str) -> Path:
    """Construit le chemin vers un fichier JSON de seed astrologique."""
    return Path(__file__).resolve().parents[4] / "docs" / "db_seeder" / "astrology" / file_name


def _load_rows(file_name: str) -> list[JsonRow]:
    """Charge les lignes d'un JSON documentaire de seed."""
    with _astrology_path(file_name).open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f"{file_name} must contain a data list")
    return [dict(row) for row in rows]


def _upsert_by_id(db: Session, model: type[Any], row: JsonRow) -> None:
    """Insère ou met à jour une ligne stable identifiée par son id documentaire."""
    row_id = int(row["id"])
    existing = db.get(model, row_id)
    payload = {key: value for key, value in row.items() if key != "id"}
    if existing is None:
        db.add(model(id=row_id, **payload))
        return
    for field_name, value in payload.items():
        setattr(existing, field_name, value)


def _load_source_id_map(
    db: Session,
    model: type[Any],
    source_file: str,
    source_field: str,
    model_field: str,
) -> dict[int, int]:
    """Associe les ids documentaires JSON aux ids réels en base."""
    db_rows = db.scalars(select(model)).all()
    db_id_by_key = {str(getattr(row, model_field)): int(row.id) for row in db_rows}
    mapping: dict[int, int] = {}
    for source_row in _load_rows(source_file):
        key = str(source_row[source_field])
        if key not in db_id_by_key:
            raise ValueError(f"missing DB reference for {source_file}: {key}")
        mapping[int(source_row["id"])] = db_id_by_key[key]
    return mapping


def _house_id_map(db: Session) -> dict[int, int]:
    """Associe les numéros de maisons documentaires aux ids réels."""
    return {int(row.number): int(row.id) for row in db.scalars(select(HouseModel)).all()}


def _remap_condition_json(condition_json: JsonRow, maps: dict[str, dict[int, int]]) -> JsonRow:
    """Remappe les ids internes d'un objet condition JSON vers les ids réels DB."""
    remapped = copy.deepcopy(condition_json)
    for field_name, id_map in maps.items():
        if field_name in remapped and remapped[field_name] is not None:
            remapped[field_name] = id_map[int(remapped[field_name])]
        plural_name = f"{field_name[:-3]}_ids" if field_name.endswith("_id") else ""
        if plural_name and plural_name in remapped:
            remapped[plural_name] = [id_map[int(value)] for value in remapped[plural_name]]
    return remapped


def _sync_lookup_tables(db: Session) -> None:
    """Synchronise les tables de vocabulaire stables des dignités."""
    lookup_sources: tuple[tuple[type[Any], str], ...] = (
        (AstralSourceModel, "astral_sources.json"),
        (AstralDignityFunctionalEffectModel, "astral_dignity_functional_effects.json"),
        (AstralDignityIntensityEffectModel, "astral_dignity_intensity_effects.json"),
        (AstralEssentialDignityCategoryModel, "astral_essential_dignity_categories.json"),
        (
            AstralEssentialDignityExpressionTendencyModel,
            "astral_essential_dignity_expression_tendencies.json",
        ),
        (AstralAccidentalDignityCategoryModel, "astral_accidental_dignity_categories.json"),
        (
            AstralAccidentalDignityExpressionTendencyModel,
            "astral_accidental_dignity_expression_tendencies.json",
        ),
        (
            AstralAccidentalDignityConditionSchemaModel,
            "astral_accidental_dignity_condition_schemas.json",
        ),
        (AstralTermSystemCodeModel, "astral_term_system_code.json"),
        (AstralDecanSystemCodeModel, "astral_decan_system_code.json"),
        (AstralSectModel, "astral_sect.json"),
        (AstralRulerAssignmentsRoleModel, "astral_ruler_assignments_role.json"),
        (AstralPlanetMotionStateModel, "astral_planet_motion_states.json"),
        (AstralSpeedRelationModel, "astral_speed_relations.json"),
        (AstralHeliacalConditionModel, "astral_heliacal_conditions.json"),
        (AstralHorizonPositionModel, "astral_horizon_positions.json"),
        (AstralSignGenderModel, "astral_sign_genders.json"),
        (AstralPlanetNatureModel, "astral_planet_natures.json"),
        (AstralConditionOperatorModel, "astral_condition_operators.json"),
        (AstralEssentialDignityTypeModel, "astral_essential_dignity_types.json"),
        (AstralAccidentalDignityTypeModel, "astral_accidental_dignity_types.json"),
    )
    for model, source_file in lookup_sources:
        expected_ids = set()
        for row in _load_rows(source_file):
            expected_ids.add(int(row["id"]))
            if "description" not in row:
                row["description"] = ""
            _upsert_by_id(db, model, row)
        db.execute(delete(model).where(model.id.not_in(expected_ids)))
    db.flush()


def _reference_maps(db: Session) -> dict[str, dict[int, int]]:
    """Prépare les correspondances d'ids documentaires vers la base courante."""
    return {
        "planet_id": _load_source_id_map(db, PlanetModel, "astral_planets.json", "code", "code"),
        "relative_planet_id": _load_source_id_map(
            db, PlanetModel, "astral_planets.json", "code", "code"
        ),
        "sign_id": _load_source_id_map(db, AstralSignModel, "astral_signs.json", "code", "code"),
        "element_id": _load_source_id_map(
            db, AstralElementModel, "astral_elements.json", "code", "code"
        ),
        "astral_system_id": _load_source_id_map(
            db, AstralSystemModel, "astral_systems.json", "name", "name"
        ),
        "house_id": _house_id_map(db),
        "aspect_id": _load_source_id_map(db, AspectModel, "astral_aspects.json", "code", "code"),
        "house_modality_id": _load_source_id_map(
            db,
            AstralHouseModalityModel,
            "astral_house_modalities.json",
            "name",
            "name",
        ),
    }


def _sync_score_profiles(db: Session, maps: dict[str, dict[int, int]]) -> None:
    """Synchronise les profils de scoring des dignités."""
    expected_ids: set[int] = set()
    for row in _load_rows("astral_diginity_score_profiles.json"):
        row["astral_system_id"] = maps["astral_system_id"][int(row["astral_system_id"])]
        expected_ids.add(int(row["id"]))
        _upsert_by_id(db, AstralDiginityScoreProfileModel, row)
    db.flush()
    db.execute(
        delete(AstralDiginityScoreProfileModel).where(
            AstralDiginityScoreProfileModel.id.not_in(expected_ids)
        )
    )


def _replace_versioned_rows(
    db: Session,
    model: type[Any],
    reference_version_id: int,
    rows: list[JsonRow],
) -> None:
    """Remplace les lignes versionnées pour éviter les doublons entre seeds."""
    db.execute(delete(model).where(model.reference_version_id == reference_version_id))
    for row in rows:
        row["reference_version_id"] = reference_version_id
        db.add(model(**row))
    db.flush()


def _sync_boundaries_and_rules(
    db: Session,
    reference_version_id: int,
    maps: dict[str, dict[int, int]],
) -> None:
    """Synchronise les bornes, faces, règles essentielles et triplicités."""
    term_rows = []
    for row in _load_rows("astral_term_bounds.json"):
        row["sign_id"] = maps["sign_id"][int(row["sign_id"])]
        row["planet_id"] = maps["planet_id"][int(row["planet_id"])]
        term_rows.append(row)
    _replace_versioned_rows(db, AstralTermBoundModel, reference_version_id, term_rows)

    decan_rows = []
    for row in _load_rows("astral_face_decans.json"):
        row["sign_id"] = maps["sign_id"][int(row["sign_id"])]
        row["planet_id"] = maps["planet_id"][int(row["planet_id"])]
        decan_rows.append(row)
    _replace_versioned_rows(db, AstralFaceDecanModel, reference_version_id, decan_rows)

    essential_rows = []
    for row in _load_rows("astral_essential_dignity_rules.json"):
        row["planet_id"] = maps["planet_id"][int(row["planet_id"])]
        row["sign_id"] = maps["sign_id"][int(row["sign_id"])]
        row["astral_system_id"] = maps["astral_system_id"][int(row["astral_system_id"])]
        essential_rows.append(row)
    _replace_versioned_rows(
        db, AstralEssentialDignityRuleModel, reference_version_id, essential_rows
    )

    triplicity_rows = []
    for row in _load_rows("astral_triplicity_ruler_assignments.json"):
        row["element_id"] = maps["element_id"][int(row["element_id"])]
        row["planet_id"] = maps["planet_id"][int(row["planet_id"])]
        row["astral_system_id"] = maps["astral_system_id"][int(row["astral_system_id"])]
        triplicity_rows.append(row)
    _replace_versioned_rows(
        db,
        AstralTriplicityRulerAssignmentModel,
        reference_version_id,
        triplicity_rows,
    )


def _sync_score_weights(db: Session) -> None:
    """Synchronise les poids de scoring non versionnés."""
    db.execute(delete(AstralEssentialDignityScoreWeightModel))
    for row in _load_rows("astral_essential_dignity_score_weights.json"):
        db.add(AstralEssentialDignityScoreWeightModel(**row))
    db.execute(delete(AstralAccidentalDignityScoreWeightModel))
    for row in _load_rows("astral_accidental_dignity_score_weights.json"):
        db.add(AstralAccidentalDignityScoreWeightModel(**row))
    db.flush()


def _sync_accidental_rules(
    db: Session,
    reference_version_id: int,
    maps: dict[str, dict[int, int]],
) -> None:
    """Synchronise les règles accidentelles et remappe leurs conditions JSON."""
    rows = []
    condition_maps = {
        key: maps[key]
        for key in (
            "planet_id",
            "relative_planet_id",
            "house_id",
            "aspect_id",
            "house_modality_id",
        )
    }
    for row in _load_rows("astral_accidental_dignity_rules.json"):
        if row.get("planet_id") is not None:
            row["planet_id"] = maps["planet_id"][int(row["planet_id"])]
        row["astral_system_id"] = maps["astral_system_id"][int(row["astral_system_id"])]
        row["condition_json"] = _remap_condition_json(row["condition_json"], condition_maps)
        rows.append(row)
    _replace_versioned_rows(db, AstralAccidentalDignityRuleModel, reference_version_id, rows)


def sync_astral_dignity_seed_data(db: Session, reference_version_id: int) -> None:
    """Synchronise tout le référentiel de dignités pour la version active."""
    _sync_lookup_tables(db)
    maps = _reference_maps(db)
    _sync_score_profiles(db, maps)
    _sync_boundaries_and_rules(db, reference_version_id, maps)
    _sync_score_weights(db)
    _sync_accidental_rules(db, reference_version_id, maps)
    db.flush()
