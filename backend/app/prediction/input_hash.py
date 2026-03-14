import hashlib
import json
from datetime import date
from enum import Enum
from typing import Any


def _canonicalize_value(value: Any) -> Any:
    """Convert supported Python values into a stable JSON-serializable shape."""
    if isinstance(value, dict):
        return {
            str(key): _canonicalize_value(item)
            for key, item in sorted(value.items(), key=lambda entry: str(entry[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_canonicalize_value(item) for item in value]
    if isinstance(value, (date, Enum)):
        return value.isoformat() if isinstance(value, date) else value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(
        f"Unsupported value in engine input hash canonicalization: {type(value).__name__}"
    )


def compute_engine_input_hash(
    natal_chart: dict[str, Any],
    local_date: date,
    timezone: str,
    latitude: float,
    longitude: float,
    reference_version: str,
    ruleset_version: str,
    *,
    engine_mode: str = "v2",
    engine_version: str | None = None,
    snapshot_version: str | None = None,
    evidence_pack_version: str | None = None,
) -> str:
    """
    Computes a stable, canonical SHA-256 hash for EngineInput.

    This function is used by both the application service (to check for
    existing runs) and the engine (to stamp the output).
    """
    canonical = _canonicalize_value(
        {
            "natal": natal_chart,
            "local_date": local_date.isoformat(),
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
            "reference_version": reference_version,
            "ruleset_version": ruleset_version,
            "engine_mode": engine_mode,
            "engine_version": engine_version or "",
            "snapshot_version": snapshot_version or "",
            "evidence_pack_version": evidence_pack_version or "",
        }
    )
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
