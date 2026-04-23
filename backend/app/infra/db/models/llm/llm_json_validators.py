# Validateurs JSON partages par les modeles LLM.
"""Regroupe les validations structurelles des champs JSON bornes."""

from __future__ import annotations

from typing import Any


def validate_string_list_field(field_name: str, value: Any) -> list[str]:
    """Valide et normalise une liste JSON de chaines non vides."""
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of strings.")

    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name} must contain only non-empty strings.")
        normalized.append(item.strip())
    return normalized


def validate_persona_formatting(value: Any) -> dict[str, bool]:
    """Valide le format JSON explicite des options de presentation d'un persona."""
    if not isinstance(value, dict):
        raise ValueError("formatting must be an object.")

    allowed_keys = {"sections", "bullets", "emojis"}
    unknown_keys = set(value) - allowed_keys
    if unknown_keys:
        unknown = ", ".join(sorted(str(key) for key in unknown_keys))
        raise ValueError(f"formatting contains unsupported keys: {unknown}.")

    formatting = {"sections": True, "bullets": False, "emojis": False}
    for key, raw in value.items():
        if not isinstance(raw, bool):
            raise ValueError(f"formatting.{key} must be a boolean.")
        formatting[str(key)] = raw
    return formatting
