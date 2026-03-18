from __future__ import annotations

# CLIMATE_LABELS: dict[(tone, intensity_bucket), str]
# intensity_bucket : "low" (0–3.9), "medium" (4.0–6.9), "high" (7.0–10.0)

CLIMATE_LABELS: dict[tuple[str, str], str] = {
    ("positive", "high"): "Journée de forte progression",
    ("positive", "medium"): "Élan favorable",
    ("positive", "low"): "Douceur portante",
    ("neutral", "high"): "Climat dynamique et équilibré",
    ("neutral", "medium"): "Climat stable et fluide",
    ("neutral", "low"): "Journée calme et sereine",
    ("mixed", "high"): "Journée intense et contrastée",
    ("mixed", "medium"): "Journée en relief",
    ("mixed", "low"): "Nuances légères et variées",
    ("negative", "high"): "Journée exigeante",
    ("negative", "medium"): "Climat de vigilance",
    ("negative", "low"): "Petite réserve passagère",
}


def get_intensity_bucket(intensity: float) -> str:
    if intensity >= 7.0:
        return "high"
    if intensity >= 4.0:
        return "medium"
    return "low"


def get_climate_label(tone: str, intensity: float) -> str:
    bucket = get_intensity_bucket(intensity)
    return CLIMATE_LABELS.get((tone, bucket), "Journée en cours")


REGIME_LABELS: dict[str, list[str]] = {
    "progression": ["Moment porteur", "Cap sur l'action", "Élan favorable"],
    "fluidité": ["Rythme fluide", "Douceur active", "Progression régulière"],
    "prudence": ["Fenêtre sensible", "Ralentir le rythme", "Gérer avec soin"],
    "pivot": ["Virage de la journée", "Moment charnière", "Tournant"],
    "récupération": ["Phase de repos", "Recharge tranquille"],
    "retombée": ["Retour au calme", "L'élan s'apaise"],
    "mise_en_route": ["Démarrage progressif", "Mise en mouvement"],
    "recentrage": ["Temps de bilan", "Ralenti créatif"],
}

ACTION_HINTS: dict[str, str] = {
    "progression": "Avancez sur vos priorités",
    "fluidité": "Maintenez le cap",
    "prudence": "Évitez les décisions engageantes",
    "pivot": "Observez avant d'agir",
    "recentrage": "Faites le point",
    "retombée": "Laissez poser",
    "récupération": "Reposez-vous",
    "mise_en_route": "Lancez doucement",
}


def get_regime_label(regime: str, top_domains: list[str]) -> str:
    pool = REGIME_LABELS.get(regime, ["Moment de la journée"])
    # Simple selection logic: index based on first domain if available
    idx = (ord(top_domains[0][0]) % len(pool)) if top_domains else 0
    return pool[idx % len(pool)]


def get_action_hint(regime: str) -> str:
    return ACTION_HINTS.get(regime, "Suivez votre rythme")


TITLE_TEMPLATES: dict[tuple[str, str], str] = {
    ("emergence", "pro_ambition"): "Montée en puissance côté pro",
    ("emergence", "relations_echanges"): "Ouverture relationnelle",
    ("emergence", "energie_bienetre"): "Regain d'énergie",
    ("emergence", "argent_ressources"): "Opportunité matérielle",
    ("emergence", "vie_personnelle"): "Élan créatif et perso",
    ("recomposition", "pro_ambition"): "Virage stratégique pro",
    ("recomposition", "relations_echanges"): "Nouvelle donne relationnelle",
    ("recomposition", "energie_bienetre"): "Changement de rythme intérieur",
    ("attenuation", "pro_ambition"): "L'exigence pro s'apaise",
    ("attenuation", "relations_echanges"): "Retour au calme relationnel",
    ("attenuation", "energie_bienetre"): "Détente et récupération",
}

FALLBACK_TITLES: dict[str, str] = {
    "emergence": "Montée en puissance",
    "recomposition": "Virage de la journée",
    "attenuation": "Retour au calme",
}

DO_AVOID_CATALOG: dict[tuple[str, str | None], tuple[str, str]] = {
    ("emergence", "pro_ambition"): ("Avancez, décidez, lancez", "Reporter, attendre"),
    ("emergence", "relations_echanges"): ("Échanger, sortir, proposer", "S'isoler, ruminer"),
    ("recomposition", "relations_echanges"): ("Écouter, dialoguer", "Imposer, forcer"),
    ("attenuation", None): ("Clôturer, ranger, ralentir", "Forcer une décision"),
    ("recomposition", None): ("Observer, s'adapter", "S'obstiner"),
    ("emergence", None): ("Saisir l'élan", "Douter"),
}


def get_turning_point_title(change_type: str, domain: str | None) -> str:
    if domain:
        title = TITLE_TEMPLATES.get((change_type, domain))
        if title:
            return title
    return FALLBACK_TITLES.get(change_type, "Moment de bascule")


def get_do_avoid(change_type: str, domain: str | None) -> tuple[str, str]:
    # Try specific match
    if domain:
        res = DO_AVOID_CATALOG.get((change_type, domain))
        if res:
            return res

    # Try change_type match with None domain
    res = DO_AVOID_CATALOG.get((change_type, None))
    if res:
        return res

    # absolute fallback
    return ("Rester à l'écoute", "Agir avec précipitation")


WINDOW_ACTIONS: dict[str, list[str]] = {
    "pro_ambition": [
        "Prendre des décisions importantes",
        "Négocier ou conclure",
        "Avancer sur un projet bloqué",
    ],
    "relations_echanges": [
        "Avoir une conversation difficile",
        "Proposer, inviter, connecter",
        "Résoudre un conflit",
    ],
    "energie_bienetre": [
        "Faire du sport",
        "S'aérer, sortir",
        "Commencer une nouvelle habitude",
    ],
    "argent_ressources": [
        "Signer, valider, investir",
        "Réviser un budget",
        "Contacter un prestataire",
    ],
    "vie_personnelle": [
        "Lancer un projet créatif",
        "Passer du temps en famille",
        "Se faire plaisir",
    ],
}

WHY_TEMPLATES: dict[str, str] = {
    "pro_ambition": "Les conditions pro sont au maximum de leur dynamique.",
    "relations_echanges": "Les échanges sont fluides et réceptifs.",
    "energie_bienetre": "Votre vitalité est à son pic.",
    "argent_ressources": "Les décisions financières bénéficient d'un soutien fort.",
    "vie_personnelle": "L'énergie créative et personnelle est au sommet.",
}


def get_best_window_why(domain: str | None) -> str:
    if domain:
        why = WHY_TEMPLATES.get(domain)
        if why:
            return why
    return "Les conditions astrologiques convergent favorablement."


def get_recommended_actions(domain: str | None) -> list[str]:
    if domain:
        actions = WINDOW_ACTIONS.get(domain)
        if actions:
            return actions[:3]
    return ["Suivez votre intuition", "Restez à l'écoute de votre rythme"]
