# Calcul canonique des hash de projection persistable.
"""Normalise les payloads de projection avant calcul SHA-256."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def canonical_projection_json(payload: Any) -> str:
    """Retourne le JSON canonique stable d'un payload de projection."""
    return json.dumps(
        projection_value_to_jsonable(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def compute_projection_hash(payload: Any) -> str:
    """Calcule le SHA-256 hexadécimal depuis le JSON canonique UTF-8."""
    canonical_json = canonical_projection_json(payload)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def projection_value_to_jsonable(value: Any) -> Any:
    """Convertit les contrats immuables en structures JSON déterministes."""
    if is_dataclass(value) and not isinstance(value, type):
        return projection_value_to_jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): projection_value_to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [projection_value_to_jsonable(item) for item in value]
    return value
