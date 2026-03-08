# backend/app/prediction/category_codes.py
from typing import Iterable

# Map legacy/display French codes to canonical English codes
_FRENCH_TO_CANONICAL = {
    "amour": "love",
    "travail": "work",
    "sante": "health",
    "argent": "money",
    "vitalite": "energy",
    "mental": "mood",
}

def normalize_category_code(code: str) -> str:
    """Normalizes a category code to its canonical English version."""
    if not code:
        return "general"
    
    lowered = code.lower().strip()
    return _FRENCH_TO_CANONICAL.get(lowered, lowered)

def normalize_category_codes(codes: Iterable[str]) -> list[str]:
    """Normalizes a list of category codes."""
    return [normalize_category_code(c) for c in codes]
