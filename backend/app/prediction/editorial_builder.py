from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.prediction.explainability import ContributorEntry, ExplainabilityReport
    from app.prediction.schemas import EngineOutput
    from app.prediction.turning_point_detector import TurningPoint


@dataclass(frozen=True)
class BestWindow:
    start_local: datetime
    end_local: datetime
    dominant_category: str


@dataclass(frozen=True)
class CategorySummary:
    code: str
    note_20: int
    power: float
    volatility: float


@dataclass(frozen=True)
class EditorialOutput:
    top3_categories: list[CategorySummary]
    bottom2_categories: list[CategorySummary]
    main_pivot: TurningPoint | None
    best_window: BestWindow | None
    caution_flags: dict[str, bool]
    overall_tone: str
    top3_contributors_per_category: dict[str, list[ContributorEntry]]


class EditorialOutputBuilder:
    CAUTION_NOTE_THRESHOLD = 7
    CAUTION_VOL_THRESHOLD = 1.5
    DEFAULT_CAUTION_CODES = {"sante", "argent"}

    def build(
        self, engine_output: EngineOutput, explainability: ExplainabilityReport
    ) -> EditorialOutput:
        """
        Produce a clear editorial contract from raw engine output.
        No LLM calls or free text generation here.
        """
        top3, bottom2 = self._build_top3_bottom2(engine_output.category_scores)
        main_pivot = self._find_main_pivot(engine_output.turning_points)
        best_window = self._find_best_window(engine_output.time_blocks, top3)
        caution_flags = self._compute_caution_flags(
            engine_output.category_scores, engine_output.run_metadata
        )
        overall_tone = self._derive_tone(top3)
        top3_contributors = self._extract_contributors(explainability, top3)

        return EditorialOutput(
            top3_categories=top3,
            bottom2_categories=bottom2,
            main_pivot=main_pivot,
            best_window=best_window,
            caution_flags=caution_flags,
            overall_tone=overall_tone,
            top3_contributors_per_category=top3_contributors,
        )

    def _build_top3_bottom2(
        self, scores: dict[str, Any]
    ) -> tuple[list[CategorySummary], list[CategorySummary]]:
        sorted_scores = sorted(
            [(code, s) for code, s in scores.items()],
            key=lambda item: (
                -self._score_value(item[1], "note_20", 0),
                self._score_value(item[1], "sort_order", 0),
            ),
        )

        top3_raw = sorted_scores[:3]
        top3 = [
            CategorySummary(
                code=c,
                note_20=self._score_value(s, "note_20", 0),
                power=self._score_value(s, "power", 0.0),
                volatility=self._score_value(s, "volatility", 0.0),
            )
            for c, s in top3_raw
        ]

        top3_codes = {c.code for c in top3}
        remaining = [(code, score) for code, score in sorted_scores if code not in top3_codes]
        sorted_remaining = sorted(
            remaining,
            key=lambda item: (
                self._score_value(item[1], "note_20", 0),
                self._score_value(item[1], "sort_order", 0),
            ),
        )
        bottom2_raw = sorted_remaining[:2]
        bottom2 = [
            CategorySummary(
                code=c,
                note_20=self._score_value(s, "note_20", 0),
                power=self._score_value(s, "power", 0.0),
                volatility=self._score_value(s, "volatility", 0.0),
            )
            for c, s in bottom2_raw
        ]

        return top3, bottom2

    def _find_main_pivot(self, turning_points: list[Any]) -> Any | None:
        if not turning_points:
            return None
        return max(turning_points, key=lambda tp: getattr(tp, "severity", 0.0))

    def _find_best_window(
        self, time_blocks: list[Any], top3: list[CategorySummary]
    ) -> BestWindow | None:
        if not time_blocks or not top3:
            return None

        top3_codes = [c.code for c in top3]
        ordered_blocks = sorted(
            time_blocks,
            key=lambda block: getattr(block, "start_local", datetime.min),
        )
        best_block = max(
            ordered_blocks,
            key=lambda block: (
                self._window_score(block, top3_codes),
                1 if top3_codes[0] in getattr(block, "dominant_categories", []) else 0,
            ),
        )

        dominant = top3_codes[0]
        dom_cats = getattr(best_block, "dominant_categories", [])
        if dom_cats:
            dominant = dom_cats[0]

        return BestWindow(
            start_local=best_block.start_local,
            end_local=best_block.end_local,
            dominant_category=dominant,
        )

    def _compute_caution_flags(
        self, scores: dict[str, Any], params: dict[str, Any] | None
    ) -> dict[str, bool]:
        caution_codes = set(
            (params or {}).get("caution_category_codes", list(self.DEFAULT_CAUTION_CODES))
        )
        flags = {}
        for code in caution_codes:
            s = scores.get(code)
            if s:
                note = self._score_value(s, "note_20", 0)
                vol = self._score_value(s, "volatility", 0.0)
                flags[code] = (
                    note <= self.CAUTION_NOTE_THRESHOLD
                    or vol >= self.CAUTION_VOL_THRESHOLD
                )
        return flags

    def _derive_tone(self, top3: list[CategorySummary]) -> str:
        if not top3:
            return "neutral"
        notes = [c.note_20 for c in top3]
        avg = sum(notes) / len(notes)
        spread = max(notes) - min(notes)
        if avg >= 13:
            return "positive"
        if avg <= 7:
            return "negative"
        if spread >= 5:
            return "mixed"
        return "neutral"

    def _extract_contributors(
        self, explainability: ExplainabilityReport, top3: list[CategorySummary]
    ) -> dict[str, list[ContributorEntry]]:
        result = {
            category_code: category_explainability.top_contributors
            for category_code, category_explainability in explainability.categories.items()
        }
        for cat in top3:
            result.setdefault(cat.code, [])
        return result

    def _score_value(self, score: Any, field_name: str, default: Any) -> Any:
        if isinstance(score, dict):
            return score.get(field_name, default)
        return getattr(score, field_name, default)

    def _window_score(self, block: Any, top3_codes: list[str]) -> float:
        category_means = getattr(block, "category_means", None)
        if isinstance(category_means, dict):
            values = [float(category_means.get(code, 0.0)) for code in top3_codes]
            return sum(values) / len(values)

        dominant_categories = getattr(block, "dominant_categories", [])
        overlap = len([code for code in top3_codes if code in dominant_categories])
        tone_priority = {"positive": 3.0, "mixed": 2.0, "neutral": 1.0, "negative": 0.0}
        return overlap + tone_priority.get(getattr(block, "tone_code", ""), 0.0)
