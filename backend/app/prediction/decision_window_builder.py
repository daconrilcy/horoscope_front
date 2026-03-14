from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from app.prediction.schemas import DecisionWindow

if TYPE_CHECKING:
    from app.prediction.block_generator import TimeBlock
    from app.prediction.schemas import V3TimeBlock, V3TurningPoint
    from app.prediction.turning_point_detector import TurningPoint


class DecisionWindowBuilder:
    """AC3 — Builds business decision windows from time blocks.

    Decision windows communicate *when* to act, wait, or be cautious.
    Types:
        - "favorable"  : positively toned block with meaningful signal
        - "prudence"   : negative or volatile block, caution warranted
        - "pivot"      : block contains a turning point
    Neutral non-pivot blocks are omitted to reduce noise (AC3).
    """

    MAX_PIVOT_WINDOW_DURATION = timedelta(minutes=90)
    PIVOT_SCORE = 12.0

    # V3 Thresholds for Actionability (AC3, AC4)
    MIN_V3_WINDOW_INTENSITY = 4.0
    MIN_V3_WINDOW_CONFIDENCE = 0.4

    def build(
        self,
        time_blocks: list[TimeBlock],
        turning_points: list[TurningPoint],
        category_scores: dict[str, Any],
    ) -> list[DecisionWindow]:
        pivot_times = sorted(tp.local_time for tp in turning_points)
        windows: list[DecisionWindow] = []

        for block in time_blocks:
            pivot_time = next(
                (pt for pt in pivot_times if block.start_local <= pt < block.end_local),
                None,
            )
            has_pivot = pivot_time is not None
            window_type = self._classify(block, has_pivot)
            if window_type == "neutral":
                continue

            score = self._block_score(block, category_scores, window_type)
            confidence = self._block_confidence(block, category_scores)
            dominant = list(block.dominant_categories[:2])
            start_local, end_local = self._window_bounds(block, window_type, pivot_time)

            windows.append(
                DecisionWindow(
                    start_local=start_local,
                    end_local=end_local,
                    window_type=window_type,
                    score=score,
                    confidence=confidence,
                    dominant_categories=dominant,
                )
            )

        return windows

    def build_v3(
        self,
        v3_blocks: list[V3TimeBlock],
        v3_turning_points: list[V3TurningPoint],
        category_scores: dict[str, Any],
    ) -> list[DecisionWindow]:
        """Derive decision windows from V3 regime blocks (Story 42.11)."""
        pivot_times = sorted(tp.local_time for tp in v3_turning_points)
        windows: list[DecisionWindow] = []

        for block in v3_blocks:
            # 1. Actionability Filter (AC3, AC4)
            # Sobriety on weak days: ignore low intensity or low confidence blocks
            if block.intensity < self.MIN_V3_WINDOW_INTENSITY and block.orientation == "stable":
                continue

            if block.confidence < self.MIN_V3_WINDOW_CONFIDENCE:
                continue

            # 2. Map Orientation to Type
            pivot_time = next(
                (pt for pt in pivot_times if block.start_local <= pt < block.end_local),
                None,
            )
            has_pivot = pivot_time is not None

            window_type = self._classify_v3(block, has_pivot)
            if window_type == "neutral":
                continue

            # 3. Calculate Score (Backward compatibility or V3 metrics)
            score = self._block_score_v3(block, category_scores, window_type)

            # 4. Bounds and Dominant Themes
            start_local, end_local = self._window_bounds_v3(block, window_type, pivot_time)
            dominant = list(block.dominant_themes[:2])

            windows.append(
                DecisionWindow(
                    start_local=start_local,
                    end_local=end_local,
                    window_type=window_type,
                    score=score,
                    confidence=block.confidence,
                    dominant_categories=dominant,
                    orientation=block.orientation,
                    intensity=block.intensity,
                )
            )

        return windows

    def _classify(self, block: TimeBlock, has_pivot: bool) -> str:
        tone = getattr(block, "tone_code", "neutral")
        if tone == "positive":
            return "favorable"
        if tone in ("negative", "mixed"):
            return "prudence"
        if has_pivot:
            return "pivot"
        return "neutral"

    def _classify_v3(self, block: V3TimeBlock, has_pivot: bool) -> str:
        if block.orientation == "rising":
            return "favorable"
        if block.orientation in ("falling", "volatile"):
            return "prudence"
        if has_pivot:
            return "pivot"
        # High intensity stable can be interesting
        if block.orientation == "stable" and block.intensity > 10.0:
            return "favorable"  # Assume high intensity stable is notable
        return "neutral"

    def _window_bounds(
        self,
        block: TimeBlock,
        window_type: str,
        pivot_time: Any,
    ) -> tuple[Any, Any]:
        if window_type != "pivot" or pivot_time is None:
            return block.start_local, block.end_local

        clipped_start = max(block.start_local, pivot_time)
        clipped_end = min(block.end_local, pivot_time + self.MAX_PIVOT_WINDOW_DURATION)
        return clipped_start, max(clipped_start, clipped_end)

    def _window_bounds_v3(
        self,
        block: V3TimeBlock,
        window_type: str,
        pivot_time: Any,
    ) -> tuple[Any, Any]:
        return self._window_bounds(block, window_type, pivot_time)

    def _block_score(
        self,
        block: TimeBlock,
        category_scores: dict[str, Any],
        window_type: str,
    ) -> float:
        if window_type == "pivot":
            return self.PIVOT_SCORE

        notes: list[float] = []
        for code in list(block.dominant_categories)[:2]:
            s = category_scores.get(code)
            if s is not None:
                note = s.get("note_20", 0) if isinstance(s, dict) else getattr(s, "note_20", 0)
                notes.append(float(note))
        return sum(notes) / len(notes) if notes else 10.0

    def _block_score_v3(
        self,
        block: V3TimeBlock,
        category_scores: dict[str, Any],
        window_type: str,
    ) -> float:
        if window_type == "pivot":
            return self.PIVOT_SCORE

        # In V3, intensity is already on 0-20 scale
        # But we might want to blend with category notes for backward compat in UI
        notes: list[float] = []
        for code in list(block.dominant_themes)[:2]:
            s = category_scores.get(code)
            if s is not None:
                if isinstance(s, dict):
                    note = s.get("note_20", s.get("score_20", 0))
                else:
                    # V3DailyMetrics uses score_20, legacy uses note_20
                    note = getattr(s, "score_20", getattr(s, "note_20", 0))
                notes.append(float(note))

        avg_note = sum(notes) / len(notes) if notes else 10.0
        # Blend: 70% V3 intensity, 30% day-level note
        return (block.intensity * 0.7) + (avg_note * 0.3)

    def _block_confidence(self, block: TimeBlock, category_scores: dict[str, Any]) -> float:
        vols: list[float] = []
        for code in list(block.dominant_categories)[:2]:
            s = category_scores.get(code)
            if s is not None:
                vol = (
                    s.get("volatility", 0.5)
                    if isinstance(s, dict)
                    else getattr(s, "volatility", 0.5)
                )
                vols.append(float(vol))
        avg_vol = sum(vols) / len(vols) if vols else 0.5
        # vol=0 → confidence=1.0, vol=3 → confidence=0.0
        return max(0.0, min(1.0, 1.0 - avg_vol / 3.0))
