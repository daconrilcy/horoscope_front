from __future__ import annotations

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
}


def get_planet_name_fr(code: str) -> str:
    return PLANET_NAMES_FR.get(code.lower(), code.capitalize())


def get_aspect_tonality(aspect: str) -> str:
    return ASPECT_TONALITY.get(aspect.lower(), "nuance")


def get_aspect_label(aspect: str) -> str:
    return ASPECT_LABELS.get(aspect.lower(), aspect.capitalize())


def get_effect_label(event_type: str) -> str:
    return EFFECT_LABELS.get(event_type, "Influence astrologique")
