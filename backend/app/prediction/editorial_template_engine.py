# backend/app/prediction/editorial_template_engine.py
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.prediction.category_codes import normalize_category_code

if TYPE_CHECKING:
    from app.prediction.editorial_builder import EditorialOutput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditorialTextOutput:
    """Final rendered editorial texts."""

    intro: str
    category_summaries: dict[str, str]
    pivot_phrase: str | None
    window_phrase: str | None
    caution_sante: str | None
    caution_argent: str | None
    time_block_summaries: list[str] = field(default_factory=list)
    turning_point_summaries: list[str] = field(default_factory=list)


class EditorialTemplateEngine:
    """
    Engine to render editorial texts from templates and EditorialOutput data.
    Purely mechanical, no LLM involved.
    """

    TEMPLATE_BASE = Path(__file__).parent / "editorial_templates"

    # Internal mappings for labels when not provided by DB
    CATEGORY_LABELS = {
        "fr": {
            "love": "Amour & Relations",
            "work": "Travail",
            "career": "Carrière",
            "energy": "Énergie & Vitalité",
            "mood": "Humeur & Climat intérieur",
            "health": "Santé & Hygiène de vie",
            "money": "Argent & Ressources",
            "sex_intimacy": "Sexe & Intimité",
            "family_home": "Famille & Foyer",
            "social_network": "Vie sociale & Réseau",
            "communication": "Communication",
            "pleasure_creativity": "Plaisir & Créativité",
        },
        "en": {
            "love": "Love & Relationships",
            "work": "Work",
            "career": "Career",
            "energy": "Energy & Vitality",
            "mood": "Mood & Inner Climate",
            "health": "Health & Routine",
            "money": "Money & Resources",
            "sex_intimacy": "Sex & Intimacy",
            "family_home": "Family & Home",
            "social_network": "Social Network",
            "communication": "Communication",
            "pleasure_creativity": "Pleasure & Creativity",
        },
    }

    TONE_LABELS = {
        "fr": {
            "positive": "très porteuse",
            "mixed": "contrastée",
            "neutral": "équilibrée",
            "negative": "exigeante",
        },
        "en": {
            "positive": "very positive",
            "mixed": "mixed",
            "neutral": "balanced",
            "negative": "challenging",
        },
    }

    SEVERITY_LABELS = {
        "fr": {
            "low": "mineur",
            "medium": "notable",
            "high": "majeur",
            "critical": "critique",
        },
        "en": {
            "low": "minor",
            "medium": "notable",
            "high": "major",
            "critical": "critical",
        },
    }

    def _get_band_label(self, note: int, lang: str = "fr") -> str:
        if lang == "fr":
            if note <= 5:
                return "fragile"
            if note <= 9:
                return "tendu"
            if note <= 12:
                return "neutre"
            if note <= 16:
                return "porteur"
            return "très favorable"
        if lang == "en":
            if note <= 5:
                return "fragile"
            if note <= 9:
                return "tense"
            if note <= 12:
                return "neutral"
            if note <= 16:
                return "favorable"
            return "very favorable"
        return "N/A"

    def _get_severity_label(self, severity: float, lang: str = "fr") -> str:
        labels = self.SEVERITY_LABELS.get(lang, self.SEVERITY_LABELS["fr"])
        if severity <= 0.25:
            return labels["low"]
        if severity <= 0.5:
            return labels["medium"]
        if severity <= 0.75:
            return labels["high"]
        return labels["critical"]

    def _load_template(self, lang: str, name: str) -> str:
        path = self.TEMPLATE_BASE / lang / f"{name}.txt"
        if not path.exists():
            # [AI-Review] Fail explicitly if template missing
            raise FileNotFoundError(f"Template not found: {path}")
        return path.read_text(encoding="utf-8").strip()

    def render(
        self,
        editorial: EditorialOutput,
        lang: str = "fr",
        time_blocks: list | None = None,
        turning_points: list | None = None,
    ) -> EditorialTextOutput:
        """
        Renders the full editorial content.
        """
        # 1. Intro
        intro_tpl = self._load_template(lang, "intro_du_jour")
        tone_labels = self.TONE_LABELS.get(lang, self.TONE_LABELS["fr"])
        tone_label = tone_labels.get(
            editorial.overall_tone,
            tone_labels.get("neutral", self.TONE_LABELS["fr"]["neutral"]),
        )
        top3_labels_list = [
            self._get_category_label(c.code, lang) for c in editorial.top3_categories
        ]
        top3_labels = ", ".join(top3_labels_list)

        intro = intro_tpl.format(
            date_local=editorial.local_date.isoformat(),
            overall_tone_label=tone_label,
            top3_labels=top3_labels,
        )

        # 2. Category Summaries
        cat_tpl = self._load_template(lang, "resume_categorie")
        category_summaries = {}
        for cat in editorial.top3_categories:
            label = self._get_category_label(cat.code, lang)
            category_summaries[cat.code] = cat_tpl.format(
                category_label=label,
                note_20=cat.note_20,
                band=self._get_band_label(cat.note_20, lang),
            )

        # 3. Pivot
        pivot_phrase = None
        if editorial.main_pivot:
            pivot_tpl = self._load_template(lang, "phrase_pivot")
            time_str = "N/A"
            severity = 0.0

            pivot = editorial.main_pivot
            if hasattr(pivot, "local_time") and isinstance(pivot.local_time, datetime):
                time_str = pivot.local_time.strftime("%H:%M")
            elif isinstance(pivot, dict):
                time_val = pivot.get("occurred_at_local")
                if isinstance(time_val, datetime):
                    time_str = time_val.strftime("%H:%M")
                elif isinstance(time_val, str):
                    time_str = time_val

            if hasattr(pivot, "severity"):
                severity = pivot.severity
            elif isinstance(pivot, dict):
                severity = pivot.get("severity", 0.0)

            pivot_phrase = pivot_tpl.format(
                pivot_time=time_str,
                pivot_severity_label=self._get_severity_label(severity, lang),
            )

        # 4. Window
        window_phrase = None
        if editorial.best_window:
            win_tpl = self._load_template(lang, "meilleure_fenetre")
            start_str = editorial.best_window.start_local.strftime("%H:%M")
            end_str = editorial.best_window.end_local.strftime("%H:%M")
            dom_category = editorial.best_window.dominant_category
            dom_label = self._get_category_label(dom_category, lang)
            window_phrase = win_tpl.format(
                window_start=start_str,
                window_end=end_str,
                dominant_category_label=dom_label,
            )

        # 5. Cautions
        caution_sante = None
        if editorial.caution_flags.get("health") or editorial.caution_flags.get("sante"):
            caution_sante = self._load_template(lang, "prudence_sante")

        caution_argent = None
        if editorial.caution_flags.get("money") or editorial.caution_flags.get("argent"):
            caution_argent = self._load_template(lang, "prudence_argent")

        # 6. Time Blocks and Turning Points Summaries
        time_block_summaries = []
        if time_blocks:
            time_block_summaries = [self._render_time_block_summary(b, lang) for b in time_blocks]

        turning_point_summaries = []
        if turning_points:
            turning_point_summaries = [self._render_turning_point_summary(tp, lang) for tp in turning_points]

        return EditorialTextOutput(
            intro=intro,
            category_summaries=category_summaries,
            pivot_phrase=pivot_phrase,
            window_phrase=window_phrase,
            caution_sante=caution_sante,
            caution_argent=caution_argent,
            time_block_summaries=time_block_summaries,
            turning_point_summaries=turning_point_summaries,
        )

    def _get_category_label(self, code: str, lang: str) -> str:
        labels = self.CATEGORY_LABELS.get(lang, self.CATEGORY_LABELS["fr"])
        canonical_code = normalize_category_code(code)
        return labels.get(canonical_code, canonical_code)

    def _render_time_block_summary(self, block: Any, lang: str) -> str:
        tpl = self._load_template(lang, "resume_bloc_horaire")
        tone_labels = self.TONE_LABELS.get(lang, self.TONE_LABELS["fr"])
        tone_label = tone_labels.get(block.tone_code, block.tone_code)
        
        cats_labels = [self._get_category_label(c, lang) for c in block.dominant_categories]
        categories_labels = ", ".join(cats_labels) if cats_labels else ("plusieurs domaines" if lang == "fr" else "several areas")

        return tpl.format(
            start_time=block.start_local.strftime("%H:%M"),
            end_time=block.end_local.strftime("%H:%M"),
            tone_label=tone_label,
            categories_labels=categories_labels,
        )

    def _render_turning_point_summary(self, tp: Any, lang: str) -> str:
        tpl = self._load_template(lang, "resume_turning_point")
        
        cats_labels = [self._get_category_label(c, lang) for c in tp.categories_impacted]
        categories_labels = ", ".join(cats_labels) if cats_labels else ("plusieurs domaines" if lang == "fr" else "several areas")

        return tpl.format(
            pivot_time=tp.local_time.strftime("%H:%M"),
            pivot_severity_label=self._get_severity_label(tp.severity, lang),
            categories_labels=categories_labels,
        )
