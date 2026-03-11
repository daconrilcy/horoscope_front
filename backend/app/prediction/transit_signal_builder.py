from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from app.prediction.contribution_calculator import ContributionCalculator
from app.prediction.domain_router import DomainRouter
from app.prediction.event_detector import EventDetector
from app.prediction.schemas import AstroEvent

if TYPE_CHECKING:
    from app.prediction.context_loader import LoadedPredictionContext
    from app.prediction.schemas import NatalChart, StepAstroState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitSignalBuildResult:
    timeline: dict[str, dict[datetime, float]]
    diagnostics: dict[str, object]


class TransitSignalBuilder:
    """
    Builder for continuous transit signal T(c,t) in engine v3 (AC1, AC2, AC3).

    The continuous layer deliberately reuses the same orb, polarity and weighting
    primitives as the event-based engine. The only v3-specific part is the
    continuous sampling and weighted theme routing.
    """

    TARGET_BUDGET_MS = 100.0
    PRIMARY_ROLE_MULTIPLIER = 1.0
    SECONDARY_ROLE_MULTIPLIER = 0.6

    def __init__(
        self,
        contribution_calculator: ContributionCalculator | None = None,
        domain_router: DomainRouter | None = None,
    ) -> None:
        self._contribution_calculator = contribution_calculator or ContributionCalculator()
        self._domain_router = domain_router or DomainRouter()

    def build_timeline(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
    ) -> dict[str, dict[datetime, float]]:
        return self.build(steps, natal, ctx).timeline

    def build(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
    ) -> TransitSignalBuildResult:
        """
        Builds a continuous transit signal timeline for each enabled theme.

        Budget (AC6): target < 100ms for 96 steps on a standard day.
        """
        start_perf = time.perf_counter()
        detector = EventDetector(ctx, natal)
        enabled_themes = [
            category.code for category in ctx.prediction_context.categories if category.is_enabled
        ]
        timeline: dict[str, dict[datetime, float]] = {theme: {} for theme in enabled_themes}
        routing_indexes = self._build_weighted_routing(enabled_themes, ctx)
        orb_series = self._build_orb_series(steps, natal)
        target_specs = [
            (
                target_code,
                natal_lon,
                natal.planet_houses.get(target_code),
                detector._discriminate_exact_code(target_code),
            )
            for target_code, natal_lon in natal.planet_positions.items()
        ]
        orb_max_cache: dict[tuple[str, str], float] = {}
        diagnostics = self._initialize_diagnostics(enabled_themes)

        for step_index, step in enumerate(steps):
            step_scores = {theme: 0.0 for theme in enabled_themes}

            for body_code, planet_state in step.planets.items():
                for target_code, _natal_lon, target_house, event_type in target_specs:
                    for aspect_deg, aspect_name in EventDetector.ASPECTS_V1.items():
                        key = (body_code, target_code, aspect_deg)
                        orb = orb_series[key][step_index]
                        orb_max = orb_max_cache.setdefault(
                            (body_code, aspect_name),
                            detector._orb_max(body_code, aspect_name),
                        )
                        if orb > orb_max:
                            continue
                        phase = self._resolve_phase(orb_series[key], step_index)
                        event = self._build_synthetic_event(
                            step=step,
                            body_code=body_code,
                            target_code=target_code,
                            target_house=target_house,
                            transit_house=planet_state.natal_house_transited,
                            aspect_name=aspect_name,
                            event_type=event_type,
                            orb=orb,
                            orb_max=orb_max,
                            phase=phase,
                            ctx=ctx,
                        )
                        base_signal = self._continuous_base_signal(event, ctx)
                        if abs(base_signal) < 1e-9:
                            continue

                        routed = self._route_v3_weighted(
                            event,
                            enabled_themes,
                            routing_indexes,
                        )
                        for theme, route_weight in routed.items():
                            contribution = max(-2.0, min(2.0, base_signal * route_weight))
                            step_scores[theme] += contribution
                            self._record_contributor(
                                diagnostics=diagnostics,
                                theme=theme,
                                body_code=body_code,
                                target_code=target_code,
                                aspect_name=aspect_name,
                                contribution=contribution,
                                local_time=step.local_time,
                                phase=phase,
                                orb=orb,
                                event_type=event_type,
                            )

            for theme in enabled_themes:
                score = max(-2.0, min(2.0, step_scores[theme]))
                timeline[theme][step.local_time] = score
                self._record_theme_extrema(diagnostics, theme, score, step.local_time)

        duration_ms = (time.perf_counter() - start_perf) * 1000
        diagnostics["performance"] = {
            "budget_target_ms": self.TARGET_BUDGET_MS,
            "sample_count": len(steps),
        }
        self._finalize_diagnostics(diagnostics)
        logger.info(
            "transit_signal_built steps=%d duration_ms=%.2f AC6_budget_ok=%s",
            len(steps),
            duration_ms,
            duration_ms < self.TARGET_BUDGET_MS,
        )
        return TransitSignalBuildResult(timeline=timeline, diagnostics=diagnostics)

    def _build_weighted_routing(
        self,
        enabled_themes: list[str],
        ctx: LoadedPredictionContext,
    ) -> dict[str, dict[str, dict[object, float]]]:
        theme_planets: dict[str, dict[str, float]] = {theme: {} for theme in enabled_themes}
        theme_houses: dict[str, dict[int, float]] = {theme: {} for theme in enabled_themes}

        for weight in ctx.prediction_context.planet_category_weights:
            if weight.category_code not in theme_planets or weight.weight <= 0:
                continue
            role_factor = self._role_multiplier(getattr(weight, "influence_role", None))
            theme_planets[weight.category_code][weight.planet_code.lower()] = (
                float(weight.weight) * role_factor
            )

        for weight in ctx.prediction_context.house_category_weights:
            if weight.category_code not in theme_houses or weight.weight <= 0:
                continue
            role_factor = self._role_multiplier(getattr(weight, "routing_role", None))
            theme_houses[weight.category_code][weight.house_number] = (
                float(weight.weight) * role_factor
            )

        return {"planets": theme_planets, "houses": theme_houses}

    def _build_orb_series(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
    ) -> dict[tuple[str, str, int], list[float]]:
        series: dict[tuple[str, str, int], list[float]] = {}
        for step in steps:
            for body_code, planet_state in step.planets.items():
                for target_code, natal_lon in natal.planet_positions.items():
                    diff = abs(planet_state.longitude - natal_lon) % 360
                    if diff > 180:
                        diff = 360 - diff
                    for aspect_deg in EventDetector.ASPECTS_V1:
                        series.setdefault((body_code, target_code, aspect_deg), []).append(
                            abs(diff - aspect_deg)
                        )
        return series

    def _resolve_phase(self, orbs: list[float], index: int) -> str:
        current = orbs[index]
        prev_orb = orbs[index - 1] if index > 0 else None
        next_orb = orbs[index + 1] if index + 1 < len(orbs) else None

        if prev_orb is not None and next_orb is not None:
            if current < prev_orb and current <= next_orb:
                return "applying"
            if current > prev_orb and current >= next_orb:
                return "separating"
        if next_orb is not None:
            return "applying" if next_orb < current else "separating"
        if prev_orb is not None:
            return "applying" if current < prev_orb else "separating"
        return "exact"

    def _build_synthetic_event(
        self,
        *,
        step: StepAstroState,
        body_code: str,
        target_code: str,
        target_house: int | None,
        transit_house: int | None,
        aspect_name: str,
        event_type: str,
        orb: float,
        orb_max: float,
        phase: str,
        ctx: LoadedPredictionContext,
    ) -> AstroEvent:
        event_type_data = ctx.ruleset_context.event_types.get(event_type)
        return AstroEvent(
            event_type=event_type,
            ut_time=step.ut_jd,
            local_time=step.local_time,
            body=body_code,
            target=target_code,
            aspect=aspect_name,
            orb_deg=orb,
            priority=int(getattr(event_type_data, "priority", 50) or 50),
            base_weight=float(getattr(event_type_data, "base_weight", 1.0) or 1.0),
            metadata={
                "orb_max": orb_max,
                "phase": phase,
                "natal_house_target": target_house,
                "natal_house_transited": transit_house,
            },
        )

    def _continuous_base_signal(
        self,
        event: AstroEvent,
        ctx: LoadedPredictionContext,
    ) -> float:
        if self._contribution_calculator._f_orb(event, ctx) <= 0.0:
            return 0.0

        return (
            self._contribution_calculator._w_event(event)
            * self._contribution_calculator._w_planet(event.body, ctx)
            * self._contribution_calculator._w_aspect(event.aspect, ctx)
            * self._contribution_calculator._f_orb(event, ctx)
            * self._contribution_calculator._f_phase(event)
            * self._contribution_calculator._f_target(event.target)
            * self._contribution_calculator._pol(event, "_continuous_", ctx)
        )

    def _route_v3_weighted(
        self,
        event: AstroEvent,
        enabled_themes: list[str],
        routing_indexes: dict[str, dict[str, dict[object, float]]],
    ) -> dict[str, float]:
        house_vector = self._domain_router._build_house_vector(event)
        body_code = (event.body or "").lower()
        routed: dict[str, float] = {}

        for theme in enabled_themes:
            house_projection = 0.0
            for house_num, vector_weight in house_vector.items():
                house_projection += (
                    vector_weight * routing_indexes["houses"][theme].get(house_num, 0.0)
                )

            planet_weight = routing_indexes["planets"][theme].get(body_code, 0.0)
            planet_blend = 0.50 + 0.50 * planet_weight
            route_weight = house_projection * planet_blend if house_vector else planet_blend
            if route_weight > 0.0:
                routed[theme] = route_weight

        return routed

    def _role_multiplier(self, raw_role: str | None) -> float:
        if raw_role is None:
            return self.PRIMARY_ROLE_MULTIPLIER
        role = raw_role.strip().lower()
        if role == "primary":
            return self.PRIMARY_ROLE_MULTIPLIER
        if role == "secondary":
            return self.SECONDARY_ROLE_MULTIPLIER
        return self.PRIMARY_ROLE_MULTIPLIER

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
        body_code: str,
        target_code: str,
        aspect_name: str,
        contribution: float,
        local_time: datetime,
        phase: str,
        orb: float,
        event_type: str,
    ) -> None:
        theme_diag = diagnostics["themes"][theme]
        contributors = theme_diag["contributors"]
        key = f"{body_code}->{target_code}:{aspect_name}"
        current = contributors.get(key)
        if current is None or abs(contribution) > current["max_abs_contribution"]:
            contributors[key] = {
                "body": body_code,
                "target": target_code,
                "aspect": aspect_name,
                "event_type": event_type,
                "max_abs_contribution": abs(contribution),
                "signed_contribution": contribution,
                "peak_at": local_time.isoformat(),
                "phase": phase,
                "orb_deg": orb,
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
            theme_diag["top_contributors"] = contributors[:3]
            del theme_diag["contributors"]
