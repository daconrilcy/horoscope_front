from __future__ import annotations

import logging
from typing import Any

from app.domain.astrology.natal_calculation import sign_from_longitude
from app.prompts.common_context import PromptCommonContext

logger = logging.getLogger(__name__)

STYLE_INSTRUCTIONS = {
    "standard": "Astrologie occidentale classique, ton positif et accessible.",
    "vedique": "Références védiques : nakshatra, maisons védiques, dharma, karma.",
    "humaniste": "Approche humaniste : archétypes jungiens, croissance personnelle.",
    "karmique": "Insiste sur les leçons de vie, les nœuds lunaires, les cycles karmiques.",
    "psychologique": "Vocabulaire psychologique moderne : patterns, intégration.",
}


class AstrologerPromptBuilder:
    """
    Builds the detailed prompt for the LLM narrator (Story 60.16).
    Integrates natal data, daily events, and user style preferences.
    """

    def build(
        self,
        common_context: PromptCommonContext,
        time_windows: list[dict[str, Any]],
        events: list[Any],
        astrologer_profile_key: str = "standard",
        lang: str = "fr",
    ) -> str:
        # 1. Natal Foundation
        natal_section = self._build_natal_section(common_context)

        # 2. Daily Context
        date_str = common_context.today_date

        # 3. Astro Events Summary
        events_str = self._format_events(events)

        # 4. Time Windows & Regimes
        windows_str = self._format_windows(time_windows)

        # 5. Style Instructions
        style_instr = STYLE_INSTRUCTIONS.get(astrologer_profile_key, STYLE_INSTRUCTIONS["standard"])
        if lang != "fr":
            # Basic translation for non-fr (could be improved)
            if astrologer_profile_key == "vedique":
                style_instr = "Use Vedic references: nakshatra, vedic houses, dharma, karma."
            elif astrologer_profile_key == "humaniste":
                style_instr = (
                    "Adopt a humanistic approach: Jungian archetypes, personal growth, symbolism."
                )
            elif astrologer_profile_key == "karmique":
                style_instr = "Emphasize life lessons, lunar nodes, karmic cycles."
            elif astrologer_profile_key == "psychologique":
                style_instr = (
                    "Use modern psychological vocabulary: patterns, integration, behaviors."
                )
            else:
                style_instr = (
                    "Use classic western astrology vocabulary, positive and accessible tone."
                )

        prompt = f"""
CONTEXTE ASTROLOGIQUE DU JOUR ({date_str})

PROFIL NATAL DE L'UTILISATEUR :
{natal_section}

ÉVÉNEMENTS CÉLESTES MAJEURS DU JOUR :
{events_str}

DÉROULÉ DE LA JOURNÉE (CRÉNEAUX HORAIRES) :
{windows_str}

CONSIGNES DE RÉDACTION :
- Style : {style_instr}
- Ton : {common_context.astrologer_profile.get("tonality", "bienveillant")}
- Langue : {"Français" if lang == "fr" else "English"}
- Format attendu : JSON strict.
- daily_synthesis : Une synthèse globale de la journée (2 phrases).
- astro_events_intro : Une phrase courte pour introduire les événements du ciel.
- time_window_narratives : Un objet avec les clés "nuit", "matin", "apres_midi", "soiree".
  Chaque valeur est une phrase décrivant l'ambiance du créneau.
- turning_point_narratives : Une liste de phrases (une par turning point détecté).

Génère un contenu inspirant, fluide et personnalisé.
"""
        return prompt.strip()

    def _build_natal_section(self, ctx: PromptCommonContext) -> str:
        if ctx.natal_interpretation:
            return ctx.natal_interpretation[:1000]  # Limit size

        if not ctx.natal_data:
            return "Profil natal non disponible."

        # Fallback raw data formatting
        pos = ctx.natal_data.get("planet_positions", [])
        planets = []
        for p in pos:
            code = p.get("planet_code")
            sign = p.get("sign_code")
            if code in ["SO", "LU"]:
                planets.append(f"{code} en {sign}")

        houses = ctx.natal_data.get("houses", [])
        asc = "Inconnu"
        if houses:
            asc = sign_from_longitude(houses[0].get("cusp_longitude", 0))

        return (
            f"Soleil/Lune : {', '.join(planets)}. Ascendant : {asc}. "
            f"Précision : {ctx.precision_level}."
        )

    def _format_events(self, events: list[Any]) -> str:
        if not events:
            return "Aucun événement majeur particulier."

        lines = []
        for e in events[:10]:
            body = getattr(e, "body", "?")
            target = getattr(e, "target", "")
            aspect = getattr(e, "aspect", "")
            ev_type = getattr(e, "event_type", "")
            lines.append(f"- {ev_type}: {body} {aspect} {target}")

        return "\n".join(lines)

    def _format_windows(self, windows: list[dict[str, Any]]) -> str:
        lines = []
        for w in windows:
            key = w.get("period_key", "?")
            regime = w.get("regime", "?")
            label = w.get("label", "")
            domains = ", ".join(w.get("top_domains", []))
            lines.append(
                f"[{key}] {w.get('time_range')}: {label} (Régime: {regime}). Domaines: {domains}"
            )
        return "\n".join(lines)
