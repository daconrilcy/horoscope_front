"""Construction du JSON public utilisé pour restituer un thème natal."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from app.domain.astrology.zodiac import sign_from_longitude

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult
    from app.services.user_profile.birth_profile_service import UserBirthProfileData

MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

PLANET_NAMES_FR = {
    "sun": "Soleil",
    "moon": "Lune",
    "mercury": "Mercure",
    "venus": "Vénus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturne",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluton",
    "chiron": "Chiron",
    "lilith": "Lune Noire",
    "node": "Nœud Nord",
}

SIGN_NAMES_FR = {
    "aries": "Bélier",
    "taurus": "Taureau",
    "gemini": "Gémeaux",
    "cancer": "Cancer",
    "leo": "Lion",
    "virgo": "Vierge",
    "libra": "Balance",
    "scorpio": "Scorpion",
    "sagittarius": "Sagittaire",
    "capricorn": "Capricorne",
    "aquarius": "Verseau",
    "pisces": "Poissons",
}

ASPECT_NAMES_FR = {
    "conjunction": "conjonction",
    "opposition": "opposition",
    "trine": "trigone",
    "square": "carré",
    "sextile": "sextile",
}

# Regex for evidence IDs as per Story 29.1 AC4
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Z0-9_\.:-]{3,80}$")


def _longitude_to_sign(longitude: float) -> str:
    """Retourne le signe correspondant à une longitude zodiacale."""
    return sign_from_longitude(longitude)


def _longitude_in_sign(longitude: float) -> float:
    """Retourne la position en degrés à l'intérieur du signe."""
    return round(longitude % 30.0, 2)


def build_chart_json(
    natal_result: NatalResult,
    birth_profile: UserBirthProfileData,
    degraded_mode: str | None = None,
) -> dict[str, Any]:
    """
    Construit le payload public canonique du thème natal.

    Le payload regroupe les placements nécessaires aux restitutions publiques,
    dont les maisons, les planètes et les maîtres de maisons.
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
        planets.append(
            {
                "code": p.planet_code,
                "sign": p.sign_code,
                "longitude": round(p.longitude, 2),
                "longitude_in_sign": _longitude_in_sign(p.longitude),
                "house": None if is_no_time else p.house_number,
                "is_retrograde": p.is_retrograde,
                "speed": round(p.speed_longitude, 2) if p.speed_longitude is not None else None,
            }
        )

    # Houses
    houses = []
    if not is_no_time:
        for h in natal_result.houses:
            houses.append(
                {
                    "number": h.number,
                    "cusp_longitude": round(h.cusp_longitude, 2),
                    "sign": _longitude_to_sign(h.cusp_longitude),
                }
            )

    # Maîtres de maisons
    house_rulers = []
    if not is_no_time:
        for item in getattr(natal_result, "house_rulers", []):
            house_rulers.append(
                {
                    "house_number": item.house_number,
                    "cusp_sign": item.cusp_sign,
                    "ruler_planet": item.ruler_planet,
                    "ruler_planet_sign": item.ruler_planet_sign,
                    "ruler_planet_house": item.ruler_planet_house,
                }
            )

    # Aspects
    aspects = []
    for a in natal_result.aspects:
        # Filter for major aspects only as per Epic 29 requirements.
        # Minor aspects are currently calculated by the engine
        # but not supported by the JSON contract.
        if a.aspect_code in MAJOR_ASPECTS:
            orb_value = a.orb_used if a.orb_used is not None else a.orb
            aspects.append(
                {
                    "type": a.aspect_code,
                    "planet_a": a.planet_a,
                    "planet_b": a.planet_b,
                    "angle": round(a.angle, 2),
                    "orb": round(orb_value, 2) if orb_value is not None else None,
                    "applying": None,  # Unknown status
                }
            )

    # Angles
    angles = {
        "ASC": None,
        "MC": None,
        "DSC": None,
        "IC": None,
    }

    if not (is_no_time or is_no_location):
        house_dict = {h.number: h for h in natal_result.houses}
        map_angles = {"ASC": 1, "MC": 10, "DSC": 7, "IC": 4}
        for angle_key, house_num in map_angles.items():
            h = house_dict.get(house_num)
            if h:
                angles[angle_key] = {
                    "longitude": round(h.cusp_longitude, 2),
                    "sign": _longitude_to_sign(h.cusp_longitude),
                }

    return {
        "meta": meta,
        "planets": planets,
        "houses": houses,
        "house_rulers": house_rulers,
        "aspects": aspects,
        "angles": angles,
    }


def _get_evidence_priority(eid: str) -> int:
    """Détermine la priorité de tri des identifiants d'évidence."""
    # Priority 0: Luminaries and Angles
    if any(eid.startswith(p) for p in ["SUN_", "MOON_", "ASC_", "MC_", "IC_", "DSC_"]):
        return 0
    # Priority 1: Positions (Signs, Houses, Retrograde)
    planets = [
        "MERCURY_",
        "VENUS_",
        "MARS_",
        "JUPITER_",
        "SATURN_",
        "URANUS_",
        "NEPTUNE_",
        "PLUTO_",
        "CHIRON_",
        "LILITH_",
        "NODE_",
    ]
    if any(eid.startswith(p) for p in planets):
        return 1
    # Priority 2: Aspects
    if eid.startswith("ASPECT_"):
        return 2
    # Priority 3: Others (House cusps in signs, etc.)
    return 3


def build_evidence_catalog(chart_json: dict[str, Any]) -> list[str]:
    """Retourne la liste triée des identifiants d'évidence historiques."""
    enriched = build_enriched_evidence_catalog(chart_json)
    return sorted(list(enriched.keys()), key=lambda x: (_get_evidence_priority(x), x))


def build_enriched_evidence_catalog(chart_json: dict[str, Any]) -> dict[str, list[str]]:
    r"""
    Produit les libellés autorisés pour chaque identifiant d'évidence.

    Ce catalogue sert à valider les références entre le JSON technique et le
    texte généré par les restitutions natales.
    """
    # Map of ID -> list of labels
    catalog: dict[str, list[str]] = {}

    def add(eid: str, labels: list[str]):
        clean_id = eid.replace(" ", "_").upper()
        if EVIDENCE_ID_PATTERN.match(clean_id):
            if clean_id not in catalog:
                catalog[clean_id] = []
            for label in labels:
                if label and label not in catalog[clean_id]:
                    catalog[clean_id].append(label)

    # 1. Planets
    for p in chart_json.get("planets", []):
        p_code = p["code"]
        s_code = p["sign"]
        p_name = PLANET_NAMES_FR.get(p_code, p_code.capitalize())
        s_name = SIGN_NAMES_FR.get(s_code, s_code.capitalize())

        # PLANET_SIGN
        add(
            f"{p_code.upper()}_{s_code.upper()}",
            [f"{p_name} en {s_name}", f"{p_name} en signe du {s_name}"],
        )  # noqa: E501

        # PLANET_H{house}
        house = p.get("house")
        if house is not None:
            add(f"{p_code.upper()}_H{house}", [f"{p_name} en Maison {house}"])
            add(
                f"{p_code.upper()}_{s_code.upper()}_H{house}",
                [f"{p_name} en {s_name} en Maison {house}"],
            )

        if p.get("is_retrograde"):
            add(f"{p_code.upper()}_RETROGRADE", [f"{p_name} rétrograde"])

    # 2. Aspects
    for a in chart_json.get("aspects", []):
        p1 = a["planet_a"]
        p2 = a["planet_b"]
        asp_type = a["type"]
        p1_name = PLANET_NAMES_FR.get(p1, p1.capitalize())
        p2_name = PLANET_NAMES_FR.get(p2, p2.capitalize())
        asp_name = ASPECT_NAMES_FR.get(asp_type, asp_type)

        pair = sorted([p1.upper(), p2.upper()])
        base_id = f"ASPECT_{pair[0]}_{pair[1]}_{asp_type.upper()}"

        labels = [
            f"{asp_name} entre {p1_name} et {p2_name}",
            f"{p1_name} {asp_name} {p2_name}",
        ]
        add(base_id, labels)

        orb = a.get("orb")
        if orb is not None:
            orb_int = int(round(orb))
            add(f"{base_id}_ORB{orb_int}", labels)

    # 3. Angles
    angles = chart_json.get("angles", {})
    angle_names = {
        "ASC": "Ascendant",
        "MC": "Milieu du Ciel",
        "DSC": "Descendant",
        "IC": "Fond du Ciel",
    }  # noqa: E501
    if angles:
        for angle_key, data in angles.items():
            if data and data.get("sign"):
                s_code = data["sign"]
                s_name = SIGN_NAMES_FR.get(s_code, s_code.capitalize())
                a_name = angle_names.get(angle_key, angle_key)
                add(f"{angle_key}_{s_code.upper()}", [f"{a_name} en {s_name}"])

    # 4. Houses
    for h in chart_json.get("houses", []):
        num = h["number"]
        s_code = h["sign"]
        s_name = SIGN_NAMES_FR.get(s_code, s_code.capitalize())
        add(f"HOUSE_{num}_IN_{s_code.upper()}", [f"Maison {num} en {s_name}"])

    # 5. House rulers
    for ruler in chart_json.get("house_rulers", []):
        house_num = ruler["house_number"]
        planet_code = ruler["ruler_planet"]
        planet_name = PLANET_NAMES_FR.get(planet_code, planet_code.capitalize())
        base_labels = [f"Maître de Maison {house_num} : {planet_name}"]
        add(f"HOUSE_{house_num}_RULER_{planet_code.upper()}", base_labels)

        ruler_house = ruler.get("ruler_planet_house")
        if ruler_house is not None:
            add(
                f"HOUSE_{house_num}_RULER_{planet_code.upper()}_H{ruler_house}",
                [*base_labels, f"Maître de Maison {house_num} en Maison {ruler_house}"],
            )

        ruler_sign = ruler.get("ruler_planet_sign")
        if ruler_sign:
            sign_name = SIGN_NAMES_FR.get(ruler_sign, str(ruler_sign).capitalize())
            add(
                f"HOUSE_{house_num}_RULER_{planet_code.upper()}_{str(ruler_sign).upper()}",
                [*base_labels, f"Maître de Maison {house_num} en {sign_name}"],
            )

    return catalog
