from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult
    from app.services.user_birth_profile_service import UserBirthProfileData

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]
MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

# Regex for evidence IDs as per Story 29.1 AC4
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Z0-9_\.:-]{3,60}$")

def _longitude_to_sign(longitude: float) -> str:
    """Returns the sign name for a given longitude."""
    index = int((longitude % 360.0) // 30.0) % 12
    return SIGNS[index]

def _longitude_in_sign(longitude: float) -> float:
    """Returns the longitude within the sign (0-30)."""
    return round(longitude % 30.0, 2)

def build_chart_json(
    natal_result: NatalResult,
    birth_profile: UserBirthProfileData,
    degraded_mode: str | None = None,
) -> dict[str, Any]:
    """
    Builds the canonical chart_json payload for LLMGateway.
    
    Args:
        natal_result: The calculated natal result.
        birth_profile: The user's birth profile data.
        degraded_mode: Optional string indicating degraded modes:
                       "no_time", "no_location", "no_location_no_time".
                       If None, it is derived from birth_profile.
        
    Returns:
        A dictionary with keys: meta, planets, houses, aspects, angles.
    """
    # Auto-derive degraded_mode if not provided
    if degraded_mode is None:
        no_time = birth_profile.birth_time is None
        no_location = birth_profile.birth_lat is None or birth_profile.birth_lon is None
        if no_time and no_location:
            degraded_mode = "no_location_no_time"
        elif no_time:
            degraded_mode = "no_time"
        elif no_location:
            degraded_mode = "no_location"

    is_no_time = degraded_mode in {"no_time", "no_location_no_time"}
    is_no_location = degraded_mode in {"no_location", "no_location_no_time"}

    # Meta information
    birth_timezone = birth_profile.birth_timezone
    if hasattr(natal_result, "prepared_input"):
        birth_timezone = natal_result.prepared_input.birth_timezone

    zodiac = str(natal_result.zodiac)
    if hasattr(natal_result.zodiac, "value"):
        zodiac = str(natal_result.zodiac.value)

    house_system = str(natal_result.house_system)
    if hasattr(natal_result.house_system, "value"):
        house_system = str(natal_result.house_system.value)

    meta = {
        "birth_date": birth_profile.birth_date,
        "birth_time": None if is_no_time else birth_profile.birth_time,
        "birth_place": None if is_no_location else birth_profile.birth_place,
        "birth_timezone": birth_timezone,
        "degraded_mode": degraded_mode,
        "engine": natal_result.engine,
        "zodiac": zodiac,
        "house_system": house_system,
        "reference_version": natal_result.reference_version,
        "ruleset_version": natal_result.ruleset_version,
        "chart_json_version": "1",
        "aspects_applying_available": False,
    }

    # Planets
    planets = []
    for p in natal_result.planet_positions:
        planets.append({
            "code": p.planet_code,
            "sign": p.sign_code,
            "longitude": round(p.longitude, 2),
            "longitude_in_sign": _longitude_in_sign(p.longitude),
            "house": None if is_no_time else p.house_number,
            "is_retrograde": p.is_retrograde,
            "speed": round(p.speed_longitude, 2),
        })

    # Houses
    houses = []
    if not is_no_time:
        for h in natal_result.houses:
            houses.append({
                "number": h.number,
                "cusp_longitude": round(h.cusp_longitude, 2),
                "sign": _longitude_to_sign(h.cusp_longitude),
            })

    # Aspects
    aspects = []
    for a in natal_result.aspects:
        # Filter for major aspects only as per Epic 29 requirements.
        # Minor aspects are currently calculated by the engine but not supported by the JSON contract.
        if a.aspect_code in MAJOR_ASPECTS:
            aspects.append({
                "type": a.aspect_code,
                "planet_a": a.planet_a,
                "planet_b": a.planet_b,
                "angle": round(a.angle, 2),
                "orb": round(a.orb_used, 2),
                "applying": None, # Unknown status
            })

    # Angles
    angles = {
        "ASC": None,
        "MC": None,
        "DSC": None,
        "IC": None,
    }

    if not (is_no_time or is_no_location):
        house_dict = {h.number: h for h in natal_result.houses}
        map_angles = {
            "ASC": 1,
            "MC": 10,
            "DSC": 7,
            "IC": 4
        }
        for angle_key, house_num in map_angles.items():
            h = house_dict.get(house_num)
            if h:
                angles[angle_key] = {
                    "longitude": round(h.cusp_longitude, 2),
                    "sign": _longitude_to_sign(h.cusp_longitude)
                }

    return {
        "meta": meta,
        "planets": planets,
        "houses": houses,
        "aspects": aspects,
        "angles": angles,
    }

def _get_evidence_priority(eid: str) -> int:
    """Helper to determine sorting priority for evidence IDs."""
    # Priority 0: Luminaries and Angles
    if any(eid.startswith(p) for p in ["SUN_", "MOON_", "ASC_", "MC_", "IC_", "DSC_"]):
        return 0
    # Priority 1: Positions (Signs, Houses, Retrograde)
    planets = [
        "MERCURY_", "VENUS_", "MARS_", "JUPITER_", "SATURN_", "URANUS_",
        "NEPTUNE_", "PLUTO_", "CHIRON_", "LILITH_", "NODE_"
    ]
    if any(eid.startswith(p) for p in planets):
        return 1
    # Priority 2: Aspects
    if eid.startswith("ASPECT_"):
        return 2
    # Priority 3: Others (House cusps in signs, etc.)
    return 3

def build_evidence_catalog(chart_json: dict[str, Any]) -> list[str]:
    r"""
    Produces a list of evidence identifiers in UPPER_SNAKE_CASE.
    
    Evidence IDs follow the pattern: ^[A-Z0-9_\.:-]{3,60}$
    """
    evidence = []

    # Planets
    for p in chart_json.get("planets", []):
        planet = str(p["code"]).upper()
        sign = str(p["sign"]).upper()
        # PLANET_SIGN
        evidence.append(f"{planet}_{sign}")
        
        house = p.get("house")
        if house is not None:
            # PLANET_H{house}
            evidence.append(f"{planet}_H{house}")
            # PLANET_SIGN_H{house}
            evidence.append(f"{planet}_{sign}_H{house}")
            
        if p.get("is_retrograde"):
            evidence.append(f"{planet}_RETROGRADE")

    # Aspects
    for a in chart_json.get("aspects", []):
        p1 = str(a["planet_a"]).upper()
        p2 = str(a["planet_b"]).upper()
        aspect_type = str(a["type"]).upper()
        
        # ASPECT_PA_PB_TYPE (sorted PA, PB for stability)
        pair = sorted([p1, p2])
        base_id = f"ASPECT_{pair[0]}_{pair[1]}_{aspect_type}"
        evidence.append(base_id)
        
        # ASPECT_PA_PB_TYPE_ORB{int_orb}
        orb = a.get("orb")
        if orb is not None:
            orb_int = int(round(orb))
            evidence.append(f"{base_id}_ORB{orb_int}")

    # Angles
    angles = chart_json.get("angles", {})
    if angles:
        for angle_key, data in angles.items():
            if data and data.get("sign"):
                sign = str(data["sign"]).upper()
                evidence.append(f"{angle_key}_{sign}")

    # House cusps in signs
    for h in chart_json.get("houses", []):
        num = h["number"]
        sign = h["sign"].upper()
        evidence.append(f"HOUSE_{num}_IN_{sign}")

    # Clean and validate against pattern
    # Use list(set(...)) to deduplicate
    unique_evidence = set()
    for eid in evidence:
        # Basic cleanup: uppercase, replace spaces/hyphens with underscore if needed
        # but the logic above already uses UPPER and underscores.
        clean_id = eid.replace(" ", "_").upper()
        if EVIDENCE_ID_PATTERN.match(clean_id):
            unique_evidence.add(clean_id)
            
    # Sort by priority then alpha
    sorted_evidence = sorted(
        list(unique_evidence), 
        key=lambda x: (_get_evidence_priority(x), x)
    )

    if len(sorted_evidence) > 40:
        # Truncate keeping the most important ones (priority based)
        return sorted_evidence[:40]
        
    return sorted_evidence
