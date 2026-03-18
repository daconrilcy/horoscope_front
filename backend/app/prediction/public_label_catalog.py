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
