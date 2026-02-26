from __future__ import annotations

# Valeurs d'orbes par défaut (en degrés) pour les aspects majeurs
DEFAULT_ASPECT_ORBS: dict[str, float] = {
    "conjunction": 8.0,
    "sextile": 4.0,
    "square": 6.0,
    "trine": 6.0,
    "opposition": 8.0,
}

# Valeur d'orbe par défaut pour les autres aspects (mineurs, etc.)
DEFAULT_FALLBACK_ORB = 6.0

# Bornes de validation pour les orbes
MIN_ORB_DEG = 0.0
MAX_ORB_DEG = 15.0
