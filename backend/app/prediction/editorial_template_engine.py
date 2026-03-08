# backend/app/prediction/editorial_template_engine.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

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


class EditorialTemplateEngine:
    """
    Engine to render editorial texts from templates and EditorialOutput data.
    Purely mechanical, no LLM involved.
    """

    TEMPLATE_BASE = Path(__file__).parent / "editorial_templates"

    # Internal mappings for labels when not provided by DB
    CATEGORY_LABELS = {
        "fr": {
            "amour": "Amour & Relations",
            "travail": "Travail & Carrière",
            "vitalite": "Vitalité & Énergie",
            "finances": "Finances & Matériel",
        }
    }

    TONE_LABELS = {
        "fr": {
            "positive": "très porteuse",
            "mixed": "contrastée",
            "neutral": "équilibrée",
            "negative": "exigeante",
        }
    }

    SEVERITY_LABELS = {
        "fr": {
            "low": "mineur",
            "medium": "notable",
            "high": "majeur",
            "critical": "critique",
        }
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

    def render(self, editorial: EditorialOutput, lang: str = "fr") -> EditorialTextOutput:
        """
        Renders the full editorial content.
        """
        # 1. Intro
        intro_tpl = self._load_template(lang, "intro_du_jour")
        tone_label = self.TONE_LABELS.get(lang, {}).get(editorial.overall_tone, "neutre")
        cat_labels = self.CATEGORY_LABELS.get(lang, {})
        top3_labels_list = [cat_labels.get(c.code, c.code) for c in editorial.top3_categories]
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
            label = cat_labels.get(cat.code, cat.code)
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
            dom_label = cat_labels.get(dom_category, dom_category)
            window_phrase = win_tpl.format(
                window_start=start_str,
                window_end=end_str,
                dominant_category_label=dom_label,
            )

        # 5. Cautions
        caution_sante = None
        if editorial.caution_flags.get("sante"):
            caution_sante = self._load_template(lang, "prudence_sante")

        caution_argent = None
        if editorial.caution_flags.get("argent"):
            caution_argent = self._load_template(lang, "prudence_argent")

        return EditorialTextOutput(
            intro=intro,
            category_summaries=category_summaries,
            pivot_phrase=pivot_phrase,
            window_phrase=window_phrase,
            caution_sante=caution_sante,
            caution_argent=caution_argent,
        )
