"""Charge les catalogues astrologiques documentaires utilises par le seed SQL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def astrology_research_path(file_name: str) -> Path:
    """Construit le chemin vers une source JSON astrologique canonique."""
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "docs" / "recherches astro" / file_name


def load_aspect_family_names() -> tuple[str, ...]:
    """Charge les familles d'aspects depuis le fichier pluriel canonique."""
    source_path = astrology_research_path("astral_aspect_families.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    families = raw.get("family") if isinstance(raw, dict) else None
    if not isinstance(families, list) or not families:
        raise ValueError("aspect families source must contain a non-empty family list")
    return tuple(str(value) for value in families)


def load_aspect_rows() -> tuple[dict[str, Any], ...]:
    """Charge les aspects stables depuis la source JSON canonique."""
    source_path = astrology_research_path("aspects.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, list) or not raw:
        raise ValueError("aspects source must be a non-empty list")
    return tuple(dict(row) for row in raw)


def load_structural_reference_rows(section: str) -> tuple[dict[str, Any], ...]:
    """Charge une section du catalogue structurel astrologique."""
    source_path = astrology_research_path("structural_reference_catalog.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get(section) if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"structural reference section must be non-empty: {section}")
    return tuple(dict(row) for row in rows)


def load_astral_system_names() -> tuple[str, ...]:
    """Charge les systemes astraux depuis le JSON documentaire canonique."""
    source_path = astrology_research_path("astral_systems.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    systems = raw.get("name") if isinstance(raw, dict) else None
    if not isinstance(systems, list) or not systems:
        raise ValueError("astral systems source must contain a non-empty name list")
    return tuple(str(value) for value in systems)


def load_language_rows() -> tuple[dict[str, Any], ...]:
    """Charge les langues supportees depuis la source documentaire canonique."""
    source_path = Path(__file__).resolve().parents[5] / "docs" / "languages.json"
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


def load_astral_object_type_rows() -> tuple[dict[str, Any], ...]:
    """Charge les types d'objets astrologiques depuis la source canonique."""
    return _load_data_rows("astral_object_types.json", "object types")


def _load_data_rows(file_name: str, label: str) -> tuple[dict[str, Any], ...]:
    """Charge une liste `data` non vide depuis un fichier documentaire."""
    source_path = astrology_research_path(file_name)
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{label} source must contain data rows")
    return tuple(dict(row) for row in rows)
