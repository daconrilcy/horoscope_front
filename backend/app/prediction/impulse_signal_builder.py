from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from app.prediction.contribution_calculator import ContributionCalculator
from app.prediction.domain_router import DomainRouter
from app.prediction.temporal_kernel import spread_event_weights

if TYPE_CHECKING:
    from app.prediction.context_loader import LoadedPredictionContext
    from app.prediction.schemas import AstroEvent, SamplePoint

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImpulseSignalBuildResult:
    timeline: dict[str, dict[datetime, float]]
    diagnostics: dict[str, object]


class ImpulseSignalBuilder:
    """
    Builder for impulse signal layer E(c,t) in engine v3.

    The impulse layer must remain a local accent:
    - it only reacts to exact hits and major ingresses kept for product/debug value;
    - it no longer reuses the natal structural baseline as a hidden multiplier;
    - it is gated by the already-existing local regime (T+A), so an isolated exact
      event cannot fabricate a meaningful relief on its own.
    """

    MAX_EVENT_CONTRIB = 0.5
    MAX_TOTAL_IMPULSE = 1.0
    TARGET_BUDGET_MS = 50.0
    SUPPORT_REFERENCE = 0.35
    IMPULSE_EVENT_TYPES = frozenset(
        {
            "aspect_exact_to_angle",
            "aspect_exact_to_luminary",
            "aspect_exact_to_personal",
            "moon_sign_ingress",
        }
    )

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
        _ns_map: dict[str, float],
        ctx: LoadedPredictionContext,
        *,
        support_timelines: dict[str, dict[datetime, float]] | None = None,
    ) -> dict[str, dict[datetime, float]]:
        return self.build(
            events,
            samples,
            _ns_map,
            ctx,
            support_timelines=support_timelines,
        ).timeline

    def build(
        self,
        events: list[AstroEvent],
        samples: list[SamplePoint],
        _ns_map: dict[str, float],
        ctx: LoadedPredictionContext,
        *,
        support_timelines: dict[str, dict[datetime, float]] | None = None,
    ) -> ImpulseSignalBuildResult:
        """
        Builds an impulse timeline for each enabled theme.

        `_ns_map` is kept for API compatibility with the previous builder shape,
        but the impulse layer intentionally does not multiply by B(c).
        """
        start_perf = time.perf_counter()
        enabled_themes = [
            category.code for category in ctx.prediction_context.categories if category.is_enabled
        ]
        timeline: dict[str, dict[datetime, float]] = {
            theme: {sample.local_time: 0.0 for sample in samples} for theme in enabled_themes
        }
        diagnostics = self._initialize_diagnostics(enabled_themes)
        impulse_events = [event for event in events if event.event_type in self.IMPULSE_EVENT_TYPES]
        neutral_ns_map = {theme: 1.0 for theme in enabled_themes}

        for event in impulse_events:
            routed_categories = self._domain_router.route(event, ctx)
            contributions = self._contribution_calculator.compute(
                event,
                neutral_ns_map,
                routed_categories,
                ctx,
            )
            spread = spread_event_weights(event, samples)
            for step_i, weight in spread:
                local_time = samples[step_i].local_time
                for theme_code, contrib in contributions.items():
                    if theme_code not in enabled_themes:
                        continue
                    support_factor = self._support_factor(
                        theme_code,
                        local_time,
                        support_timelines or {},
                    )
                    if support_factor <= 0.0:
                        continue
                    clamped_contrib = max(
                        -self.MAX_EVENT_CONTRIB,
                        min(self.MAX_EVENT_CONTRIB, contrib),
                    )
                    weighted_contrib = clamped_contrib * weight * support_factor
                    timeline[theme_code][local_time] += weighted_contrib
                    self._record_contributor(
                        diagnostics=diagnostics,
                        theme=theme_code,
                        event=event,
                        contribution=weighted_contrib,
                        local_time=local_time,
                        support_factor=support_factor,
                    )

        for theme in enabled_themes:
            for local_time, current_value in timeline[theme].items():
                capped = max(-self.MAX_TOTAL_IMPULSE, min(self.MAX_TOTAL_IMPULSE, current_value))
                timeline[theme][local_time] = capped
                self._record_theme_extrema(diagnostics, theme, capped, local_time)

        duration_ms = (time.perf_counter() - start_perf) * 1000
        diagnostics["performance"] = {
            "budget_target_ms": self.TARGET_BUDGET_MS,
            "sample_count": len(samples),
            "impulse_event_count": len(impulse_events),
        }
        self._finalize_diagnostics(diagnostics)
        logger.info(
            "impulse_signal_built events=%d duration_ms=%.2f AC_budget_ok=%s",
            len(impulse_events),
            duration_ms,
            duration_ms < self.TARGET_BUDGET_MS,
        )
        return ImpulseSignalBuildResult(timeline=timeline, diagnostics=diagnostics)

    def _support_factor(
        self,
        theme_code: str,
        local_time: datetime,
        support_timelines: dict[str, dict[datetime, float]],
    ) -> float:
        theme_timeline = support_timelines.get(theme_code, {})
        support_signal = float(theme_timeline.get(local_time, 0.0))
        if abs(support_signal) < 1e-9:
            return 0.0
        return min(1.0, abs(support_signal) / self.SUPPORT_REFERENCE)

    def _initialize_diagnostics(self, enabled_themes: list[str]) -> dict[str, object]:
        return {
            "themes": {
                theme: {
                    "max_score": None,
                    "max_at": None,
                    "min_score": None,
                    "min_at": None,
                    "contributors": {},
                }
                for theme in enabled_themes
            }
        }

    def _record_contributor(
        self,
        *,
        diagnostics: dict[str, object],
        theme: str,
        event,
        contribution: float,
        local_time: datetime,
        support_factor: float,
    ) -> None:
        theme_diag = diagnostics["themes"][theme]
        contributors = theme_diag["contributors"]
        key = (
            f"{event.event_type}:{event.body or 'None'}:"
            f"{event.target or 'None'}:{event.aspect or 'None'}"
        )
        current = contributors.get(key)
        if current is None or abs(contribution) > current["max_abs_contribution"]:
            contributors[key] = {
                "event_type": event.event_type,
                "body": event.body,
                "target": event.target,
                "aspect": event.aspect,
                "max_abs_contribution": abs(contribution),
                "signed_contribution": contribution,
                "peak_at": local_time.isoformat(),
                "support_factor": support_factor,
            }

    def _record_theme_extrema(
        self,
        diagnostics: dict[str, object],
        theme: str,
        score: float,
        local_time: datetime,
    ) -> None:
        theme_diag = diagnostics["themes"][theme]
        if theme_diag["max_score"] is None or score > theme_diag["max_score"]:
            theme_diag["max_score"] = score
            theme_diag["max_at"] = local_time.isoformat()
        if theme_diag["min_score"] is None or score < theme_diag["min_score"]:
            theme_diag["min_score"] = score
            theme_diag["min_at"] = local_time.isoformat()

    def _finalize_diagnostics(self, diagnostics: dict[str, object]) -> None:
        for theme_diag in diagnostics["themes"].values():
            contributors = list(theme_diag["contributors"].values())
            contributors.sort(key=lambda item: item["max_abs_contribution"], reverse=True)
            theme_diag["top_contributors"] = contributors[:5]
            del theme_diag["contributors"]
