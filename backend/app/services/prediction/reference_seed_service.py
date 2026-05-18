"""Porte le seed canonique des references et rulesets de prediction."""

import json
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AspectProfileModel,
    AstralAspectDefinitionModel,
    AstralAspectFamilyModel,
    AstralAspectInterpretationProfileModel,
    AstralAspectInterpretationProfileTranslationModel,
    AstralAspectOrbRuleModel,
    AstralDefaultValenceModel,
    AstralDignityTypeModel,
    AstralElementModel,
    AstralHouseInterpretationProfileTranslationModel,
    AstralInterpretiveValenceModel,
    AstralModalityModel,
    AstralPlanetInterpretationProfileModel,
    AstralPlanetInterpretationProfileTranslationModel,
    AstralPlanetSignDignityModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseInterpretationProfileModel,
    HouseModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    PredictionRulesetModel,
    ReferenceVersionModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.repositories import ReferenceRepository
from app.infra.db.repositories.house_system_reference import sync_house_system_seed_data
from app.services.reference_data.aspect_interpretation_seed_service import (
    sync_aspect_interpretation_profiles,
)
from app.services.reference_data.house_interpretation_seed_service import (
    sync_house_interpretation_profiles,
)
from app.services.reference_data.planet_interpretation_seed_service import (
    sync_planet_interpretation_profiles,
)
from app.services.reference_data.translation_seed_service import sync_astral_translation_seed_data


class PredictionReferenceSeedAbortError(RuntimeError):
    """Erreur levee quand le seed de prediction doit s interrompre explicitement."""


EXPECTED_COUNTS = {
    "prediction_categories": 12,
    "planet_profiles": 10,
    "house_profiles": 12,
    "astral_house_interpretation_profiles": 12,
    "astral_planet_interpretation_profiles": 10,
    "astral_aspect_interpretation_profiles": 20,
    "astral_aspect_profiles": 20,
    "astral_aspect_definitions": 80,
    "astral_aspect_orb_rules": 79,
    "astral_default_valence": 4,
    "astral_interpretive_valence": 5,
    "astro_points": 4,
    "astral_dignity_type": 4,
    "astral_elements": 4,
    "astral_modalities": 3,
    "astral_polarities": 2,
    "astral_planet_sign_dignities": 50,
    "astral_sign_profiles": 12,
    "astral_planet_category_weights": 85,
    "house_category_weights": 24,
    "point_category_weights": 8,
    "ruleset_event_types": 16,  # 8 per ruleset (1.0.0 and 2.0.0)
    "ruleset_parameters": 16,  # 8 per ruleset (1.0.0 and 2.0.0)
}

SIGN_PROFILE_DATA = [
    ("aries", "fire", "cardinal", "yang"),
    ("taurus", "earth", "fixed", "yin"),
    ("gemini", "air", "mutable", "yang"),
    ("cancer", "water", "cardinal", "yin"),
    ("leo", "fire", "fixed", "yang"),
    ("virgo", "earth", "mutable", "yin"),
    ("libra", "air", "cardinal", "yang"),
    ("scorpio", "water", "fixed", "yin"),
    ("sagittarius", "fire", "mutable", "yang"),
    ("capricorn", "earth", "cardinal", "yin"),
    ("aquarius", "air", "fixed", "yang"),
    ("pisces", "water", "mutable", "yin"),
]
SIGN_CODE_BY_SOURCE_ID = {
    index: sign_code
    for index, (sign_code, _element, _modality, _polarity) in enumerate(SIGN_PROFILE_DATA, 1)
}
PLANET_CODE_BY_SOURCE_ID = {
    1: "sun",
    2: "moon",
    3: "mercury",
    4: "venus",
    5: "mars",
    6: "jupiter",
    7: "saturn",
    8: "uranus",
    9: "neptune",
    10: "pluto",
}


def _astro_research_path(file_name: str) -> Path:
    """Construit le chemin vers les sources JSON astrologiques documentaires."""
    repo_root = Path(__file__).resolve().parents[4]
    candidates = (
        repo_root / "docs" / "db_seeder" / "astrology" / file_name,
        Path(__file__).resolve().parents[3] / "docs" / "db_seeder" / "astrology" / file_name,
        repo_root / "docs" / "recherches astro" / file_name,
        Path(__file__).resolve().parents[3] / "docs" / "recherches astro" / file_name,
    )
    for source_path in candidates:
        if source_path.exists():
            return source_path
    raise FileNotFoundError(f"missing astrology seed source: {file_name}")


def _load_sign_keywords() -> dict[str, dict[str, list[str]]]:
    """Charge les mots-clés des signes depuis la source documentaire canonique."""
    keywords_path = _astro_research_path("astral_sign_keywords.json")
    with keywords_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("signs keywords source must contain a non-empty data list")
    return {
        str(row["code"]): {
            "keywords": [str(value) for value in row["keywords_json"]],
            "shadow_keywords": [str(value) for value in row["shadow_keywords_json"]],
        }
        for row in rows
    }


def _load_planet_sign_dignities() -> list[dict[str, object]]:
    """Charge les dignités planétaires depuis la source documentaire canonique."""
    source_path = _astro_research_path("astral_planet_sign_dignities.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("planet sign dignities source must be a non-empty list")
    return rows


def _load_aspect_families() -> list[str]:
    """Charge les familles d'aspects depuis la source documentaire canonique."""
    with _astro_research_path("astral_aspect_families.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("aspect families source must contain a non-empty family list")
    return [str(row["name"]) for row in rows]


def _load_aspects() -> list[dict[str, object]]:
    """Charge les aspects astrologiques depuis la source documentaire canonique."""
    with _astro_research_path("astral_aspects.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("aspects source must be a non-empty list")
    return rows


def _load_aspect_profiles() -> list[dict[str, object]]:
    """Charge les profils prédictifs d'aspects depuis la source documentaire."""
    with _astro_research_path("astral_aspect_profiles.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    profiles = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("aspect profiles source must contain a non-empty seed list")
    return profiles


def _load_daily_planet_profiles() -> list[dict[str, object]]:
    """Charge les paramètres daily des planètes depuis la source documentaire."""
    with _astro_research_path("astral_prediction_daily_planet_profiles.json").open(
        encoding="utf-8"
    ) as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_prediction_daily_planet_profiles":
        raise ValueError("daily planet profiles source targets an unexpected table")
    profiles = raw.get("data")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("daily planet profiles source must contain a non-empty data list")
    if not all(isinstance(profile, dict) for profile in profiles):
        raise ValueError("daily planet profiles rows must be objects")
    return profiles


def _load_aspect_definition_groups() -> list[dict[str, object]]:
    """Charge les définitions d'aspects par système depuis la source documentaire."""
    with _astro_research_path("astral_aspect_definitions.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    groups = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(groups, list) or not groups:
        raise ValueError("aspect definitions source must contain a non-empty seed list")
    return groups


def _load_aspect_orb_rule_groups() -> list[dict[str, object]]:
    """Charge les règles de surcharge d'orbes depuis la source documentaire."""
    with _astro_research_path("astral_aspect_orb_rules.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    groups = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(groups, list) or not groups:
        raise ValueError("aspect orb rules source must contain a non-empty seed list")
    return groups


def _resolve_aspect_orb_rule_groups() -> list[dict[str, object]]:
    """Retourne les règles physiques locales sans déplier l'héritage."""
    raw_groups = _load_aspect_orb_rule_groups()
    rules_by_system: dict[str, list[dict[str, object]]] = {}
    inheritance_by_system: dict[str, str | None] = {}
    final_groups: list[dict[str, object]] = []

    for group in raw_groups:
        system_code = str(group["astral_system_code"])
        if "copy_rules_from" in group:
            raise ValueError("copy_rules_from is forbidden for aspect orb rule groups")
        parent_code = group.get("inherits_from")
        inheritance_by_system[system_code] = None if parent_code is None else str(parent_code)
        rules = [dict(rule) for rule in group.get("rules", [])]
        if "override_rules" in group:
            rules.extend(dict(rule) for rule in group.get("override_rules", []))
        rules_by_system[system_code] = rules
        final_groups.append(
            {
                "reference_version_id": group["reference_version_id"],
                "astral_system_code": system_code,
                "rules": rules,
            }
        )

    unknown_parent_codes = {
        parent_code
        for parent_code in inheritance_by_system.values()
        if parent_code is not None and parent_code not in rules_by_system
    }
    if unknown_parent_codes:
        raise ValueError(
            "unknown inherited aspect orb rule system: " + ", ".join(sorted(unknown_parent_codes))
        )
    _ensure_no_complete_inherited_orb_rule_copy(rules_by_system, inheritance_by_system)
    return final_groups


def _orb_rule_signature(rule: dict[str, object]) -> tuple[object, ...]:
    """Construit une signature stable pour detecter une copie physique."""
    return (
        str(rule.get("aspect_code")),
        str(rule.get("calculation_context")),
        str(rule.get("source_body_type")),
        rule.get("source_planet_code"),
        rule.get("source_point_code"),
        str(rule.get("target_body_type")),
        rule.get("target_planet_code"),
        rule.get("target_point_code"),
        float(rule.get("orb_deg", 0)),
        int(rule.get("priority", 0)),
        bool(rule.get("is_enabled", True)),
    )


def _ensure_no_complete_inherited_orb_rule_copy(
    rules_by_system: dict[str, list[dict[str, object]]],
    inheritance_by_system: dict[str, str | None],
) -> None:
    """Refuse qu'un systeme enfant stocke une copie complete de son parent."""
    for system_code, parent_code in inheritance_by_system.items():
        if parent_code is None:
            continue
        parent_rules = rules_by_system.get(parent_code)
        if not parent_rules:
            continue
        child_signatures = {_orb_rule_signature(rule) for rule in rules_by_system[system_code]}
        parent_signatures = {_orb_rule_signature(rule) for rule in parent_rules}
        if parent_signatures and parent_signatures <= child_signatures:
            raise ValueError(
                f"aspect orb rules for {system_code} duplicate inherited parent {parent_code}"
            )


def _required_keyword_list(
    keywords_by_sign: dict[str, dict[str, list[str]]],
    sign_code: str,
    field_name: str,
) -> list[str]:
    """Valide la présence des listes de mots-clés attendues pour un signe."""
    sign_keywords = keywords_by_sign.get(sign_code)
    if sign_keywords is None:
        raise ValueError(f"missing keywords for sign {sign_code}")
    values = sign_keywords.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing {field_name} for sign {sign_code}")
    return [str(value) for value in values]


def _ensure_taxonomy(
    db: Session,
    model: type[
        AstralDignityTypeModel | AstralElementModel | AstralModalityModel | AstralPolarityModel
    ],
    rows: list[tuple[str, str]],
) -> dict[str, int]:
    """Insère les valeurs manquantes d'une taxonomie astrale stable."""
    for code, name in rows:
        if db.scalar(select(model.id).where(model.code == code)) is None:
            db.add(model(code=code, name=name))
    db.flush()
    return {row.code: row.id for row in db.scalars(select(model)).all()}


def _ensure_astral_dignity_types(db: Session) -> None:
    """Garantit le référentiel stable des types de dignités astrologiques."""
    _ensure_taxonomy(
        db,
        AstralDignityTypeModel,
        [
            ("domicile", "Domicile"),
            ("detriment", "Detriment"),
            ("exaltation", "Exaltation"),
            ("fall", "Fall"),
        ],
    )


def _ensure_astral_systems(db: Session) -> dict[str, int]:
    """Garantit le référentiel stable des systèmes astrologiques."""
    inheritance = {
        "traditional": None,
        "modern": None,
        "hellenistic": "traditional",
        "medieval": "traditional",
    }
    for name in inheritance:
        if db.scalar(select(AstralSystemModel.id).where(AstralSystemModel.name == name)) is None:
            db.add(AstralSystemModel(name=name))
    db.flush()
    systems = {row.name: row for row in db.scalars(select(AstralSystemModel)).all()}
    for name, parent_name in inheritance.items():
        system = systems[name]
        system.inherits_from_system_id = None if parent_name is None else systems[parent_name].id
    db.flush()
    return {row.name: row.id for row in db.scalars(select(AstralSystemModel)).all()}


def _ensure_astral_aspect_families(db: Session) -> dict[str, int]:
    """Garantit les familles stables d'aspects depuis le JSON canonique."""
    for name in _load_aspect_families():
        if (
            db.scalar(
                select(AstralAspectFamilyModel.id).where(AstralAspectFamilyModel.name == name)
            )
            is None
        ):
            db.add(AstralAspectFamilyModel(name=name))
    db.flush()
    return {row.name: row.id for row in db.scalars(select(AstralAspectFamilyModel)).all()}


def _ensure_astral_valences(db: Session) -> None:
    """Garantit les référentiels stables de valences d'aspects."""
    for name in ("positive", "negative", "neutral", "contextual"):
        if (
            db.scalar(
                select(AstralDefaultValenceModel.id).where(AstralDefaultValenceModel.name == name)
            )
            is None
        ):
            db.add(AstralDefaultValenceModel(name=name))
    for name in (
        "supportive",
        "harmonious",
        "dynamic_challenging",
        "polarizing",
        "amplifying",
    ):
        if (
            db.scalar(
                select(AstralInterpretiveValenceModel.id).where(
                    AstralInterpretiveValenceModel.name == name
                )
            )
            is None
        ):
            db.add(AstralInterpretiveValenceModel(name=name))
    db.flush()


def _sync_astral_aspects(db: Session) -> None:
    """Synchronise les aspects stables et leur famille depuis le JSON canonique."""
    families = _ensure_astral_aspect_families(db)
    expected_codes: set[str] = set()
    for source_row in _load_aspects():
        code = str(source_row["code"])
        family_name = str(source_row["family"])
        if family_name not in families:
            raise ValueError(f"unknown aspect family: {family_name}")
        expected_codes.add(code)
        aspect = db.scalar(select(AspectModel).where(AspectModel.code == code))
        if aspect is None:
            db.add(
                AspectModel(
                    code=code,
                    name=str(source_row["name"]),
                    angle=float(source_row["angle"]),
                    family=families[family_name],
                )
            )
            continue
        aspect.name = str(source_row["name"])
        aspect.angle = float(source_row["angle"])
        aspect.family = families[family_name]
    db.execute(delete(AspectModel).where(AspectModel.code.not_in(expected_codes)))
    db.flush()


def _sync_astral_aspect_profiles(db: Session, reference_version_id: int) -> None:
    """Synchronise les profils prédictifs d'aspects pour une version."""
    aspects = {row.code: row.id for row in db.scalars(select(AspectModel)).all()}
    expected_aspect_ids: set[int] = set()
    for source_row in _load_aspect_profiles():
        aspect_code = str(source_row["aspect_code"])
        if aspect_code not in aspects:
            raise ValueError(f"unknown aspect code in profiles: {aspect_code}")
        aspect_id = aspects[aspect_code]
        expected_aspect_ids.add(aspect_id)
        profile = db.scalar(
            select(AspectProfileModel).where(
                AspectProfileModel.reference_version_id == reference_version_id,
                AspectProfileModel.aspect_id == aspect_id,
            )
        )
        payload = {
            "intensity_weight": float(source_row["intensity_weight"]),
            "default_valence": str(source_row["default_valence"]),
            "interpretive_valence": str(source_row["interpretive_valence"]),
            "polarity_score": float(source_row["polarity_score"]),
            "energy_type": str(source_row["energy_type"]),
            "orb_multiplier": float(source_row["orb_multiplier"]),
            "phase_sensitive": bool(source_row["phase_sensitive"]),
            "phase_behavior_json": json.dumps(
                source_row["phase_behavior_json"], ensure_ascii=False
            ),
            "strength_thresholds_json": json.dumps(
                source_row["strength_thresholds_json"], ensure_ascii=False
            ),
            "micro_note": source_row.get("micro_note"),
        }
        if profile is None:
            db.add(
                AspectProfileModel(
                    reference_version_id=reference_version_id,
                    aspect_id=aspect_id,
                    **payload,
                )
            )
            continue
        for key, value in payload.items():
            setattr(profile, key, value)
    db.execute(
        delete(AspectProfileModel).where(
            AspectProfileModel.reference_version_id == reference_version_id,
            AspectProfileModel.aspect_id.not_in(expected_aspect_ids),
        )
    )
    db.flush()


def _sync_astral_aspect_definitions(db: Session, reference_version_id: int) -> None:
    """Synchronise les définitions d'aspects par système astrologique."""
    aspects = {row.code: row.id for row in db.scalars(select(AspectModel)).all()}
    systems = _ensure_astral_systems(db)
    modern_defaults: dict[str, dict[str, object]] = {}
    for group in _load_aspect_definition_groups():
        if str(group["astral_system_code"]) == "modern":
            modern_defaults = {str(row["aspect_code"]): row for row in group.get("definitions", [])}
            break
    expected_pairs: set[tuple[int, int]] = set()

    for group in _load_aspect_definition_groups():
        system_name = str(group["astral_system_code"])
        if system_name not in systems:
            raise ValueError(f"unknown astral system in aspect definitions: {system_name}")
        system_id = systems[system_name]
        definitions = {str(row["aspect_code"]): row for row in group.get("definitions", [])}
        disabled_codes = {str(code) for code in group.get("disabled_aspect_codes", [])}
        for aspect_code in disabled_codes:
            if aspect_code in modern_defaults and aspect_code not in definitions:
                definitions[aspect_code] = {
                    **modern_defaults[aspect_code],
                    "is_enabled": False,
                    "scoring_weight": 0.0,
                }
        for aspect_code, source_row in definitions.items():
            if aspect_code not in aspects:
                raise ValueError(f"unknown aspect code in definitions: {aspect_code}")
            aspect_id = aspects[aspect_code]
            expected_pairs.add((aspect_id, system_id))
            definition = db.scalar(
                select(AstralAspectDefinitionModel).where(
                    AstralAspectDefinitionModel.reference_version_id == reference_version_id,
                    AstralAspectDefinitionModel.aspect_id == aspect_id,
                    AstralAspectDefinitionModel.astral_system_id == system_id,
                )
            )
            payload = {
                "is_enabled": bool(source_row["is_enabled"]),
                "is_major": bool(source_row["is_major"]),
                "is_minor": bool(source_row["is_minor"]),
                "default_orb_deg": (
                    None
                    if source_row.get("default_orb_deg") is None
                    else float(source_row["default_orb_deg"])
                ),
                "display_priority": (
                    None
                    if source_row.get("display_priority") is None
                    else int(source_row["display_priority"])
                ),
                "interpretation_weight": float(source_row["interpretation_weight"]),
                "scoring_weight": float(source_row["scoring_weight"]),
                "micro_note": source_row.get("micro_note"),
            }
            if definition is None:
                db.add(
                    AstralAspectDefinitionModel(
                        reference_version_id=reference_version_id,
                        aspect_id=aspect_id,
                        astral_system_id=system_id,
                        **payload,
                    )
                )
                continue
            for key, value in payload.items():
                setattr(definition, key, value)
    valid_aspect_ids = {aspect_id for aspect_id, _system_id in expected_pairs}
    valid_system_ids = {system_id for _aspect_id, system_id in expected_pairs}
    db.execute(
        delete(AstralAspectDefinitionModel).where(
            AstralAspectDefinitionModel.reference_version_id == reference_version_id,
            AstralAspectDefinitionModel.aspect_id.not_in(valid_aspect_ids),
        )
    )
    db.execute(
        delete(AstralAspectDefinitionModel).where(
            AstralAspectDefinitionModel.reference_version_id == reference_version_id,
            AstralAspectDefinitionModel.astral_system_id.not_in(valid_system_ids),
        )
    )
    db.flush()


def _sync_astral_aspect_orb_rules(db: Session, reference_version_id: int) -> None:
    """Synchronise les exceptions d'orbes sans dupliquer les orbes standards."""
    aspects = {row.code: row.id for row in db.scalars(select(AspectModel)).all()}
    systems = _ensure_astral_systems(db)
    planets = {row.code: row.id for row in db.scalars(select(PlanetModel)).all()}
    expected_keys: set[tuple[object, ...]] = set()

    for group in _resolve_aspect_orb_rule_groups():
        system_code = str(group["astral_system_code"])
        if system_code not in systems:
            raise ValueError(f"unknown astral system in aspect orb rules: {system_code}")
        system_id = systems[system_code]
        for source_row in group["rules"]:
            aspect_code = str(source_row["aspect_code"])
            if aspect_code not in aspects:
                raise ValueError(f"unknown aspect code in orb rules: {aspect_code}")
            source_planet_code = source_row.get("source_planet_code")
            target_planet_code = source_row.get("target_planet_code")
            source_planet_id = (
                None if source_planet_code is None else planets[str(source_planet_code)]
            )
            target_planet_id = (
                None if target_planet_code is None else planets[str(target_planet_code)]
            )
            payload = {
                "reference_version_id": reference_version_id,
                "astral_system_id": system_id,
                "aspect_id": aspects[aspect_code],
                "calculation_context": str(source_row["calculation_context"]),
                "source_body_type": str(source_row["source_body_type"]),
                "source_planet_id": source_planet_id,
                "source_point_code": source_row.get("source_point_code"),
                "target_body_type": str(source_row["target_body_type"]),
                "target_planet_id": target_planet_id,
                "target_point_code": source_row.get("target_point_code"),
                "orb_deg": float(source_row["orb_deg"]),
                "priority": int(source_row["priority"]),
                "is_enabled": bool(source_row["is_enabled"]),
                "micro_note": source_row.get("micro_note"),
            }
            key = (
                payload["reference_version_id"],
                payload["astral_system_id"],
                payload["aspect_id"],
                payload["calculation_context"],
                payload["source_body_type"],
                payload["source_planet_id"],
                payload["source_point_code"],
                payload["target_body_type"],
                payload["target_planet_id"],
                payload["target_point_code"],
            )
            expected_keys.add(key)
            rule = db.scalar(
                select(AstralAspectOrbRuleModel).where(
                    AstralAspectOrbRuleModel.reference_version_id == reference_version_id,
                    AstralAspectOrbRuleModel.astral_system_id == system_id,
                    AstralAspectOrbRuleModel.aspect_id == aspects[aspect_code],
                    AstralAspectOrbRuleModel.calculation_context == payload["calculation_context"],
                    AstralAspectOrbRuleModel.source_body_type == payload["source_body_type"],
                    AstralAspectOrbRuleModel.source_planet_id == source_planet_id,
                    AstralAspectOrbRuleModel.source_point_code == payload["source_point_code"],
                    AstralAspectOrbRuleModel.target_body_type == payload["target_body_type"],
                    AstralAspectOrbRuleModel.target_planet_id == target_planet_id,
                    AstralAspectOrbRuleModel.target_point_code == payload["target_point_code"],
                )
            )
            if rule is None:
                db.add(AstralAspectOrbRuleModel(**payload))
                continue
            for field_name, field_value in payload.items():
                setattr(rule, field_name, field_value)

    for existing in db.scalars(
        select(AstralAspectOrbRuleModel).where(
            AstralAspectOrbRuleModel.reference_version_id == reference_version_id
        )
    ).all():
        existing_key = (
            existing.reference_version_id,
            existing.astral_system_id,
            existing.aspect_id,
            existing.calculation_context,
            existing.source_body_type,
            existing.source_planet_id,
            existing.source_point_code,
            existing.target_body_type,
            existing.target_planet_id,
            existing.target_point_code,
        )
        if existing_key not in expected_keys:
            db.delete(existing)
    db.flush()


def ensure_astral_aspect_reference_data(db: Session, reference_version_id: int) -> None:
    """Synchronise les référentiels d'aspects et leurs profils versionnés."""
    _ensure_astral_valences(db)
    _sync_astral_aspects(db)
    version = db.get(ReferenceVersionModel, reference_version_id)
    profiles_count = db.scalar(
        select(func.count())
        .select_from(AspectProfileModel)
        .where(AspectProfileModel.reference_version_id == reference_version_id)
    )
    definitions_count = db.scalar(
        select(func.count())
        .select_from(AstralAspectDefinitionModel)
        .where(AstralAspectDefinitionModel.reference_version_id == reference_version_id)
    )
    orb_rules_count = db.scalar(
        select(func.count())
        .select_from(AstralAspectOrbRuleModel)
        .where(AstralAspectOrbRuleModel.reference_version_id == reference_version_id)
    )
    if (
        version is not None
        and version.is_locked
        and profiles_count == EXPECTED_COUNTS["astral_aspect_profiles"]
        and definitions_count == EXPECTED_COUNTS["astral_aspect_definitions"]
        and orb_rules_count == EXPECTED_COUNTS["astral_aspect_orb_rules"]
    ):
        return
    _sync_astral_aspect_profiles(db, reference_version_id)
    _sync_astral_aspect_definitions(db, reference_version_id)
    _sync_astral_aspect_orb_rules(db, reference_version_id)


def ensure_astral_sign_profiles(db: Session) -> None:
    """Crée les profils structurels des douze signes à partir des taxonomies."""
    elements = _ensure_taxonomy(
        db,
        AstralElementModel,
        [("fire", "Fire"), ("earth", "Earth"), ("air", "Air"), ("water", "Water")],
    )
    modalities = _ensure_taxonomy(
        db,
        AstralModalityModel,
        [("cardinal", "Cardinal"), ("fixed", "Fixed"), ("mutable", "Mutable")],
    )
    polarities = _ensure_taxonomy(
        db,
        AstralPolarityModel,
        [("yang", "Yang"), ("yin", "Yin")],
    )
    signs = {sign.code: sign.id for sign in db.scalars(select(AstralSignModel)).all()}
    keywords_by_sign = _load_sign_keywords()

    for sign_code, element_code, modality_code, polarity_code in SIGN_PROFILE_DATA:
        keywords_json = json.dumps(
            _required_keyword_list(keywords_by_sign, sign_code, "keywords"),
            ensure_ascii=False,
        )
        shadow_keywords_json = json.dumps(
            _required_keyword_list(keywords_by_sign, sign_code, "shadow_keywords"),
            ensure_ascii=False,
        )
        profile = db.scalar(
            select(AstralSignProfileModel).where(
                AstralSignProfileModel.astral_sign_id == signs[sign_code]
            )
        )
        if profile is None:
            db.add(
                AstralSignProfileModel(
                    astral_sign_id=signs[sign_code],
                    astral_element_id=elements[element_code],
                    astral_modality_id=modalities[modality_code],
                    astral_polarity_id=polarities[polarity_code],
                    keywords_json=keywords_json,
                    shadow_keywords_json=shadow_keywords_json,
                )
            )
            continue
        profile.astral_element_id = elements[element_code]
        profile.astral_modality_id = modalities[modality_code]
        profile.astral_polarity_id = polarities[polarity_code]
        profile.keywords_json = keywords_json
        profile.shadow_keywords_json = shadow_keywords_json
    db.flush()


def _ensure_astral_planet_sign_dignities(db: Session) -> None:
    """Synchronise les dignités planétaires par signe depuis le JSON canonique."""
    _ensure_astral_dignity_types(db)
    systems = _ensure_astral_systems(db)
    dignity_types = {row.code: row.id for row in db.scalars(select(AstralDignityTypeModel)).all()}
    sign_ids = {row.code: row.id for row in db.scalars(select(AstralSignModel)).all()}
    planet_ids = {row.code: row.id for row in db.scalars(select(PlanetModel)).all()}
    expected_ids: set[int] = set()

    for source_row in _load_planet_sign_dignities():
        row_id = int(source_row["id"])
        source_sign_id = int(source_row["astral_sign_id"])
        source_planet_id = int(source_row["planet_id"])
        sign_code = SIGN_CODE_BY_SOURCE_ID.get(source_sign_id)
        planet_code = PLANET_CODE_BY_SOURCE_ID.get(source_planet_id)
        dignity_type = str(source_row["dignity_type"])
        system = str(source_row["system"])
        if sign_code not in sign_ids:
            raise ValueError(f"unknown astral_sign_id: {source_sign_id}")
        if planet_code not in planet_ids:
            raise ValueError(f"unknown astral_planet_id: {source_planet_id}")
        if dignity_type not in dignity_types:
            raise ValueError(f"unknown dignity_type: {dignity_type}")
        if system not in systems:
            raise ValueError(f"unknown astral system: {system}")
        expected_ids.add(row_id)
        dignity = db.get(AstralPlanetSignDignityModel, row_id)
        if dignity is None:
            db.add(
                AstralPlanetSignDignityModel(
                    id=row_id,
                    astral_sign_id=sign_ids[sign_code],
                    astral_planet_id=planet_ids[planet_code],
                    astral_dignity_type_id=dignity_types[dignity_type],
                    astral_system_id=systems[system],
                    weight=float(source_row["weight"]),
                    is_primary=bool(source_row["is_primary"]),
                )
            )
            continue
        dignity.astral_sign_id = sign_ids[sign_code]
        dignity.astral_planet_id = planet_ids[planet_code]
        dignity.astral_dignity_type_id = dignity_types[dignity_type]
        dignity.astral_system_id = systems[system]
        dignity.weight = float(source_row["weight"])
        dignity.is_primary = bool(source_row["is_primary"])

    db.execute(
        delete(AstralPlanetSignDignityModel).where(
            AstralPlanetSignDignityModel.id.not_in(expected_ids)
        )
    )
    db.flush()


def ensure_astral_planet_sign_dignities(db: Session) -> None:
    """Synchronise les dignités stables requises par les maîtrises natales."""
    _ensure_astral_planet_sign_dignities(db)


def _check_counts(db: Session, reference_version_id: int) -> dict[str, int]:
    """Compte les artefacts attendus pour une version de référence donnée."""
    actual = {}
    actual["prediction_categories"] = db.scalar(
        select(func.count())
        .select_from(PredictionCategoryModel)
        .where(PredictionCategoryModel.reference_version_id == reference_version_id)
    )
    actual["planet_profiles"] = db.scalar(
        select(func.count())
        .select_from(PlanetProfileModel)
        .where(PlanetProfileModel.reference_version_id == reference_version_id)
    )
    actual["house_profiles"] = db.scalar(
        select(func.count())
        .select_from(HouseProfileModel)
        .where(HouseProfileModel.reference_version_id == reference_version_id)
    )
    actual["astral_house_interpretation_profiles"] = db.scalar(
        select(func.count())
        .select_from(HouseInterpretationProfileModel)
        .where(HouseInterpretationProfileModel.reference_version_id == reference_version_id)
    )
    actual["astral_planet_interpretation_profiles"] = db.scalar(
        select(func.count())
        .select_from(AstralPlanetInterpretationProfileModel)
        .where(AstralPlanetInterpretationProfileModel.reference_version_id == reference_version_id)
    )
    actual["astral_aspect_interpretation_profiles"] = db.scalar(
        select(func.count())
        .select_from(AstralAspectInterpretationProfileModel)
        .where(AstralAspectInterpretationProfileModel.reference_version_id == reference_version_id)
    )
    actual["astral_aspect_profiles"] = db.scalar(
        select(func.count())
        .select_from(AspectProfileModel)
        .where(AspectProfileModel.reference_version_id == reference_version_id)
    )
    actual["astral_aspect_definitions"] = db.scalar(
        select(func.count())
        .select_from(AstralAspectDefinitionModel)
        .where(AstralAspectDefinitionModel.reference_version_id == reference_version_id)
    )
    actual["astral_aspect_orb_rules"] = db.scalar(
        select(func.count())
        .select_from(AstralAspectOrbRuleModel)
        .where(AstralAspectOrbRuleModel.reference_version_id == reference_version_id)
    )
    actual["astral_default_valence"] = db.scalar(
        select(func.count()).select_from(AstralDefaultValenceModel)
    )
    actual["astral_interpretive_valence"] = db.scalar(
        select(func.count()).select_from(AstralInterpretiveValenceModel)
    )
    actual["astro_points"] = db.scalar(select(func.count()).select_from(AstroPointModel))
    actual["astral_dignity_type"] = db.scalar(
        select(func.count()).select_from(AstralDignityTypeModel)
    )
    actual["astral_elements"] = db.scalar(select(func.count()).select_from(AstralElementModel))
    actual["astral_modalities"] = db.scalar(select(func.count()).select_from(AstralModalityModel))
    actual["astral_polarities"] = db.scalar(select(func.count()).select_from(AstralPolarityModel))
    actual["astral_planet_sign_dignities"] = db.scalar(
        select(func.count()).select_from(AstralPlanetSignDignityModel)
    )
    actual["astral_sign_profiles"] = db.scalar(
        select(func.count()).select_from(AstralSignProfileModel)
    )
    actual["astral_planet_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PlanetCategoryWeightModel)
        .where(PlanetCategoryWeightModel.reference_version_id == reference_version_id)
    )
    actual["house_category_weights"] = db.scalar(
        select(func.count())
        .select_from(HouseCategoryWeightModel)
        .where(HouseCategoryWeightModel.reference_version_id == reference_version_id)
    )
    actual["point_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PointCategoryWeightModel)
        .where(PointCategoryWeightModel.reference_version_id == reference_version_id)
    )

    # Les rulesets sont rattachés à la version de référence ciblée.
    rulesets = db.scalars(
        select(PredictionRulesetModel).where(
            PredictionRulesetModel.reference_version_id == reference_version_id
        )
    ).all()

    actual["ruleset_event_types"] = 0
    actual["ruleset_parameters"] = 0

    for ruleset in rulesets:
        actual["ruleset_event_types"] += db.scalar(
            select(func.count())
            .select_from(RulesetEventTypeModel)
            .where(RulesetEventTypeModel.ruleset_id == ruleset.id)
        )
        actual["ruleset_parameters"] += db.scalar(
            select(func.count())
            .select_from(RulesetParameterModel)
            .where(RulesetParameterModel.ruleset_id == ruleset.id)
        )

    return actual


def _seed_ruleset_content(db: Session, ruleset_id: int):
    """Alimente les types d événements et paramètres d un ruleset donné."""
    # Types d événements : (code, groupe, priorité, poids de base).
    # Les priorités sont calibrées par rapport à
    # TurningPointDetector.PRIORITY_PIVOT_THRESHOLD = 65 :
    #   >= 65 : peut déclencher un pivot à haute priorité
    #   < 65 : enrichit seulement un pivot déjà existant
    event_types_data = [
        ("aspect_exact_to_angle", "aspect", 80, 2.0),  # above pivot threshold
        ("aspect_exact_to_luminary", "aspect", 75, 1.8),  # above pivot threshold
        ("aspect_exact_to_personal", "aspect", 68, 1.5),  # slightly above pivot threshold
        ("aspect_enter_orb", "aspect", 40, 1.0),  # below threshold — enriches only
        ("aspect_exit_orb", "aspect", 25, 0.5),  # below threshold
        ("moon_sign_ingress", "ingress", 72, 1.5),  # above pivot threshold
        ("asc_sign_change", "ingress", 78, 2.0),  # above pivot threshold — structurant
        ("planetary_hour_change", "timing", 20, 0.8),  # well below threshold
    ]
    for code, group, priority, weight in event_types_data:
        db.add(
            RulesetEventTypeModel(
                ruleset_id=ruleset_id,
                code=code,
                name=code.replace("_", " ").title(),
                event_group=group,
                priority=priority,
                base_weight=weight,
            )
        )

    # Paramètres runtime du ruleset.
    params_data = [
        ("orb_multiplier_applying", "float", "1.2"),
        ("orb_multiplier_exact", "float", "1.5"),
        ("orb_multiplier_separating", "float", "0.8"),
        ("turning_point_threshold", "float", "0.7"),
        ("score_clamp_min", "float", "0.0"),
        ("score_clamp_max", "float", "100.0"),
        ("top_turning_points_count", "int", "3"),
        ("normalization_method", "string", "percentile"),
    ]
    for key, dtype, val in params_data:
        db.add(
            RulesetParameterModel(
                ruleset_id=ruleset_id, param_key=key, param_value=val, data_type=dtype
            )
        )


def _ensure_legacy_reference_version_seeded(db: Session) -> ReferenceVersionModel:
    """Réamorce la référence 1.0.0 quand une base migrée ne contient aucune donnée."""
    repo = ReferenceRepository(db)
    v1 = repo.get_version("1.0.0")
    if v1 is None:
        print("Creating reference version 1.0.0...")
        v1 = repo.create_version("1.0.0", description="Initial seeded version")

    repo.seed_version_defaults()
    sync_house_system_seed_data(db)
    db.flush()
    _ensure_astral_dignity_types(db)
    _ensure_astral_systems(db)
    ensure_astral_sign_profiles(db)
    _ensure_astral_planet_sign_dignities(db)
    ensure_astral_aspect_reference_data(db, v1.id)
    sync_house_interpretation_profiles(db, v1.id)
    sync_planet_interpretation_profiles(db, v1.id)
    sync_aspect_interpretation_profiles(db, v1.id)
    sync_astral_translation_seed_data(db, v1.id)
    db.flush()
    return v1


def run_prediction_reference_seed(db: Session) -> None:
    """Crée ou répare le seed canonique de la référence 2.0.0 et de ses rulesets."""
    # 1. Vérification d idempotence.
    v2 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0"))
    if v2 is not None:
        _ensure_astral_dignity_types(db)
        _ensure_astral_systems(db)
        if db.scalar(select(func.count()).select_from(AstralSignModel)) > 0:
            ensure_astral_sign_profiles(db)
            _ensure_astral_planet_sign_dignities(db)
            sync_house_interpretation_profiles(db, v2.id)
            sync_planet_interpretation_profiles(db, v2.id)
            ensure_astral_aspect_reference_data(db, v2.id)
            sync_aspect_interpretation_profiles(db, v2.id)
            sync_astral_translation_seed_data(db, v2.id)
        actual = _check_counts(db, v2.id)

        # On exige au minimum la présence du ruleset 2.0.0 pour considérer
        # l amorçage comme partiellement réalisé.
        ruleset_v2 = db.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "2.0.0",
            )
        )

        all_ok = (
            all(actual.get(k, 0) == v for k, v in EXPECTED_COUNTS.items())
            and ruleset_v2 is not None
        )

        if all_ok and v2.is_locked:
            print("2.0.0 already seeded and locked — skipping")
            return

        if not v2.is_locked:
            print("2.0.0 exists but is unlocked — proceeding with repair/seed")
            # Chemin de réparation : purge des données partielles avant reseed.
            db.execute(
                delete(RulesetEventTypeModel).where(
                    RulesetEventTypeModel.ruleset_id.in_(
                        select(PredictionRulesetModel.id).where(
                            PredictionRulesetModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(RulesetParameterModel).where(
                    RulesetParameterModel.ruleset_id.in_(
                        select(PredictionRulesetModel.id).where(
                            PredictionRulesetModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(PredictionRulesetModel).where(
                    PredictionRulesetModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(PointCategoryWeightModel).where(
                    PointCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(HouseCategoryWeightModel).where(
                    HouseCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(PlanetCategoryWeightModel).where(
                    PlanetCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(HouseProfileModel).where(HouseProfileModel.reference_version_id == v2.id)
            )
            db.execute(
                delete(AstralHouseInterpretationProfileTranslationModel).where(
                    AstralHouseInterpretationProfileTranslationModel.source_profile_id.in_(
                        select(HouseInterpretationProfileModel.id).where(
                            HouseInterpretationProfileModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(AstralAspectInterpretationProfileTranslationModel).where(
                    AstralAspectInterpretationProfileTranslationModel.source_profile_id.in_(
                        select(AstralAspectInterpretationProfileModel.id).where(
                            AstralAspectInterpretationProfileModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(AstralPlanetInterpretationProfileTranslationModel).where(
                    AstralPlanetInterpretationProfileTranslationModel.source_profile_id.in_(
                        select(AstralPlanetInterpretationProfileModel.id).where(
                            AstralPlanetInterpretationProfileModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(HouseInterpretationProfileModel).where(
                    HouseInterpretationProfileModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(AstralAspectInterpretationProfileModel).where(
                    AstralAspectInterpretationProfileModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(AstralPlanetInterpretationProfileModel).where(
                    AstralPlanetInterpretationProfileModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(PlanetProfileModel).where(PlanetProfileModel.reference_version_id == v2.id)
            )
            db.execute(delete(AstralSignProfileModel))
            db.execute(
                delete(AstralAspectOrbRuleModel).where(
                    AstralAspectOrbRuleModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(AstralAspectDefinitionModel).where(
                    AstralAspectDefinitionModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(AspectProfileModel).where(AspectProfileModel.reference_version_id == v2.id)
            )
            db.execute(
                delete(PredictionCategoryModel).where(
                    PredictionCategoryModel.reference_version_id == v2.id
                )
            )

            # Les structures sont stables et globales. En réparation on vérifie
            # seulement que le vocabulaire de base existe.
            has_basic_data = db.scalar(select(func.count()).select_from(PlanetModel)) > 0
            if not has_basic_data:
                repo = ReferenceRepository(db)
                repo.seed_version_defaults()
            db.flush()
            ensure_astral_sign_profiles(db)
            _ensure_astral_planet_sign_dignities(db)
            ensure_astral_aspect_reference_data(db, v2.id)
            sync_planet_interpretation_profiles(db, v2.id)
            sync_aspect_interpretation_profiles(db, v2.id)
            sync_astral_translation_seed_data(db, v2.id)
        else:
            # État corrompu ou incomplet alors que la version est verrouillée.
            lines = [
                (
                    "ERROR: 2.0.0 exists and is LOCKED but is incomplete. "
                    "Manual investigation required."
                )
            ]
            for k, expected in EXPECTED_COUNTS.items():
                got = actual.get(k, 0)
                status = "OK" if got == expected else f"MISMATCH (expected {expected}, got {got})"
                lines.append(f"  {k}: {status}")
            lines.append(f"  ruleset_v2_exists: {ruleset_v2 is not None}")
            lines.append(f"  is_locked: {v2.is_locked}")
            raise PredictionReferenceSeedAbortError("\n".join(lines))
    else:
        # 2. Initialisation de V1 et V2.
        v1 = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        if not v1:
            v1 = _ensure_legacy_reference_version_seeded(db)

        print("Creating reference version 2.0.0...")
        repo = ReferenceRepository(db)
        v2 = repo.create_version(
            version="2.0.0",
            description="Moteur de prédiction quotidienne v1 — référentiel sémantique complet",
        )
        v2.is_locked = False
        db.flush()

        # 3. Les structures stables sont resynchronisées depuis les JSON canoniques.
        print("Syncing stable astrology structures...")
        repo.seed_version_defaults()
        db.flush()
        _ensure_astral_dignity_types(db)
        _ensure_astral_systems(db)
        ensure_astral_sign_profiles(db)
        _ensure_astral_planet_sign_dignities(db)
        ensure_astral_aspect_reference_data(db, v2.id)

    # 4. Alimentation des catégories de prédiction.
    print("Seeding prediction categories...")
    categories_data = [
        ("energy", "Energy", "Énergie", 1),
        ("mood", "Mood", "Humeur", 2),
        ("health", "Health", "Santé", 3),
        ("work", "Work", "Travail", 4),
        ("career", "Career", "Carrière", 5),
        ("money", "Money", "Argent", 6),
        ("love", "Love", "Amour", 7),
        ("sex_intimacy", "Sex & Intimacy", "Intimité", 8),
        ("family_home", "Family & Home", "Famille & Foyer", 9),
        ("social_network", "Social Network", "Réseau social", 10),
        ("communication", "Communication", "Communication", 11),
        ("pleasure_creativity", "Pleasure & Creativity", "Plaisir & Créativité", 12),
    ]
    for code, name, display_name, order in categories_data:
        db.add(
            PredictionCategoryModel(
                reference_version_id=v2.id,
                code=code,
                name=name,
                display_name=display_name,
                sort_order=order,
                is_public=True,
                is_enabled=True,
            )
        )
    db.flush()

    # Résolution des identifiants utiles pour les étapes suivantes.
    categories = {
        c.code: c.id
        for c in db.scalars(
            select(PredictionCategoryModel).where(
                PredictionCategoryModel.reference_version_id == v2.id
            )
        ).all()
    }
    planets = {p.code: p.id for p in db.scalars(select(PlanetModel)).all()}

    # 5. Alimentation des profils planétaires.
    print("Seeding planet profiles...")
    planet_code_by_source_id = {
        source_id: code for source_id, code in PLANET_CODE_BY_SOURCE_ID.items()
    }
    for source_row in _load_daily_planet_profiles():
        planet_code = planet_code_by_source_id[int(source_row["planet_id"])]
        db.add(
            PlanetProfileModel(
                reference_version_id=v2.id,
                planet_id=planets[planet_code],
                weight_intraday=float(source_row["weight_intraday"]),
                weight_day_climate=float(source_row["weight_day_climate"]),
                daily_visibility_score=float(source_row["daily_visibility_score"]),
                daily_emotional_impact_score=float(source_row["daily_emotional_impact_score"]),
                daily_conscious_activation_score=float(
                    source_row["daily_conscious_activation_score"]
                ),
                is_enabled=bool(source_row["is_enabled"]),
                micro_note=(
                    None if source_row.get("micro_note") is None else str(source_row["micro_note"])
                ),
            )
        )

    # 6. Alimentation des profils de maisons.
    print("Seeding house profiles...")
    house_profiles_data = [
        # numéro, type, visibilité, priorité
        (1, "angular", 1.0, 10),
        (2, "succedent", 0.7, 6),
        (3, "cadent", 0.5, 4),
        (4, "angular", 0.9, 9),
        (5, "succedent", 0.7, 6),
        (6, "cadent", 0.6, 5),
        (7, "angular", 0.9, 9),
        (8, "succedent", 0.7, 7),
        (9, "cadent", 0.5, 4),
        (10, "angular", 1.0, 10),
        (11, "succedent", 0.6, 5),
        (12, "cadent", 0.4, 3),
    ]
    houses = {h.number: h.id for h in db.scalars(select(HouseModel)).all()}
    for num, kind, vis, prio in house_profiles_data:
        db.add(
            HouseProfileModel(
                reference_version_id=v2.id,
                house_id=houses[num],
                house_kind=kind,
                visibility_weight=vis,
                base_priority=prio,
            )
        )
    sync_house_interpretation_profiles(db, v2.id)
    sync_planet_interpretation_profiles(db, v2.id)

    # 7. Alimentation des poids planète -> catégorie.
    print("Seeding planet category weights...")
    pcw_data = [
        ("sun", "energy", 0.8, "primary"),
        ("sun", "mood", 0.6, "secondary"),
        ("sun", "health", 0.5, "secondary"),
        ("sun", "work", 0.6, "secondary"),
        ("sun", "career", 0.8, "primary"),
        ("sun", "money", 0.5, "secondary"),
        ("sun", "love", 0.5, "secondary"),
        ("sun", "pleasure_creativity", 0.6, "primary"),
        ("moon", "energy", 0.4, "secondary"),
        ("moon", "mood", 0.9, "primary"),
        ("moon", "health", 0.6, "primary"),
        ("moon", "love", 0.7, "primary"),
        ("moon", "sex_intimacy", 0.4, "secondary"),
        ("moon", "family_home", 0.8, "primary"),
        ("moon", "social_network", 0.4, "secondary"),
        ("moon", "pleasure_creativity", 0.4, "secondary"),
        ("mercury", "energy", 0.3, "secondary"),
        ("mercury", "mood", 0.4, "secondary"),
        ("mercury", "work", 0.8, "primary"),
        ("mercury", "career", 0.5, "secondary"),
        ("mercury", "money", 0.3, "secondary"),
        ("mercury", "love", 0.3, "secondary"),
        ("mercury", "social_network", 0.7, "secondary"),
        ("mercury", "communication", 0.9, "primary"),
        ("mercury", "pleasure_creativity", 0.4, "secondary"),
        ("venus", "energy", 0.3, "secondary"),
        ("venus", "mood", 0.6, "secondary"),
        ("venus", "health", 0.4, "secondary"),
        ("venus", "money", 0.6, "secondary"),
        ("venus", "love", 0.9, "primary"),
        ("venus", "sex_intimacy", 0.7, "primary"),
        ("venus", "family_home", 0.5, "secondary"),
        ("venus", "social_network", 0.6, "secondary"),
        ("venus", "communication", 0.4, "secondary"),
        ("venus", "pleasure_creativity", 0.8, "primary"),
        ("mars", "energy", 0.9, "primary"),
        ("mars", "mood", 0.4, "secondary"),
        ("mars", "health", 0.6, "secondary"),
        ("mars", "work", 0.7, "secondary"),
        ("mars", "career", 0.5, "secondary"),
        ("mars", "money", 0.3, "secondary"),
        ("mars", "love", 0.4, "secondary"),
        ("mars", "sex_intimacy", 0.8, "primary"),
        ("mars", "pleasure_creativity", 0.4, "secondary"),
        ("jupiter", "energy", 0.5, "secondary"),
        ("jupiter", "mood", 0.6, "secondary"),
        ("jupiter", "health", 0.4, "secondary"),
        ("jupiter", "work", 0.5, "secondary"),
        ("jupiter", "career", 0.8, "primary"),
        ("jupiter", "money", 0.7, "primary"),
        ("jupiter", "love", 0.4, "secondary"),
        ("jupiter", "family_home", 0.4, "secondary"),
        ("jupiter", "social_network", 0.6, "secondary"),
        ("jupiter", "communication", 0.4, "secondary"),
        ("jupiter", "pleasure_creativity", 0.6, "secondary"),
        ("saturn", "energy", 0.3, "secondary"),
        ("saturn", "work", 0.7, "primary"),
        ("saturn", "career", 0.7, "primary"),
        ("saturn", "money", 0.5, "secondary"),
        ("saturn", "health", 0.5, "secondary"),
        ("saturn", "family_home", 0.4, "secondary"),
        ("uranus", "energy", 0.4, "secondary"),
        ("uranus", "mood", 0.3, "secondary"),
        ("uranus", "work", 0.4, "secondary"),
        ("uranus", "career", 0.4, "secondary"),
        ("uranus", "sex_intimacy", 0.3, "secondary"),
        ("uranus", "social_network", 0.5, "secondary"),
        ("uranus", "communication", 0.4, "secondary"),
        ("uranus", "pleasure_creativity", 0.5, "secondary"),
        ("neptune", "mood", 0.5, "secondary"),
        ("neptune", "health", 0.3, "secondary"),
        ("neptune", "love", 0.5, "secondary"),
        ("neptune", "sex_intimacy", 0.4, "secondary"),
        ("neptune", "family_home", 0.3, "secondary"),
        ("neptune", "social_network", 0.4, "secondary"),
        ("neptune", "pleasure_creativity", 0.5, "secondary"),
        ("pluto", "energy", 0.5, "secondary"),
        ("pluto", "mood", 0.3, "secondary"),
        ("pluto", "health", 0.4, "secondary"),
        ("pluto", "work", 0.4, "secondary"),
        ("pluto", "career", 0.5, "secondary"),
        ("pluto", "money", 0.5, "secondary"),
        ("pluto", "love", 0.4, "secondary"),
        ("pluto", "sex_intimacy", 0.6, "secondary"),
        ("pluto", "pleasure_creativity", 0.3, "secondary"),
    ]
    for p_code, c_code, weight, role in pcw_data:
        db.add(
            PlanetCategoryWeightModel(
                reference_version_id=v2.id,
                planet_id=planets[p_code],
                category_id=categories[c_code],
                weight=weight,
                influence_role=role,
            )
        )

    # 8. Alimentation des poids maison -> catégorie.
    print("Seeding house category weights...")
    hcw_data = [
        (1, "energy", 0.8, "primary"),
        (1, "mood", 0.6, "secondary"),
        (2, "money", 0.9, "primary"),
        (2, "work", 0.5, "secondary"),
        (3, "communication", 0.9, "primary"),
        (3, "social_network", 0.5, "secondary"),
        (4, "family_home", 0.9, "primary"),
        (4, "mood", 0.5, "secondary"),
        (5, "pleasure_creativity", 0.9, "primary"),
        (5, "love", 0.6, "secondary"),
        (6, "health", 0.9, "primary"),
        (6, "work", 0.7, "secondary"),
        (7, "love", 0.8, "primary"),
        (7, "social_network", 0.6, "secondary"),
        (8, "sex_intimacy", 0.8, "primary"),
        (8, "money", 0.6, "secondary"),
        (9, "pleasure_creativity", 0.5, "secondary"),
        (9, "career", 0.4, "secondary"),
        (10, "career", 0.9, "primary"),
        (10, "work", 0.6, "secondary"),
        (11, "social_network", 0.9, "primary"),
        (11, "pleasure_creativity", 0.5, "secondary"),
        (12, "mood", 0.5, "secondary"),
        (12, "health", 0.4, "secondary"),
    ]
    for house_num, c_code, weight, role in hcw_data:
        db.add(
            HouseCategoryWeightModel(
                reference_version_id=v2.id,
                house_id=houses[house_num],
                category_id=categories[c_code],
                weight=weight,
                routing_role=role,
            )
        )

    # 9. Alimentation des points astrologiques.
    print("Seeding astro points...")
    points_data = [
        ("asc", "Ascendant", "angle"),
        ("dsc", "Descendant", "angle"),
        ("mc", "Midheaven (MC)", "angle"),
        ("ic", "Imum Coeli (IC)", "angle"),
    ]
    for code, name, ptype in points_data:
        existing_point = db.scalar(select(AstroPointModel).where(AstroPointModel.code == code))
        if existing_point is None:
            db.add(AstroPointModel(code=code, name=name, point_type=ptype))
    db.flush()

    # Alimentation des poids point -> catégorie.
    points = {p.code: p.id for p in db.scalars(select(AstroPointModel)).all()}
    pcw_points_data = [
        ("asc", "energy", 0.8),
        ("asc", "mood", 0.7),
        ("mc", "career", 0.9),
        ("mc", "work", 0.6),
        ("dsc", "love", 0.7),
        ("dsc", "social_network", 0.6),
        ("ic", "family_home", 0.9),
        ("ic", "mood", 0.5),
    ]
    for p_code, c_code, weight in pcw_points_data:
        db.add(
            PointCategoryWeightModel(
                reference_version_id=v2.id,
                point_id=points[p_code],
                category_id=categories[c_code],
                weight=weight,
            )
        )

    # 10. Consolidation des dignités qui portent les maîtrises de signes.
    print("Seeding planet sign dignities...")
    _ensure_astral_planet_sign_dignities(db)

    # 11. Alimentation des profils et définitions d aspects.
    print("Seeding aspect profiles...")
    ensure_astral_aspect_reference_data(db, v2.id)
    sync_aspect_interpretation_profiles(db, v2.id)
    sync_astral_translation_seed_data(db, v2.id)

    # 12. Alimentation du ruleset 1.0.0 (legacy).
    print("Seeding ruleset 1.0.0 (legacy)...")
    ruleset_v1 = PredictionRulesetModel(
        version="1.0.0",
        reference_version_id=v2.id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        description="Ruleset legacy (v1) rattaché à la référence 2.0.0",
        is_locked=False,
    )
    db.add(ruleset_v1)
    db.flush()
    _seed_ruleset_content(db, ruleset_v1.id)

    # 13. Alimentation du ruleset 2.0.0 (canonique).
    print("Seeding ruleset 2.0.0 (canonical)...")
    ruleset_v2 = PredictionRulesetModel(
        version="2.0.0",
        reference_version_id=v2.id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        description="Ruleset canonique v2 rattaché à la référence 2.0.0",
        is_locked=False,
    )
    db.add(ruleset_v2)
    db.flush()
    _seed_ruleset_content(db, ruleset_v2.id)
    db.flush()

    # 14. Validation des comptages attendus.
    print("Validating counts...")
    actual = _check_counts(db, v2.id)
    for k, expected in EXPECTED_COUNTS.items():
        got = actual.get(k, 0)
        if got != expected:
            raise ValueError(f"Validation failed for {k}: expected {expected}, got {got}")

    # 16. Verrouillage final de V2.
    print("Locking reference version 2.0.0...")
    v2.is_locked = True
    db.flush()
    print("Seed 31.3 completed successfully.")


__all__ = [
    "PredictionReferenceSeedAbortError",
    "ensure_astral_aspect_reference_data",
    "ensure_astral_planet_sign_dignities",
    "ensure_astral_sign_profiles",
    "run_prediction_reference_seed",
]
