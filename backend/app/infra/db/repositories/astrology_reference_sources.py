"""Charge les catalogues astrologiques documentaires utilises par le seed SQL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def astrology_research_path(file_name: str) -> Path:
    """Construit le chemin vers une source JSON astrologique canonique."""
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs" / "db_seeder" / "astrology" / file_name


def load_aspect_family_names() -> tuple[str, ...]:
    """Charge les familles d'aspects depuis le fichier pluriel canonique."""
    source_path = astrology_research_path("astral_aspect_families.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("aspect families source must contain a non-empty family list")
    return tuple(str(row["name"]) for row in rows)


def load_aspect_rows() -> tuple[dict[str, Any], ...]:
    """Charge les aspects stables depuis la source JSON canonique."""
    return _load_data_rows("astral_aspects.json", "aspects")


def load_structural_reference_rows(section: str) -> tuple[dict[str, Any], ...]:
    """Charge une section du catalogue structurel astrologique."""
    source_path = astrology_research_path("astral_structural_reference_catalog.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    data = raw.get("data") if isinstance(raw, dict) else None
    rows = data.get(section) if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"structural reference section must be non-empty: {section}")
    return tuple(dict(row) for row in rows)


def load_astral_planet_rows() -> tuple[dict[str, Any], ...]:
    """Charge les planètes canoniques depuis la table JSON dédiée."""
    return _load_data_rows("astral_planets.json", "astral planets")


def load_astral_sign_rows() -> tuple[dict[str, Any], ...]:
    """Charge les signes canoniques depuis la table JSON dédiée."""
    return _load_data_rows("astral_signs.json", "astral signs")


def load_astral_constellation_rows() -> tuple[dict[str, Any], ...]:
    """Charge les constellations canoniques depuis la table JSON dédiée."""
    return _load_data_rows("astral_constellations.json", "astral constellations")


def load_astral_hemisphere_rows() -> tuple[dict[str, Any], ...]:
    """Charge les hémisphères célestes depuis la table JSON dédiée."""
    return _load_data_rows("astral_hemispheres.json", "astral hemispheres")


def load_astral_zodiacal_reference_system_category_rows() -> tuple[dict[str, Any], ...]:
    """Charge les catégories de systèmes de référence zodiacaux."""
    return _load_data_rows(
        "astral_zodiacal_reference_system_categories.json",
        "zodiacal reference system categories",
    )


def load_astral_zodiacal_reference_system_rows() -> tuple[dict[str, Any], ...]:
    """Charge les systèmes de référence zodiacaux depuis la table JSON dédiée."""
    return _load_data_rows(
        "astral_zodiacal_reference_systems.json",
        "zodiacal reference systems",
    )


def load_astral_reference_epoch_rows() -> tuple[dict[str, Any], ...]:
    """Charge les époques de référence astronomiques depuis la table JSON dédiée."""
    return _load_data_rows("astral_reference_epochs.json", "astral reference epochs")


def load_astral_reference_source_rows() -> tuple[dict[str, Any], ...]:
    """Charge les sources de référence astrales depuis la table JSON dédiée."""
    return _load_data_rows("astral_reference_sources.json", "astral reference sources")


def load_astral_fixed_star_rows() -> tuple[dict[str, Any], ...]:
    """Charge les étoiles fixes canoniques depuis la table JSON dédiée."""
    return _load_data_rows("astral_fixed_stars.json", "astral fixed stars")


def load_astral_fixed_star_keyword_rows() -> tuple[dict[str, Any], ...]:
    """Charge les groupes de mots-clés des étoiles fixes."""
    return _load_data_rows("astral_fixed_star_keywords.json", "astral fixed star keywords")


def load_astral_fixed_star_definition_rows() -> tuple[dict[str, Any], ...]:
    """Charge les définitions astronomiques et astrologiques des étoiles fixes."""
    return _load_data_rows("astral_fixed_star_definitions.json", "astral fixed star definitions")


def load_astral_fixed_star_keyword_translation_rows() -> tuple[dict[str, Any], ...]:
    """Charge les traductions des mots-clés d'étoiles fixes."""
    source_path = (
        astrology_research_path("translation") / "astral_fixed_star_keyword_translations.json"
    )
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_fixed_star_keyword_translations":
        raise ValueError("astral fixed star keyword translations target an unexpected table")
    data = raw.get("data")
    rows = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("astral fixed star keyword translations must contain data.keywords rows")
    return tuple(dict(row) for row in rows)


def load_astral_point_family_rows() -> tuple[dict[str, Any], ...]:
    """Charge les familles de points astrologiques calculés."""
    return _load_data_rows("astral_point_families.json", "astral point families")


def load_astral_point_rows() -> tuple[dict[str, Any], ...]:
    """Charge les points astrologiques calculés canoniques."""
    return _load_data_rows("astral_points.json", "astral points")


def load_astral_point_calculation_variant_rows() -> tuple[dict[str, Any], ...]:
    """Charge les variantes de calcul des points astrologiques."""
    return _load_data_rows(
        "astral_point_calculation_variants.json",
        "astral point calculation variants",
    )


def load_astral_point_alias_rows() -> tuple[dict[str, Any], ...]:
    """Charge les alias et clés moteur des points astrologiques."""
    return _load_data_rows("astral_point_aliases.json", "astral point aliases")


def load_astral_point_interpretation_keyword_rows() -> tuple[dict[str, Any], ...]:
    """Charge les mots-clés interprétatifs des points astrologiques."""
    return _load_data_rows(
        "astral_point_interpretation_keywords.json",
        "astral point interpretation keywords",
    )


def load_astral_point_interpretation_profile_rows() -> tuple[dict[str, Any], ...]:
    """Charge les profils éditoriaux des points astrologiques."""
    return _load_data_rows(
        "astral_point_interpretation_profiles.json",
        "astral point interpretation profiles",
    )


def load_astral_point_interpretation_keyword_translation_rows() -> tuple[dict[str, Any], ...]:
    """Charge les traductions des mots-clés des points astrologiques."""
    source_path = (
        astrology_research_path("translation")
        / "astral_point_interpretation_keyword_translations.json"
    )
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if (
        not isinstance(raw, dict)
        or raw.get("name") != "astral_point_interpretation_keyword_translations"
    ):
        raise ValueError("astral point keyword translations target an unexpected table")
    data = raw.get("data")
    rows = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("astral point keyword translations must contain data.keywords rows")
    return tuple(dict(row) for row in rows)


def load_astral_system_names() -> tuple[str, ...]:
    """Charge les systemes astraux depuis le JSON documentaire canonique."""
    source_path = astrology_research_path("astral_systems.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("astral systems source must contain a non-empty name list")
    return tuple(str(row["name"]) for row in rows)


def load_language_rows() -> tuple[dict[str, Any], ...]:
    """Charge les langues supportees depuis la source documentaire canonique."""
    source_path = Path(__file__).resolve().parents[5] / "docs" / "db_seeder" / "languages.json"
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("languages source must contain data rows")
    return tuple(dict(row) for row in rows)


def load_house_axis_definition_rows() -> tuple[dict[str, Any], ...]:
    """Charge les definitions structurelles d'axes de maisons."""
    source_path = astrology_research_path("astral_house_axis_definitions.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("house axis definitions source must contain data rows")
    return tuple(dict(row) for row in rows)


def load_house_axis_member_rows() -> tuple[dict[str, Any], ...]:
    """Charge les associations structurelles maisons/axes."""
    source_path = astrology_research_path("astral_house_axis_members.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("house axis members source must contain data rows")
    return tuple(dict(row) for row in rows)


def load_astral_angle_point_rows() -> tuple[dict[str, Any], ...]:
    """Charge les angles astrologiques structurels depuis la source canonique."""
    return _load_data_rows("astral_angle_points.json", "angle points")


def load_astral_astrological_role_rows() -> tuple[dict[str, Any], ...]:
    """Charge les rôles astrologiques structurels depuis la source canonique."""
    return _load_data_rows("astral_astrological_roles.json", "astrological roles")


def load_astral_calculation_type_rows() -> tuple[dict[str, Any], ...]:
    """Charge les types de calcul astrologique depuis la source canonique."""
    return _load_data_rows("astral_calculation_types.json", "calculation types")


def load_astral_house_modality_rows() -> tuple[dict[str, Any], ...]:
    """Charge les modalités de maisons astrologiques depuis la source canonique."""
    return _load_data_rows("astral_house_modalities.json", "house modalities")


def load_astral_house_system_rows() -> tuple[dict[str, Any], ...]:
    """Charge les systèmes de maisons astrologiques depuis la source canonique."""
    return _load_data_rows("astral_house_system.json", "house systems")


def load_astral_object_type_rows() -> tuple[dict[str, Any], ...]:
    """Charge les types d'objets astrologiques depuis la source canonique."""
    return _load_data_rows("astral_object_types.json", "object types")


def load_astral_speed_rows() -> tuple[dict[str, Any], ...]:
    """Charge les classes de vitesse astrologiques depuis la source canonique."""
    return _load_data_rows("astral_speed.json", "speed classes")


def load_astral_typical_polarity_rows() -> tuple[dict[str, Any], ...]:
    """Charge les polarites typiques astrologiques depuis la source canonique."""
    return _load_data_rows("astral_typical_polarities.json", "typical polarities")


def load_astral_planet_definition_rows() -> tuple[dict[str, Any], ...]:
    """Charge les definitions structurelles planetaires depuis la source canonique."""
    return _load_data_rows("astral_planet_definitions.json", "planet definitions")


def _load_data_rows(file_name: str, label: str) -> tuple[dict[str, Any], ...]:
    """Charge une liste `data` non vide depuis un fichier documentaire."""
    source_path = astrology_research_path(file_name)
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{label} source must contain data rows")
    return tuple(dict(row) for row in rows)
