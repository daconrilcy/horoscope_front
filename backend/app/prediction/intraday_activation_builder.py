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
    from app.prediction.temporal_sampler import DayGrid

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntradayActivationBuildResult:
    timeline: dict[str, dict[datetime, float]]
    diagnostics: dict[str, object]


class IntradayActivationBuilder:
    """
    Builder for continuous intraday activation A(c,t) in engine v3.

    The layer reuses event-engine primitives wherever possible:
    - Moon aspects use the same orb, phase, weighting and polarity rules as T(c,t).
    - Secondary modulators (planetary hours, angle sign changes, Moon ingress)
      reuse event taxonomy and weighted theme routing, but remain amplitude-capped
      so they texture the day without behaving like impulse pivots.
    """

    TARGET_BUDGET_MS = 50.0
    PRIMARY_ROLE_MULTIPLIER = 1.0
    SECONDARY_ROLE_MULTIPLIER = 0.6
    SECONDARY_MODULATOR_SCALE = 0.05
    SECONDARY_MODULATOR_CLAMP = 0.20

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
        day_grid: DayGrid | None = None,
        detected_events: list[AstroEvent] | None = None,
    ) -> dict[str, dict[datetime, float]]:
        return self.build(
            steps,
            natal,
            ctx,
            day_grid=day_grid,
            detected_events=detected_events,
        ).timeline

    def build(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
        *,
        day_grid: DayGrid | None = None,
        detected_events: list[AstroEvent] | None = None,
    ) -> IntradayActivationBuildResult:
        """
        Build a continuous activation timeline for each enabled theme.

        Budget (AC6): target < 50ms for 96 steps on a standard day.
        """
        start_perf = time.perf_counter()
        enabled_themes = [
            category.code for category in ctx.prediction_context.categories if category.is_enabled
        ]
        timeline: dict[str, dict[datetime, float]] = {theme: {} for theme in enabled_themes}
        routing_indexes = self._build_weighted_routing(enabled_themes, ctx)
        diagnostics = self._initialize_diagnostics(enabled_themes)

        if not steps:
            diagnostics["performance"] = {
                "budget_target_ms": self.TARGET_BUDGET_MS,
                "sample_count": 0,
                "secondary_event_count": 0,
            }
            self._finalize_diagnostics(diagnostics)
            return IntradayActivationBuildResult(timeline=timeline, diagnostics=diagnostics)

        detector = EventDetector(ctx, natal)
        moon_specs = self._build_moon_specs(natal, detector)
        moon_orb_series = self._build_moon_orb_series(steps, natal)
        secondary_events = self._collect_secondary_events(
            steps=steps,
            natal=natal,
            ctx=ctx,
            day_grid=day_grid,
            detected_events=detected_events,
        )
        secondary_events_by_step = self._bucket_events_by_step(secondary_events, steps)

        for step_index, step in enumerate(steps):
            step_scores = {theme: 0.0 for theme in enabled_themes}
            moon_state = step.planets.get("Moon")

            if moon_state is not None:
                for target_code, target_house, event_type in moon_specs:
                    for aspect_deg, aspect_name in EventDetector.ASPECTS_V1.items():
                        key = (target_code, aspect_deg)
                        orb_series = moon_orb_series[key]
                        orb = orb_series[step_index]
                        orb_max = detector._orb_max("Moon", aspect_name)
                        if orb > orb_max:
                            continue
                        phase = self._resolve_phase(orb_series, step_index)
                        event = self._build_moon_aspect_event(
                            step=step,
                            target_code=target_code,
                            target_house=target_house,
                            transit_house=moon_state.natal_house_transited,
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

                        routed = self._route_v3_weighted(event, enabled_themes, routing_indexes)
                        for theme, route_weight in routed.items():
                            contribution = max(
                                -2.0,
                                min(2.0, base_signal * route_weight),
                            )
                            step_scores[theme] += contribution
                            self._record_contributor(
                                diagnostics=diagnostics,
                                theme=theme,
                                contributor_type="moon_aspect",
                                body_code=event.body or "",
                                target_code=event.target or "",
                                label=event.aspect or "",
                                contribution=contribution,
                                local_time=step.local_time,
                                metadata={
                                    "event_type": event.event_type,
                                    "phase": phase,
                                    "orb_deg": orb,
                                },
                            )

            for event in secondary_events_by_step.get(step_index, []):
                base_signal = self._secondary_modulator_signal(event, ctx)
                if abs(base_signal) < 1e-9:
                    continue
                routed = self._route_secondary_event(event, enabled_themes, routing_indexes)
                for theme, route_weight in routed.items():
                    contribution = max(
                        -self.SECONDARY_MODULATOR_CLAMP,
                        min(
                            self.SECONDARY_MODULATOR_CLAMP,
                            base_signal * route_weight,
                        ),
                    )
                    step_scores[theme] += contribution
                    self._record_contributor(
                        diagnostics=diagnostics,
                        theme=theme,
                        contributor_type="secondary_modulator",
                        body_code=event.body or "",
                        target_code=event.target or "",
                        label=event.event_type,
                        contribution=contribution,
                        local_time=step.local_time,
                        metadata={
                            "event_type": event.event_type,
                            "hour_number": event.metadata.get("hour_number"),
                            "angle_code": event.metadata.get("angle_code"),
                        },
                    )

            for theme in enabled_themes:
                score = max(-2.0, min(2.0, step_scores[theme]))
                timeline[theme][step.local_time] = score
                self._record_theme_extrema(diagnostics, theme, score, step.local_time)

        duration_ms = (time.perf_counter() - start_perf) * 1000
        diagnostics["performance"] = {
            "budget_target_ms": self.TARGET_BUDGET_MS,
            "sample_count": len(steps),
            "secondary_event_count": len(secondary_events),
        }
        self._finalize_diagnostics(diagnostics)
        logger.info(
            "intraday_activation_built steps=%d duration_ms=%.2f AC6_budget_ok=%s",
            len(steps),
            duration_ms,
            duration_ms < self.TARGET_BUDGET_MS,
        )
        return IntradayActivationBuildResult(timeline=timeline, diagnostics=diagnostics)

    def _build_moon_specs(
        self,
        natal: NatalChart,
        detector: EventDetector,
    ) -> list[tuple[str, int | None, str]]:
        return [
            (
                target_code,
                natal.planet_houses.get(target_code),
                detector._discriminate_exact_code(target_code),
            )
            for target_code in natal.planet_positions
        ]

    def _build_moon_orb_series(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
    ) -> dict[tuple[str, int], list[float]]:
        series: dict[tuple[str, int], list[float]] = {}
        for step in steps:
            moon = step.planets.get("Moon")
            if moon is None:
                continue
            for target_code, natal_lon in natal.planet_positions.items():
                diff = abs(moon.longitude - natal_lon) % 360
                if diff > 180:
                    diff = 360 - diff
                for aspect_deg in EventDetector.ASPECTS_V1:
                    series.setdefault((target_code, aspect_deg), []).append(abs(diff - aspect_deg))
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

    def _build_moon_aspect_event(
        self,
        *,
        step: StepAstroState,
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
            body="Moon",
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

    def _collect_secondary_events(
        self,
        *,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
        day_grid: DayGrid | None,
        detected_events: list[AstroEvent] | None,
    ) -> list[AstroEvent]:
        secondary_events = list(
            detected_events
            if detected_events is not None
            else self._detect_secondary_events(steps, natal, ctx, day_grid)
        )
        secondary_events = [
            self._enrich_secondary_event(event, steps)
            for event in secondary_events
            if event.event_type in {"planetary_hour_change", "asc_sign_change"}
        ]
        secondary_events.extend(self._detect_mc_sign_changes(steps, ctx))
        secondary_events.sort(key=lambda event: event.local_time)
        return secondary_events

    def _detect_secondary_events(
        self,
        steps: list[StepAstroState],
        natal: NatalChart,
        ctx: LoadedPredictionContext,
        day_grid: DayGrid | None,
    ) -> list[AstroEvent]:
        if day_grid is None:
            detected = EventDetector(ctx, natal)._detect_moon_ingress(steps)
            detected.extend(EventDetector(ctx, natal)._detect_asc_sign_change(steps))
            return detected
        return EventDetector(ctx, natal).detect(steps, day_grid)

    def _enrich_secondary_event(
        self,
        event: AstroEvent,
        steps: list[StepAstroState],
    ) -> AstroEvent:
        metadata = dict(event.metadata)
        if event.event_type == "asc_sign_change":
            metadata.setdefault("angle_code", event.body or "Asc")
            metadata.setdefault("natal_house_target", 1)
            metadata.setdefault("natal_house_transited", 1)
        return AstroEvent(
            event_type=event.event_type,
            ut_time=event.ut_time,
            local_time=event.local_time,
            body=event.body,
            target=event.target,
            aspect=event.aspect,
            orb_deg=event.orb_deg,
            priority=event.priority,
            base_weight=event.base_weight,
            metadata=metadata,
        )

    def _detect_mc_sign_changes(
        self,
        steps: list[StepAstroState],
        ctx: LoadedPredictionContext,
    ) -> list[AstroEvent]:
        detected: list[AstroEvent] = []
        prev_sign: int | None = None
        event_type_data = ctx.ruleset_context.event_types.get("asc_sign_change")

        for step in steps:
            sign_code = int(step.mc_deg // 30)
            if prev_sign is not None and sign_code != prev_sign:
                detected.append(
                    AstroEvent(
                        event_type="asc_sign_change",
                        ut_time=step.ut_jd,
                        local_time=step.local_time,
                        body="MC",
                        target=None,
                        aspect=None,
                        orb_deg=0.0,
                        priority=int(getattr(event_type_data, "priority", 50) or 50),
                        base_weight=float(getattr(event_type_data, "base_weight", 1.0) or 1.0),
                        metadata={
                            "from_sign": prev_sign,
                            "to_sign": sign_code,
                            "angle_code": "MC",
                            "natal_house_target": 10,
                            "natal_house_transited": 10,
                        },
                    )
                )
            prev_sign = sign_code

        return detected

    def _bucket_events_by_step(
        self,
        events: list[AstroEvent],
        steps: list[StepAstroState],
    ) -> dict[int, list[AstroEvent]]:
        buckets: dict[int, list[AstroEvent]] = {}
        for event in events:
            step_index = min(
                range(len(steps)),
                key=lambda index: abs(steps[index].ut_jd - event.ut_time),
            )
            buckets.setdefault(step_index, []).append(event)
        return buckets

    def _secondary_modulator_signal(
        self,
        event: AstroEvent,
        ctx: LoadedPredictionContext,
    ) -> float:
        return (
            self.SECONDARY_MODULATOR_SCALE
            * self._contribution_calculator._w_event(event)
            * self._contribution_calculator._w_planet(event.body, ctx)
            * self._secondary_modulator_polarity(event.body, ctx)
        )

    def _secondary_modulator_polarity(
        self,
        body_code: str | None,
        ctx: LoadedPredictionContext,
    ) -> float:
        if body_code is None:
            return 1.0
        planet_profile = self._lookup_mapping_value(
            ctx.prediction_context.planet_profiles,
            body_code,
        )
        if planet_profile is None:
            return 1.0
        polarity = str(getattr(planet_profile, "typical_polarity", "") or "").strip().lower()
        if polarity == "negative":
            return -1.0
        if polarity == "positive":
            return 1.0
        return 0.5

    def _build_weighted_routing(
        self,
        enabled_themes: list[str],
        ctx: LoadedPredictionContext,
    ) -> dict[str, dict[str, dict[object, float]]]:
        theme_planets: dict[str, dict[str, float]] = {theme: {} for theme in enabled_themes}
        theme_houses: dict[str, dict[int, float]] = {theme: {} for theme in enabled_themes}
        theme_points: dict[str, dict[str, float]] = {theme: {} for theme in enabled_themes}

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

        for weight in getattr(ctx.prediction_context, "point_category_weights", ()):
            if weight.category_code not in theme_points or weight.weight <= 0:
                continue
            theme_points[weight.category_code][weight.point_code.lower()] = float(weight.weight)

        return {"planets": theme_planets, "houses": theme_houses, "points": theme_points}

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
            if body_code in {"asc", "mc"}:
                point_weight = routing_indexes["points"][theme].get(body_code, 0.0)
                route_weight = max(house_projection, point_weight)
            else:
                planet_blend = 0.50 + 0.50 * planet_weight
                route_weight = house_projection * planet_blend if house_vector else planet_blend

            if route_weight > 0.0:
                routed[theme] = route_weight

        return routed

    def _route_secondary_event(
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

            if body_code in {"asc", "mc"}:
                point_weight = routing_indexes["points"][theme].get(body_code, 0.0)
                route_weight = max(house_projection, point_weight)
            elif house_vector:
                planet_weight = routing_indexes["planets"][theme].get(body_code, 0.0)
                route_weight = house_projection * (0.50 + 0.50 * planet_weight)
            else:
                route_weight = routing_indexes["planets"][theme].get(body_code, 0.0)

            if route_weight > 0.0:
                routed[theme] = route_weight

        return routed

    def _role_multiplier(self, raw_role: str | None) -> float:
        if raw_role is None:
            return self.PRIMARY_ROLE_MULTIPLIER
        role = raw_role.strip().lower()
        if role == "secondary":
            return self.SECONDARY_ROLE_MULTIPLIER
        return self.PRIMARY_ROLE_MULTIPLIER

    def _lookup_mapping_value(self, mapping: dict | None, key: object) -> object | None:
        if mapping is None:
            return None
        if not isinstance(key, str):
            candidates = (key,)
        else:
            candidates = (key, key.lower(), key.upper(), key.title())
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
        return None

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
        contributor_type: str,
        body_code: str,
        target_code: str,
        label: str,
        contribution: float,
        local_time: datetime,
        metadata: dict[str, object],
    ) -> None:
        theme_diag = diagnostics["themes"][theme]
        contributors = theme_diag["contributors"]
        key = f"{contributor_type}:{body_code}->{target_code}:{label}"
        current = contributors.get(key)
        if current is None or abs(contribution) > current["max_abs_contribution"]:
            contributors[key] = {
                "type": contributor_type,
                "body": body_code,
                "target": target_code or None,
                "label": label,
                "max_abs_contribution": abs(contribution),
                "signed_contribution": contribution,
                "peak_at": local_time.isoformat(),
                **metadata,
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
