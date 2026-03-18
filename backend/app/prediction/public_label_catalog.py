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
