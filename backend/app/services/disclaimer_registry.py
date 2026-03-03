"""Registre statique des disclaimers applicatifs (Story 30-8 T5).

Les disclaimers ne sont plus générés par le LLM — ils sont injectés par l'API
selon le locale de la requête. Cela réduit les tokens LLM et stabilise le message légal.
"""

from __future__ import annotations

_DISCLAIMERS: dict[str, list[str]] = {
    "fr-FR": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
    "fr-BE": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
    "fr-CH": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
    "en-US": ["Astrology is a tool for personal reflection, not a certified predictive science."],
    "en-GB": ["Astrology is a tool for personal reflection, not a certified predictive science."],
    "en-AU": ["Astrology is a tool for personal reflection, not a certified predictive science."],
    "_default": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
}


def get_disclaimers(locale: str) -> list[str]:
    """Retourne les disclaimers statiques pour le locale donné.

    Utilise d'abord le locale exact, puis tente le fallback vers le code de langue
    de base (ex: 'fr' pour 'fr-CA') avant d'utiliser le '_default'.

    Args:
        locale: Code locale au format 'fr-FR', 'en-US', etc.

    Returns:
        Liste de chaînes disclaimer (garantie non vide).
    """
    # 1. Tentative avec le locale exact
    result = _DISCLAIMERS.get(locale)
    if result:
        return result

    # 2. Tentative avec le code de langue de base
    if "-" in locale:
        lang = locale.split("-")[0]
        # Recherche du premier locale commençant par ce code langue
        for key, value in _DISCLAIMERS.items():
            if key.startswith(f"{lang}-"):
                return value

    # 3. Fallback final
    return _DISCLAIMERS.get("_default") or []
