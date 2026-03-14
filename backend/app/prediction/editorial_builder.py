from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from app.prediction.category_codes import normalize_category_code, normalize_category_codes

from .schemas import BestWindow, CategorySummary, EditorialOutput, EngineOutput

if TYPE_CHECKING:
    from .explainability import ExplainabilityReport
    from .schemas import V3EvidencePack


class EditorialOutputBuilder:
    CAUTION_NOTE_THRESHOLD = 7
    CAUTION_VOL_THRESHOLD = 1.5
    DEFAULT_CAUTION_CODES = {"health", "money"}

    def build(
        self, engine_output: EngineOutput, explainability: ExplainabilityReport
    ) -> EditorialOutput:
        """Legacy build from EngineOutput (V2)."""
        top3, bottom2 = self._build_top3_bottom2(engine_output.category_scores)
        main_pivot = self._find_main_pivot(engine_output.turning_points)
        best_window = self._find_best_window(
            engine_output.time_blocks, top3, engine_output.category_scores
        )
        caution_flags = self._compute_caution_flags(
            engine_output.category_scores, engine_output.run_metadata
        )
        overall_tone = self._derive_tone(top3)
        top3_contributors = self._extract_contributors(explainability, top3)
        return EditorialOutput(
            local_date=engine_output.effective_context.local_date,
            top3_categories=top3,
            bottom2_categories=bottom2,
            main_pivot=main_pivot,
            best_window=best_window,
            caution_flags=caution_flags,
            overall_tone=overall_tone,
            top3_contributors_per_category=top3_contributors,
        )

    def build_from_evidence(self, evidence: V3EvidencePack) -> EditorialOutput:
        """
        AC1 Story 42.16: Branch editorial on the evidence pack.
        Ensures wording cannot invent relief absent from evidence.
        """
        # 1. Themes
        sorted_themes = sorted(evidence.themes.values(), key=lambda t: t.score_20, reverse=True)
        top3 = [
            CategorySummary(
                code=t.code,
                note_20=round(t.score_20),
                power=t.intensity / 20.0,
                volatility=1.0 - t.stability / 20.0,
            )
            for t in sorted_themes[:3]
        ]

        remaining = sorted_themes[3:]
        bottom2 = [
            CategorySummary(
                code=t.code,
                note_20=round(t.score_20),
                power=t.intensity / 20.0,
                volatility=1.0 - t.stability / 20.0,
            )
            for t in sorted(remaining, key=lambda t: t.score_20)[:2]
        ]

        # 2. Main Pivot (from turning points)
        main_pivot = None
        if evidence.turning_points:
            main_tp = max(evidence.turning_points, key=lambda tp: tp.amplitude)
            from types import SimpleNamespace

            main_pivot = SimpleNamespace(
                local_time=main_tp.local_time,
                severity=main_tp.amplitude / 10.0,
                summary=f"Bascule ({main_tp.reason})",
            )

        # 3. Best Window
        best_window = None
        if evidence.time_windows:
            # Prioritize favorable windows with high confidence
            candidates = [w for w in evidence.time_windows if w.type in ("favorable", "pivot")]
            if candidates:
                bw = max(candidates, key=lambda w: (w.score, w.confidence))
                best_window = BestWindow(
                    start_local=bw.start_local,
                    end_local=bw.end_local,
                    dominant_category=bw.themes[0] if bw.themes else "unknown",
                )

        # 4. Tone
        overall_tone = evidence.day_profile.get("tone") or self._derive_tone(top3)

        local_date = self._resolve_evidence_local_date(evidence)

        return EditorialOutput(
            local_date=local_date,
            top3_categories=top3,
            bottom2_categories=bottom2,
            main_pivot=main_pivot,
            best_window=best_window,
            caution_flags={},  # Will be derived later if needed
            overall_tone=overall_tone,
            top3_contributors_per_category={},  # Handled by evidence drivers in interpretation
        )

    def _resolve_evidence_local_date(self, evidence: V3EvidencePack):
        raw_local_date = evidence.day_profile.get("local_date")
        if isinstance(raw_local_date, str):
            try:
                return datetime.fromisoformat(raw_local_date).date()
            except ValueError:
                try:
                    return date.fromisoformat(raw_local_date)
                except ValueError:
                    pass
        if evidence.time_windows:
            return evidence.time_windows[0].start_local.date()
        if evidence.turning_points:
            return evidence.turning_points[0].local_time.date()
        return evidence.generated_at.date()

    def _build_top3_bottom2(self, scores):
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

    def _find_main_pivot(self, turning_points):
        if not turning_points:
            return None
        return max(turning_points, key=lambda tp: getattr(tp, "severity", 0.0))

    def _find_best_window(self, time_blocks, top3, category_scores=None):
        if not time_blocks or not top3:
            return None
        top3_codes = [c.code for c in top3]
        ordered_blocks = sorted(
            time_blocks,
            key=lambda block: getattr(block, "start_local", datetime.min),
        )
        scores = category_scores or {}
        best_block = max(
            ordered_blocks,
            key=lambda block: self._window_score(block, top3_codes, scores),
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

    def _compute_caution_flags(self, scores, params):
        caution_codes = set(
            normalize_category_codes(
                (params or {}).get("caution_category_codes", list(self.DEFAULT_CAUTION_CODES))
            )
        )
        flags = {}
        for code in caution_codes:
            s = scores.get(code)
            if s is None:
                s = scores.get(normalize_category_code(code))
            if s:
                note = self._score_value(s, "note_20", 0)
                vol = self._score_value(s, "volatility", 0.0)
                flags[code] = (
                    note <= self.CAUTION_NOTE_THRESHOLD or vol >= self.CAUTION_VOL_THRESHOLD
                )
        return flags

    def _derive_tone(self, top3):
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

    def _extract_contributors(self, explainability, top3):
        result = {
            category_code: category_explainability.top_contributors
            for category_code, category_explainability in explainability.categories.items()
        }
        for cat in top3:
            result.setdefault(cat.code, [])
        return result

    def _score_value(self, score, field_name, default):
        if isinstance(score, dict):
            return score.get(field_name, default)
        return getattr(score, field_name, default)

    def _window_score(self, block, top3_codes, category_scores=None):
        category_means = getattr(block, "category_means", None)
        if isinstance(category_means, dict):
            notes = [float(category_means.get(code, 0.0)) for code in top3_codes]
            avg_note = sum(notes) / len(notes) if notes else 0.0
            vols = []
            for code in top3_codes:
                score = (category_scores or {}).get(code)
                if score is not None:
                    vol = self._score_value(score, "volatility", 0.5)
                    vols.append(float(vol))
            avg_vol = sum(vols) / len(vols) if vols else 0.5
            stability = 1.0 / (1.0 + avg_vol)
            tone_map = {"positive": 0.1, "mixed": 0.0, "neutral": 0.0, "negative": -0.1}
            tone_factor = 1.0 + tone_map.get(getattr(block, "tone_code", "neutral"), 0.0)
            return avg_note * stability * tone_factor
        dominant_categories = getattr(block, "dominant_categories", [])
        overlap = len([code for code in top3_codes if code in dominant_categories])
        tone_priority = {"positive": 3.0, "mixed": 2.0, "neutral": 1.0, "negative": 0.0}
        return overlap + tone_priority.get(getattr(block, "tone_code", ""), 0.0)
