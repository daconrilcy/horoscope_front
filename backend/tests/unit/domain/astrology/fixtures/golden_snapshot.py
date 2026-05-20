"""Normalisation des snapshots golden astrologiques.

Ce module de test compacte les sorties runtime en JSON stable pour verifier les
contrats publics sans capturer de champs volatils ou de traces ephemerides.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def normalize_golden_value(value: Any) -> Any:
    """Convertit une valeur runtime en structure JSON stable et arrondie."""
    if is_dataclass(value):
        return normalize_golden_value(asdict(value))
    if hasattr(value, "model_dump"):
        return normalize_golden_value(value.model_dump(mode="python"))
    if isinstance(value, dict):
        return {
            str(key): normalize_golden_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list | tuple):
        return [normalize_golden_value(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def load_snapshot(path: Path) -> dict[str, Any]:
    """Charge un snapshot JSON depuis le dossier d'evidence de la story."""
    return json.loads(path.read_text(encoding="utf-8"))
