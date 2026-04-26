"""Registre statique des disclaimers applicatifs (Story 30-8 T5).

Les disclaimers ne sont plus générés par le LLM — ils sont injectés par l'API
selon le locale de la requête. Cela réduit les tokens LLM et stabilise le message légal.
"""

from __future__ import annotations

_DISCLAIMERS: dict[str, list[str]] = {
    "fr-FR": [
        (
            "Cette interprétation astrologique est un contenu de réflexion personnelle, "
            "non scientifique et non prédictif."
        ),
        (
            "Ce contenu ne constitue pas un conseil médical, psychologique, juridique, "
            "fiscal ou financier, et ne remplace pas un professionnel qualifié."
        ),
        (
            "Aucune garantie de résultat n'est fournie ; vos décisions relèvent de votre "
            "responsabilité et de votre libre arbitre."
        ),
    ],
    "fr-BE": [
        (
            "Cette interprétation astrologique est un contenu de réflexion personnelle, "
            "non scientifique et non prédictif."
        ),
        (
            "Ce contenu ne constitue pas un conseil médical, psychologique, juridique, "
            "fiscal ou financier, et ne remplace pas un professionnel qualifié."
        ),
        (
            "Aucune garantie de résultat n'est fournie ; vos décisions relèvent de votre "
            "responsabilité et de votre libre arbitre."
        ),
    ],
    "fr-CH": [
        (
            "Cette interprétation astrologique est un contenu de réflexion personnelle, "
            "non scientifique et non prédictif."
        ),
        (
            "Ce contenu ne constitue pas un conseil médical, psychologique, juridique, "
            "fiscal ou financier, et ne remplace pas un professionnel qualifié."
        ),
        (
            "Aucune garantie de résultat n'est fournie ; vos décisions relèvent de votre "
            "responsabilité et de votre libre arbitre."
        ),
    ],
    "es-ES": [
        (
            "Esta interpretación astrológica es un contenido de reflexión personal, "
            "no científico y no predictivo."
        ),
        (
            "Este contenido no constituye asesoramiento médico, psicológico, legal, fiscal "
            "o financiero y no sustituye a un profesional cualificado."
        ),
        (
            "No se ofrece ninguna garantía de resultados; tus decisiones son tu "
            "responsabilidad y dependen de tu libre albedrío."
        ),
    ],
    "en-US": [
        (
            "This astrological interpretation is for personal reflection only and is not "
            "scientific or predictive."
        ),
        (
            "It does not constitute medical, psychological, legal, tax, or financial "
            "advice and does not replace a licensed professional."
        ),
        "No outcome is guaranteed; your decisions remain your responsibility and free will.",
    ],
    "en-GB": [
        (
            "This astrological interpretation is for personal reflection only and is not "
            "scientific or predictive."
        ),
        (
            "It does not constitute medical, psychological, legal, tax, or financial "
            "advice and does not replace a licensed professional."
        ),
        "No outcome is guaranteed; your decisions remain your responsibility and free will.",
    ],
    "en-AU": [
        (
            "This astrological interpretation is for personal reflection only and is not "
            "scientific or predictive."
        ),
        (
            "It does not constitute medical, psychological, legal, tax, or financial "
            "advice and does not replace a licensed professional."
        ),
        "No outcome is guaranteed; your decisions remain your responsibility and free will.",
    ],
    "_default": [
        (
            "Cette interprétation astrologique est un contenu de réflexion personnelle, "
            "non scientifique et non prédictif."
        ),
        (
            "Ce contenu ne constitue pas un conseil médical, psychologique, juridique, "
            "fiscal ou financier, et ne remplace pas un professionnel qualifié."
        ),
        (
            "Aucune garantie de résultat n'est fournie ; vos décisions relèvent de votre "
            "responsabilité et de votre libre arbitre."
        ),
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
