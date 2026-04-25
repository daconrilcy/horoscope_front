"""Construit le bloc d'ouverture de chat pour les premiers échanges utilisateur."""

from __future__ import annotations


def _looks_like_unclear_opening_message(message: str) -> bool:
    """Détecte un premier message trop ambigu pour lancer une réponse guidée."""
    normalized = "".join(ch for ch in message.strip().lower() if ch.isalpha())
    if not normalized:
        return True
    if len(normalized) <= 4:
        return True
    if len(set(normalized)) <= 2 and len(normalized) <= 6:
        return True
    vowels = sum(1 for ch in normalized if ch in "aeiouyàâäéèêëîïôöùûü")
    if len(normalized) <= 6 and vowels == 0:
        return True
    return False


def build_opening_chat_user_data_block(
    last_user_msg: str,
    context: dict[str, str | None],
) -> str:
    """Construit le payload conversationnel minimal pour un premier tour de chat."""
    persona_name = context.get("persona_name") or "Astrologue"
    persona_tone = context.get("persona_tone") or "direct"
    persona_style = context.get("persona_style_markers") or "non précisé"
    today_date = context.get("today_date") or "aujourd'hui"
    user_profile = context.get("user_profile_brief") or "Profil utilisateur non disponible"
    unclear_opening = _looks_like_unclear_opening_message(last_user_msg)

    return (
        f"Premier message utilisateur : {last_user_msg}\n\n"
        "Contexte initial minimal pour ce premier échange seulement:\n"
        f"- Astrologue: {persona_name}\n"
        f"- Ton astrologue: {persona_tone}\n"
        f"- Style astrologue: {persona_style}\n"
        f"- Date du jour: {today_date}\n"
        f"- Profil simple utilisateur: {user_profile}\n\n"
        "Consigne de réponse pour ce premier échange:\n"
        "- Réponds d'abord naturellement à la demande immédiate de l'utilisateur.\n"
        "- N'ouvre pas spontanément une lecture complète du thème natal "
        "ni de l'horoscope du jour.\n"
        "- Si ces éléments peuvent aider, propose ensuite simplement de regarder le thème natal, "
        "l'horoscope du jour ou les transits du moment, selon la demande.\n"
        + (
            "- Le premier message semble vague ou incompréhensible. "
            "Ne réponds pas avec une formule robotique ni une liste d'options. "
            "Dis simplement que tu n'as pas bien saisi et invite l'utilisateur "
            "à reformuler naturellement en une phrase.\n"
            if unclear_opening
            else "- Évite les salutations automatiques du type "
            '"Bonjour, comment puis-je vous aider ?" si elles n\'apportent rien.\n'
        )
        + "- Reste conversationnel, bref et humain."
    )
