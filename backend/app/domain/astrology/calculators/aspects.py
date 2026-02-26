from itertools import combinations

from app.core.constants import DEFAULT_FALLBACK_ORB, LUMINARIES


def _angular_distance(angle_a: float, angle_b: float) -> float:
    diff = abs(angle_a - angle_b) % 360.0
    return min(diff, 360.0 - diff)


def _normalize_pair_key(planet_a: str, planet_b: str) -> str:
    left, right = sorted((planet_a.strip().lower(), planet_b.strip().lower()))
    return f"{left}-{right}"


def _normalize_pair_overrides(value: object) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, float] = {}
    for raw_key, raw_value in value.items():
        key = str(raw_key).strip().lower()
        parts = [part.strip() for part in key.split("-", maxsplit=1)]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            continue
        try:
            parsed_value = float(raw_value)
        except (TypeError, ValueError):
            continue
        normalized[_normalize_pair_key(parts[0], parts[1])] = parsed_value
    return normalized


def _normalize_aspect_definition(
    definition: tuple[str, float] | dict[str, object],
    fallback_orb: float,
) -> dict[str, object]:
    if isinstance(definition, tuple):
        aspect_code, angle = definition
        return {
            "aspect_code": str(aspect_code),
            "angle": float(angle),
            "default_orb": float(fallback_orb),
            "orb_luminaries": None,
            "orb_pair_overrides": {},
        }

    aspect_code = str(definition.get("code", "")).strip()
    angle = float(definition.get("angle", 0.0))
    default_orb = float(definition.get("default_orb_deg", fallback_orb))
    orb_luminaries_raw = definition.get("orb_luminaries")
    orb_luminaries = float(orb_luminaries_raw) if orb_luminaries_raw is not None else None
    
    # Prioritize 'orb_pair_overrides' then 'orb_pairs' then 'orb_overrides'
    pair_overrides_raw = (
        definition.get("orb_pair_overrides")
        or definition.get("orb_pairs")
        or definition.get("orb_overrides")
    )
    pair_overrides = _normalize_pair_overrides(pair_overrides_raw)

    return {
        "aspect_code": aspect_code,
        "angle": angle,
        "default_orb": default_orb,
        "orb_luminaries": orb_luminaries,
        "orb_pair_overrides": pair_overrides,
    }


def calculate_major_aspects(
    positions: list[dict[str, object]],
    aspect_definitions: list[tuple[str, float] | dict[str, object]],
    max_orb: float = DEFAULT_FALLBACK_ORB,
) -> list[dict[str, object]]:
    """Calculate aspects between planet positions using hierarchical orb resolution.
    
    Resolution Priority:
    1. Pair-specific override (e.g. 'sun-mercury')
    2. Luminary override (if either planet is Sun or Moon)
    3. Default orb for the aspect
    """
    normalized_definitions = [
        _normalize_aspect_definition(definition, max_orb) for definition in aspect_definitions
    ]
    
    # Pre-normalize planet data to avoid repeated work in the hot loop
    prepared_positions = []
    for pos in positions:
        code = str(pos["planet_code"]).strip().lower()
        prepared_positions.append({
            "planet_code": code,
            "longitude": float(pos["longitude"]),
            "is_luminary": code in LUMINARIES
        })

    aspects: list[dict[str, object]] = []
    for left, right in combinations(prepared_positions, 2):
        planet_a = left["planet_code"]
        planet_b = right["planet_code"]
        is_any_luminary = left["is_luminary"] or right["is_luminary"]
        pair_key = f"{planet_a}-{planet_b}" if planet_a < planet_b else f"{planet_b}-{planet_a}"
        
        distance = _angular_distance(left["longitude"], right["longitude"])
        
        for aspect_def in normalized_definitions:
            angle = float(aspect_def["angle"])
            orb = abs(distance - angle)
            
            # Resolve orb_used
            overrides = aspect_def["orb_pair_overrides"]
            if pair_key in overrides:
                orb_used = overrides[pair_key]
            elif is_any_luminary and aspect_def["orb_luminaries"] is not None:
                orb_used = aspect_def["orb_luminaries"]
            else:
                orb_used = aspect_def["default_orb"]
                
            if orb <= orb_used:
                aspects.append(
                    {
                        "aspect_code": aspect_def["aspect_code"],
                        "planet_a": planet_a,
                        "planet_b": planet_b,
                        "angle": round(angle, 6),
                        "orb": round(orb, 6),
                        "orb_used": round(orb_used, 6),
                    }
                )
    
    aspects.sort(
        key=lambda item: (
            str(item["aspect_code"]),
            str(item["planet_a"]),
            str(item["planet_b"]),
        )
    )
    return aspects
