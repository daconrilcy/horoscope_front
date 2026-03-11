from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING

from app.prediction.contribution_calculator import ContributionCalculator
from app.prediction.domain_router import DomainRouter
from app.prediction.temporal_kernel import spread_event_weights

if TYPE_CHECKING:
    from app.prediction.context_loader import LoadedPredictionContext
    from app.prediction.schemas import AstroEvent, SamplePoint

logger = logging.getLogger(__name__)


class ImpulseSignalBuilder:
    """
    Builder for impulse signal layer E(c,t) in engine v3 (AC1, AC2, AC3).
    Accentuates strong moments (exact hits, ingresses) without carrying the whole narration.
    """

    # Impulse specific caps (AC4)
    MAX_EVENT_CONTRIB = 0.5
    MAX_TOTAL_IMPULSE = 1.0

    def __init__(
        self,
        domain_router: DomainRouter | None = None,
        contribution_calculator: ContributionCalculator | None = None,
    ):
        self._domain_router = domain_router or DomainRouter()
        self._contribution_calculator = contribution_calculator or ContributionCalculator()

    def build_timeline(
        self,
        events: list[AstroEvent],
        samples: list[SamplePoint],
        ns_map: dict[str, float],
        ctx: LoadedPredictionContext,
    ) -> dict[str, dict[datetime, float]]:
        """
        Builds an impulse timeline for each enabled theme (AC3).
        """
        start_perf = time.perf_counter()

        enabled_themes = [
            c.code for c in ctx.prediction_context.categories if c.is_enabled
        ]
        
        # Result: theme_code -> {time: score}
        timeline: dict[str, dict[datetime, float]] = {
            theme: {sample.local_time: 0.0 for sample in samples} 
            for theme in enabled_themes
        }

        # Filter events for E layer (exact hits and major ingresses)
        impulse_events = [
            e for e in events 
            if e.event_type in (
                "aspect_exact_to_angle", 
                "aspect_exact_to_luminary", 
                "aspect_exact_to_personal",
                "moon_sign_ingress"
            )
        ]

        # AC1/AC2 Story 42.5: Convert ns_map to float map for ContributionCalculator (AC6 fix)
        float_ns_map = {
            k: (v.total_score if hasattr(v, "total_score") else float(v))
            for k, v in ns_map.items()
        }

        for event in impulse_events:
            routed_categories = self._domain_router.route(event, ctx)
            contributions = self._contribution_calculator.compute(
                event,
                float_ns_map,
                routed_categories,
                ctx,
            )
            
            # Spread using kernel
            spread = spread_event_weights(event, samples)
            for step_i, weight in spread:
                local_time = samples[step_i].local_time
                for theme_code, contrib in contributions.items():
                    if theme_code in enabled_themes:
                        # Cap individual event contrib to A layer
                        # (Event total might be high in V2, but here it's an accent)
                        clamped_contrib = max(-self.MAX_EVENT_CONTRIB, 
                                            min(self.MAX_EVENT_CONTRIB, contrib))
                        
                        timeline[theme_code][local_time] += clamped_contrib * weight

        # Final per-step capping (AC4)
        for theme in enabled_themes:
            for dt in timeline[theme]:
                timeline[theme][dt] = max(-self.MAX_TOTAL_IMPULSE, 
                                        min(self.MAX_TOTAL_IMPULSE, timeline[theme][dt]))

        duration_ms = (time.perf_counter() - start_perf) * 1000
        logger.info(
            "impulse_signal_built events=%d duration_ms=%.2f",
            len(impulse_events),
            duration_ms
        )
        
        return timeline
