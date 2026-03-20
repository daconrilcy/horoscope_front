from __future__ import annotations

from typing import Any

HOUSE_SIGNIFICATIONS: dict[int, dict[str, str]] = {
    1: {"label": "Maison I", "domain": "Identité et présence"},
    2: {"label": "Maison II", "domain": "Ressources et valeurs"},
    3: {"label": "Maison III", "domain": "Communication et mobilité"},
    4: {"label": "Maison IV", "domain": "Foyer et ancrage"},
    5: {"label": "Maison V", "domain": "Créativité et plaisirs"},
    6: {"label": "Maison VI", "domain": "Travail quotidien et santé"},
    7: {"label": "Maison VII", "domain": "Relations et associations"},
    8: {"label": "Maison VIII", "domain": "Transformations et profondeur"},
    9: {"label": "Maison IX", "domain": "Philosophie et horizons"},
    10: {"label": "Maison X", "domain": "Ambition et rôle public"},
    11: {"label": "Maison XI", "domain": "Collectif et réseaux"},
    12: {"label": "Maison XII", "domain": "Intériorité et ressources cachées"},
}

ASPECT_TONALITY: dict[str, str] = {
    "trine": "fluidité",
    "sextile": "fluidité",
    "square": "ajustement",
    "opposition": "ajustement",
    "conjunction": "intensification",
    "quincunx": "adaptation",
}

ASPECT_LABELS: dict[str, str] = {
    "trine": "Trigone",
    "sextile": "Sextile",
    "square": "Carré",
    "opposition": "Opposition",
    "conjunction": "Conjonction",
    "quincunx": "Quinconce",
}

EFFECT_LABELS: dict[str, str] = {
    "transit_to_natal": "Transit sur point natal",
    "lunar_sign_change": "Lune en nouveau signe",
    "exact_aspect": "Aspect exact",
    "station_direct": "Planète repart directe",
    "station_retrograde": "Planète entre en rétrograde",
    "aspect": "Aspect planétaire",
}

PLANET_NAMES_FR: dict[str, str] = {
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
    "north_node": "Nœud Nord (Rahu)",
    "south_node": "Nœud Sud (Ketu)",
}

SIGN_NAMES_FR: dict[str, str] = {
    "ari": "Bélier",
    "tau": "Taureau",
    "gem": "Gémeaux",
    "can": "Cancer",
    "leo": "Lion",
    "vir": "Vierge",
    "lib": "Balance",
    "sco": "Scorpion",
    "sag": "Sagittaire",
    "cap": "Capricorne",
    "aqu": "Verseau",
    "pis": "Poissons",
}

FIXED_STARS: dict[str, dict[str, Any]] = {
    "regulus": {"name_fr": "Régulus", "lon": 150.0},  # Lion 0°
    "algol": {"name_fr": "Algol", "lon": 56.0},  # Taureau 26°
    "spica": {"name_fr": "Spica", "lon": 203.0},  # Balance 23°
    "antares": {"name_fr": "Antarès", "lon": 249.0},  # Scorpion 9°
    "aldebaran": {"name_fr": "Aldébaran", "lon": 69.0},  # Gémeaux 9°
    "sirius": {"name_fr": "Sirius", "lon": 103.0},  # Cancer 13°
    "fomalhaut": {"name_fr": "Fomalhaut", "lon": 333.0},  # Poissons 3°
    "betelgeuse": {"name_fr": "Bételgeuse", "lon": 88.0},  # Gémeaux 28°
    "achernar": {"name_fr": "Achernar", "lon": 45.0},  # Bélier 15°
    "vega": {"name_fr": "Véga", "lon": 285.0},  # Capricorne 15°
}


def get_planet_name_fr(code: str) -> str:
    low_code = code.lower()
    if low_code.startswith("prog_"):
        base_name = get_planet_name_fr(low_code[5:])
        return f"{base_name} Progressé"
    return PLANET_NAMES_FR.get(low_code, code.capitalize())


def get_sign_name_fr(code: str) -> str:
    return SIGN_NAMES_FR.get(code.lower(), code.capitalize())


def get_fixed_star_name_fr(key: str) -> str:
    return FIXED_STARS.get(key.lower(), {}).get("name_fr", key.capitalize())


def get_aspect_tonality(aspect: str) -> str:
    return ASPECT_TONALITY.get(aspect.lower(), "nuance")


def get_aspect_label(aspect: str) -> str:
    return ASPECT_LABELS.get(aspect.lower(), aspect.capitalize())


def get_effect_label(event_type: str) -> str:
    return EFFECT_LABELS.get(event_type, "Influence astrologique")
