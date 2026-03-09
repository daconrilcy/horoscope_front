from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.prediction.schemas import DecisionWindow

if TYPE_CHECKING:
    from app.prediction.block_generator import TimeBlock
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

    def build(
        self,
        time_blocks: list[TimeBlock],
        turning_points: list[TurningPoint],
        category_scores: dict[str, Any],
    ) -> list[DecisionWindow]:
        pivot_times = {tp.local_time for tp in turning_points}
        windows: list[DecisionWindow] = []

        for block in time_blocks:
            has_pivot = any(block.start_local <= pt < block.end_local for pt in pivot_times)
            window_type = self._classify(block, has_pivot)
            if window_type == "neutral":
                continue  # skip noise — AC3: raisonnable et lisible

            score = self._block_score(block, category_scores)
            confidence = self._block_confidence(block, category_scores)
            # AC3: limit to top 2 dominant categories per window
            dominant = list(block.dominant_categories[:2])

            windows.append(
                DecisionWindow(
                    start_local=block.start_local,
                    end_local=block.end_local,
                    window_type=window_type,
                    score=score,
                    confidence=confidence,
                    dominant_categories=dominant,
                )
            )

        return windows

    def _classify(self, block: TimeBlock, has_pivot: bool) -> str:
        if has_pivot:
            return "pivot"
        tone = getattr(block, "tone_code", "neutral")
        if tone == "positive":
            return "favorable"
        if tone in ("negative", "mixed"):
            return "prudence"
        return "neutral"

    def _block_score(self, block: TimeBlock, category_scores: dict[str, Any]) -> float:
        notes: list[float] = []
        for code in list(block.dominant_categories)[:2]:
            s = category_scores.get(code)
            if s is not None:
                note = s.get("note_20", 0) if isinstance(s, dict) else getattr(s, "note_20", 0)
                notes.append(float(note))
        return sum(notes) / len(notes) if notes else 10.0

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
