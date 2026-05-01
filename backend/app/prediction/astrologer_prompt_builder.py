"""Construit le contexte quotidien transmis au prompt gouverné d'horoscope."""

from __future__ import annotations

import logging
from typing import Any

from app.domain.astrology.natal_calculation import sign_from_longitude
from app.domain.llm.prompting.context import PromptCommonContext, QualifiedContext
from app.prediction.public_astro_vocabulary import get_planet_name_fr, get_sign_name_fr

logger = logging.getLogger(__name__)

PLANET_CODE_LABELS = {
    "SO": "Soleil",
    "LU": "Lune",
    "ME": "Mercure",
    "VE": "Vénus",
    "MA": "Mars",
    "JU": "Jupiter",
    "SA": "Saturne",
    "UR": "Uranus",
    "NE": "Neptune",
    "PL": "Pluton",
}

SIGN_LABELS_FR = {
    "ari": "Bélier",
    "aries": "Bélier",
    "tau": "Taureau",
    "taurus": "Taureau",
    "gem": "Gémeaux",
    "gemini": "Gémeaux",
    "can": "Cancer",
    "cancer": "Cancer",
    "leo": "Lion",
    "vir": "Vierge",
    "virgo": "Vierge",
    "lib": "Balance",
    "libra": "Balance",
    "sco": "Scorpion",
    "scorpio": "Scorpion",
    "sag": "Sagittaire",
    "sagittarius": "Sagittaire",
    "cap": "Capricorne",
    "capricorn": "Capricorne",
    "aqu": "Verseau",
    "aquarius": "Verseau",
    "pis": "Poissons",
    "pisces": "Poissons",
}


class AstrologerPromptBuilder:
    """Assemble uniquement les faits astrologiques quotidiens pour la narration."""

    def build(
        self,
        common_context: PromptCommonContext | QualifiedContext,
        time_windows: list[dict[str, Any]],
        astrologer_profile_key: str = "standard",
        lang: str = "fr",
        astro_daily_events: dict[str, Any] | None = None,
        day_climate: dict[str, Any] | None = None,
        best_window: dict[str, Any] | None = None,
        turning_point: dict[str, Any] | None = None,
        domain_ranking: list[dict[str, Any]] | None = None,
        variant_code: str | None = None,
    ) -> str:
        payload = self._resolve_payload(common_context)
        natal_section = self._build_natal_section(payload)
        date_str = payload.today_date
        events_str = self._format_astro_daily_events(astro_daily_events)
        day_profile_str = self._format_day_profile(
            day_climate=day_climate,
            best_window=best_window,
            turning_point=turning_point,
            domain_ranking=domain_ranking,
        )
        windows_str = self._format_windows(time_windows, domain_ranking=domain_ranking)
        prompt = f"""
CONTEXTE ASTROLOGIQUE DU JOUR ({date_str})

PROFIL NATAL DE L'UTILISATEUR :
{natal_section}

PROFIL DE LA JOURNÉE :
{day_profile_str}

ÉVÉNEMENTS CÉLESTES MAJEURS DU JOUR :
{events_str}

DÉROULÉ DE LA JOURNÉE (CRÉNEAUX HORAIRES) :
{windows_str}

PARAMÈTRES UTILISATEUR :
- Profil astrologue demandé : {astrologer_profile_key}
- Ton demandé : {payload.astrologer_profile.get("tonality", "bienveillant")}
- Langue demandée : {"Français" if lang == "fr" else "English"}
- Variante de narration : {variant_code or "standard"}
"""
        return prompt.strip()

    def _resolve_payload(
        self, common_context: PromptCommonContext | QualifiedContext
    ) -> PromptCommonContext:
        if isinstance(common_context, QualifiedContext):
            return common_context.payload
        return common_context

    def _build_natal_section(self, ctx: PromptCommonContext) -> str:
        if ctx.natal_interpretation:
            natal_summary = " ".join(ctx.natal_interpretation.split())[:1400]
            return f"Synthèse natale existante : {natal_summary}"

        if not ctx.natal_data:
            return "Profil natal non disponible."

        pos = ctx.natal_data.get("planet_positions", [])
        planets = []
        important_codes = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        fallback_codes = ["SO", "LU", "ME", "VE", "MA", "JU", "SA"]
        for p in pos:
            code = str(p.get("planet_code", ""))
            normalized = code.lower()
            if normalized in important_codes or code.upper() in fallback_codes:
                label = PLANET_CODE_LABELS.get(code.upper()) or get_planet_name_fr(normalized)
                sign = self._format_sign_label(p.get("sign_code"))
                planets.append(f"{label} en {sign}")
            if len(planets) >= 6:
                break

        houses = ctx.natal_data.get("houses", [])
        asc = "Inconnu"
        if houses:
            asc = sign_from_longitude(houses[0].get("cusp_longitude", 0))
            asc = self._format_sign_label(asc)

        return (
            f"Placements de base : {', '.join(planets) if planets else 'non disponibles'}. "
            f"Ascendant : {asc}. "
            f"Précision : {ctx.precision_level}."
        )

    def _format_astro_daily_events(self, astro_daily_events: dict[str, Any] | None) -> str:
        if not astro_daily_events:
            return "Aucun événement majeur particulier."

        sections = []

        sky = astro_daily_events.get("sky_aspects", [])
        if sky:
            sections.append("Aspects du ciel : " + ", ".join(sky))

        aspects = astro_daily_events.get("aspects", [])
        if aspects:
            sections.append("Aspects transit-natal : " + ", ".join(aspects))

        nodes = astro_daily_events.get("nodes", [])
        if nodes:
            sections.append("Nœuds lunaires : " + ", ".join(nodes))

        progressions = astro_daily_events.get("progressions", [])
        if progressions:
            sections.append("Progressions : " + ", ".join(progressions))

        returns = astro_daily_events.get("returns", [])
        if returns:
            sections.append("Retours : " + ", ".join(returns))

        ingresses = astro_daily_events.get("ingresses", [])
        if ingresses:
            sections.append("Ingresses : " + ", ".join(i["text"] for i in ingresses))

        fixed_stars = astro_daily_events.get("fixed_stars", [])
        if fixed_stars:
            sections.append("Étoiles fixes : " + ", ".join(fixed_stars))

        planet_positions = astro_daily_events.get("planet_positions", [])
        if planet_positions:
            sections.append("Positions : " + ", ".join(planet_positions))

        if not sections:
            return "Aucun événement majeur particulier."
        return "\n".join(f"- {s}" for s in sections)

    def _format_day_profile(
        self,
        *,
        day_climate: dict[str, Any] | None,
        best_window: dict[str, Any] | None,
        turning_point: dict[str, Any] | None,
        domain_ranking: list[dict[str, Any]] | None,
    ) -> str:
        sections = []

        if day_climate:
            top_domains = self._format_domain_labels(
                day_climate.get("top_domains", []), domain_ranking
            )
            sections.append(
                f"- Climat général : {day_climate.get('label', 'non disponible')} "
                f"(ton={day_climate.get('tone', 'inconnu')}, "
                f"intensité={day_climate.get('intensity', 'n/a')}, "
                f"stabilité={day_climate.get('stability', 'n/a')})."
            )
            if day_climate.get("summary"):
                sections.append(f"- Résumé moteur : {day_climate['summary']}")
            if top_domains:
                sections.append(f"- Domaines les plus activés : {top_domains}.")
            if day_climate.get("watchout"):
                watchout = self._format_domain_labels([day_climate["watchout"]], domain_ranking)
                sections.append(f"- Point de vigilance : {watchout}.")

        if best_window:
            actions = ", ".join(best_window.get("recommended_actions", []))
            sections.append(
                f"- Meilleur créneau : {best_window.get('time_range', 'non disponible')} "
                f"({best_window.get('label', 'moment favorable')}). "
                f"Pourquoi : {best_window.get('why', '')}"
            )
            if actions:
                sections.append(f"- Actions favorisées dans ce créneau : {actions}.")

        if turning_point:
            impacted = self._format_domain_labels(
                turning_point.get("affected_domains", []), domain_ranking
            )
            sections.append(
                f"- Moment clé principal : {turning_point.get('time', 'non disponible')} — "
                f"{turning_point.get('title', 'Bascule')} "
                f"({turning_point.get('change_type', 'recomposition')})."
            )
            if turning_point.get("what_changes"):
                sections.append(f"- Ce qui change : {turning_point['what_changes']}")
            if impacted:
                sections.append(f"- Domaines concernés : {impacted}.")
            if turning_point.get("do") or turning_point.get("avoid"):
                sections.append(
                    f"- Posture utile : {turning_point.get('do', 'n/a')} | À éviter : "
                    f"{turning_point.get('avoid', 'n/a')}"
                )

        if not sections:
            return "- Pas de synthèse structurelle supplémentaire disponible."
        return "\n".join(sections)

    def _format_windows(
        self, windows: list[dict[str, Any]], *, domain_ranking: list[dict[str, Any]] | None = None
    ) -> str:
        lines = []
        for w in windows:
            key = w.get("period_key", "?")
            regime = w.get("regime", "?")
            label = w.get("label", "")
            domains = self._format_domain_labels(w.get("top_domains", []), domain_ranking)
            action_hint = w.get("action_hint", "")
            slot_events = w.get("astro_events", [])
            events_part = f" Événements : {', '.join(slot_events)}." if slot_events else ""
            lines.append(
                f"[{key}] {w.get('time_range')}: {label} (Régime: {regime}). "
                f"Domaines: {domains or 'non précisés'}. "
                f"Orientation pratique: {action_hint or 'non précisée'}.{events_part}"
            )
        return "\n".join(lines)

    def _format_domain_labels(
        self, domain_keys: list[str] | tuple[str, ...], domain_ranking: list[dict[str, Any]] | None
    ) -> str:
        if not domain_keys:
            return ""
        label_by_key = {
            str(item.get("key")): str(item.get("label"))
            for item in (domain_ranking or [])
            if item.get("key") and item.get("label")
        }
        labels = [label_by_key.get(key, str(key)) for key in domain_keys]
        return ", ".join(labels)

    def _format_sign_label(self, raw_sign: Any) -> str:
        if raw_sign is None:
            return "signe inconnu"
        sign = str(raw_sign).strip().lower()
        if sign in SIGN_LABELS_FR:
            return SIGN_LABELS_FR[sign]
        if len(sign) == 3:
            return get_sign_name_fr(sign)
        return str(raw_sign).capitalize()
