"""Centralise la validation des listes issues des profils d'interpretation."""

from __future__ import annotations

from typing import Any


def required_profile_values(profile: dict[str, Any], field_name: str) -> tuple[str, ...]:
    """Extrait une liste obligatoire non vide depuis un profil documentaire."""
    values = profile.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"aspect interpretation profile misses {field_name}")
    normalized_values = tuple(str(value).strip() for value in values)
    if any(not value for value in normalized_values):
        raise ValueError(f"aspect interpretation profile misses {field_name}")
    return normalized_values


def optional_profile_values(profile: dict[str, Any], field_name: str) -> tuple[str, ...]:
    """Extrait une liste optionnelle depuis un profil documentaire."""
    values = profile.get(field_name)
    if not isinstance(values, list):
        return ()
    return tuple(str(value).strip() for value in values if str(value).strip())
