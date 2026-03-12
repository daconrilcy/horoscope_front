from __future__ import annotations

import logging
from datetime import UTC
from typing import TYPE_CHECKING, Any

from .schemas import (
    V3EvidencePack,
    V3EvidenceTheme,
    V3EvidenceTurningPoint,
    V3EvidenceWindow,
)

if TYPE_CHECKING:
    from .schemas import V3EngineOutput

logger = logging.getLogger(__name__)


class DailyPredictionEvidenceBuilder:
    """
    Synthesizes the V3 Evidence Pack from engine outputs (Story 42.15).
    Provides a stable, expert source of truth for interpretation and projection.
    """

    def build(self, v3_output: V3EngineOutput) -> V3EvidencePack:
        """
        Builds a complete evidence pack from V3 engine results.
        """
        # 1. Day Profile (Global metrics)
        day_profile = self._build_day_profile(v3_output)

        # 2. Themes (Detailed metrics per theme)
        themes = {
            code: V3EvidenceTheme(
                code=code,
                score_20=m.score_20,
                level=m.level_day,
                intensity=m.intensity_day,
                dominance=m.dominance_day,
                stability=m.stability_day,
                rarity=m.rarity_percentile,
                is_major=m.score_20 > 12.0 or m.score_20 < 8.0,
            )
            for code, m in v3_output.daily_metrics.items()
        }

        # 3. Time Windows (Actionable segments)
        time_windows = [
            V3EvidenceWindow(
                start_local=w.start_local,
                end_local=w.end_local,
                type=w.window_type,
                score=w.score,
                intensity=w.intensity or 0.0,
                confidence=w.confidence,
                themes=w.dominant_categories,
            )
            for w in v3_output.decision_windows
        ]

        # 4. Turning Points (Pivots and shifts)
        turning_points = [
            V3EvidenceTurningPoint(
                local_time=tp.local_time,
                reason=tp.reason,
                amplitude=tp.amplitude,
                confidence=tp.confidence,
                themes=tp.categories_impacted,
                drivers=[self._format_driver(d) for d in tp.drivers],
                # Story 43.1
                change_type=tp.change_type,
                previous_categories=tp.previous_categories,
                next_categories=tp.next_categories,
                primary_driver=tp.primary_driver,
            )
            for tp in v3_output.turning_points
        ]

        run_meta = v3_output.run_metadata or {}

        return V3EvidencePack(
            version=v3_output.evidence_pack_version,
            generated_at=v3_output.computed_at.astimezone(UTC),
            day_profile=day_profile,
            themes=themes,
            time_windows=time_windows,
            turning_points=turning_points,
            v3_natal_structural=run_meta.get("v3_natal_structural", {}),
            v3_layer_diagnostics={
                "transit": run_meta.get("v3_transit_signal"),
                "aspect": run_meta.get("v3_intraday_activation"),
                "event": run_meta.get("v3_impulse_signal"),
            },
            metadata=v3_output.run_metadata,
        )

    def _build_day_profile(self, v3_output: V3EngineOutput) -> dict[str, Any]:
        """Synthesizes global day characteristics."""
        all_metrics = list(v3_output.daily_metrics.values())
        if not all_metrics:
            return {
                "tone": "unknown",
                "intensity": 0.0,
                "local_date": self._resolve_local_date(v3_output),
            }

        avg_score = sum(m.score_20 for m in all_metrics) / len(all_metrics)
        avg_intensity = sum(m.intensity_day for m in all_metrics) / len(all_metrics)
        avg_stability = sum(m.stability_day for m in all_metrics) / len(all_metrics)

        return {
            "local_date": self._resolve_local_date(v3_output),
            "tone": self._derive_tone(avg_score),
            "avg_score": round(avg_score, 2),
            "avg_intensity": round(avg_intensity, 2),
            "avg_stability": round(avg_stability, 2),
            "is_calm": avg_intensity < 5.0,
            "is_unstable": avg_stability < 10.0,
            "block_count": len(v3_output.time_blocks),
            "pivot_count": len(v3_output.turning_points),
        }

    def _resolve_local_date(self, v3_output: V3EngineOutput) -> str | None:
        if v3_output.time_blocks:
            return v3_output.time_blocks[0].start_local.date().isoformat()
        if v3_output.decision_windows:
            return v3_output.decision_windows[0].start_local.date().isoformat()
        if v3_output.turning_points:
            return v3_output.turning_points[0].local_time.date().isoformat()
        for theme_signal in v3_output.theme_signals.values():
            if theme_signal.timeline:
                first_local = min(theme_signal.timeline)
                return first_local.date().isoformat()
        return None

    def _derive_tone(self, avg_score: float) -> str:
        if avg_score >= 13.0:
            return "positive"
        if avg_score <= 7.0:
            return "negative"
        return "neutral"

    def _format_driver(self, event: Any) -> str:
        """Deterministic string representation of an astrological driver."""
        body = event.body or "unknown"
        target = event.target or ""
        aspect = event.aspect or "ingress"
        return f"{body}-{aspect}-{target}".strip("-")
