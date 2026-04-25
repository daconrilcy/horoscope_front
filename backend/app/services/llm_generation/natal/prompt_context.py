"""Centralise les helpers de contexte prompt partages pour le domaine natal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.services.user_birth_profile_service import UserBirthProfileData

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult

SIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

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
}

ASPECT_NAMES_FR = {
    "conjunction": "conjonction",
    "opposition": "opposition",
    "trine": "trigone",
    "square": "carré",
    "sextile": "sextile",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

UNKNOWN_BIRTH_TIME_SENTINEL = "00:00"
UNKNOWN_LOCATION_SENTINELS = {"", "unknown", "non spécifié"}


def _longitude_to_sign(longitude: float) -> str:
    """Convertit une longitude en signe zodiacal."""
    index = int(longitude / 30) % 12
    return SIGNS[index]


def _format_longitude(longitude: float) -> str:
    """Formate une longitude en degrés et minutes."""
    sign_longitude = longitude % 30
    degrees = int(sign_longitude)
    minutes = int((sign_longitude - degrees) * 60)
    return f"{degrees}°{minutes:02d}'"


def _detect_degraded_mode(birth_profile: UserBirthProfileData) -> str | None:
    """Détecte le mode dégradé à partir du profil de naissance."""
    no_time = birth_profile.birth_time == UNKNOWN_BIRTH_TIME_SENTINEL
    no_location = (
        not birth_profile.birth_place or birth_profile.birth_place in UNKNOWN_LOCATION_SENTINELS
    )

    if no_time and no_location:
        return "no_location_no_time"
    if no_time:
        return "no_time"
    if no_location:
        return "no_location"
    return None


def build_natal_chart_summary(
    natal_result: "NatalResult",
    birth_place: str,
    birth_date: str,
    birth_time: str,
    degraded_mode: str | None = None,
) -> str:
    """Construit un résumé textuel du thème natal pour les prompts applicatifs."""
    lines: list[str] = []

    time_display = birth_time
    place_display = birth_place
    if degraded_mode == "no_time":
        time_display = "Non connue (interprétation des maisons approximative)"
    elif degraded_mode == "no_location":
        place_display = "Non connu (Ascendant non disponible)"
    elif degraded_mode == "no_location_no_time":
        time_display = "Non connue"
        place_display = "Non connu"

    lines.append(f"Thème natal né(e) le {birth_date} à {time_display} à {place_display}:")
    lines.append("")

    sun_position = next((p for p in natal_result.planet_positions if p.planet_code == "sun"), None)
    if sun_position:
        sign_name = SIGN_NAMES_FR.get(sun_position.sign_code, sun_position.sign_code)
        lon_fmt = _format_longitude(sun_position.longitude)
        lines.append(f"SOLEIL: {sign_name} à {lon_fmt} (Maison {sun_position.house_number})")

    moon_position = next(
        (p for p in natal_result.planet_positions if p.planet_code == "moon"), None
    )
    if moon_position:
        sign_name = SIGN_NAMES_FR.get(moon_position.sign_code, moon_position.sign_code)
        lon_fmt = _format_longitude(moon_position.longitude)
        lines.append(f"LUNE: {sign_name} à {lon_fmt} (Maison {moon_position.house_number})")

    house1 = next((h for h in natal_result.houses if h.number == 1), None)
    if house1:
        asc_sign = _longitude_to_sign(house1.cusp_longitude)
        asc_sign_name = SIGN_NAMES_FR.get(asc_sign, asc_sign)
        asc_lon_fmt = _format_longitude(house1.cusp_longitude)
        lines.append(f"ASCENDANT: {asc_sign_name} à {asc_lon_fmt}")

    lines.append("")
    lines.append("ASPECTS MAJEURS:")
    major_aspects = [a for a in natal_result.aspects if a.aspect_code in MAJOR_ASPECTS]
    for aspect in major_aspects[:6]:
        planet_a_name = PLANET_NAMES_FR.get(aspect.planet_a, aspect.planet_a)
        planet_b_name = PLANET_NAMES_FR.get(aspect.planet_b, aspect.planet_b)
        aspect_name = ASPECT_NAMES_FR.get(aspect.aspect_code, aspect.aspect_code)
        orb_rounded = round(aspect.orb, 1)
        lines.append(f"- {planet_a_name} {aspect_name} {planet_b_name} (orbe {orb_rounded}°)")

    lines.append("")
    lines.append("MAISONS ANGULAIRES:")
    angular_houses = {1: "Ascendant", 4: "Fond du Ciel", 7: "Descendant", 10: "Milieu du Ciel"}
    for house_num, house_label in angular_houses.items():
        house = next((h for h in natal_result.houses if h.number == house_num), None)
        if house:
            sign = _longitude_to_sign(house.cusp_longitude)
            sign_name = SIGN_NAMES_FR.get(sign, sign)
            lines.append(f"- Maison {house_num} ({house_label}): {sign_name}")

    return "\n".join(lines)


def build_chat_natal_hint(
    natal_result: "NatalResult",
    degraded_mode: str | None = None,
) -> str:
    """Construit un hint natal compact pour le contexte de chat."""
    parts: list[str] = []

    sun = next((p for p in natal_result.planet_positions if p.planet_code == "sun"), None)
    moon = next((p for p in natal_result.planet_positions if p.planet_code == "moon"), None)
    house1 = next((h for h in natal_result.houses if h.number == 1), None)

    if sun:
        sign_name = SIGN_NAMES_FR.get(sun.sign_code, sun.sign_code)
        parts.append(f"Soleil en {sign_name} (Maison {sun.house_number})")
    if moon:
        sign_name = SIGN_NAMES_FR.get(moon.sign_code, moon.sign_code)
        parts.append(f"Lune en {sign_name} (Maison {moon.house_number})")
    if house1 and degraded_mode not in {"no_location", "no_location_no_time"}:
        asc_sign = _longitude_to_sign(house1.cusp_longitude)
        asc_name = SIGN_NAMES_FR.get(asc_sign, asc_sign)
        parts.append(f"Ascendant {asc_name}")

    major = sorted(
        [a for a in natal_result.aspects if a.aspect_code in MAJOR_ASPECTS],
        key=lambda a: a.orb,
    )[:3]
    for aspect in major:
        planet_a_name = PLANET_NAMES_FR.get(aspect.planet_a, aspect.planet_a)
        planet_b_name = PLANET_NAMES_FR.get(aspect.planet_b, aspect.planet_b)
        aspect_name = ASPECT_NAMES_FR.get(aspect.aspect_code, aspect.aspect_code)
        parts.append(f"{planet_a_name} {aspect_name} {planet_b_name}")

    return " · ".join(parts)


__all__ = [
    "_detect_degraded_mode",
    "_format_longitude",
    "_longitude_to_sign",
    "build_chat_natal_hint",
    "build_natal_chart_summary",
]
