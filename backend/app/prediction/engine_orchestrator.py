from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from numbers import Real
from types import SimpleNamespace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app.core.config import DailyEngineMode, settings
from app.infra.db.repositories.prediction_schemas import RulesetContext

from .aggregator import TemporalAggregator, V3ThemeAggregator
from .astro_calculator import AstroCalculator
from .block_generator import BlockGenerator
from .calibrator import PercentileCalibrator
from .category_codes import normalize_category_codes
from .context_loader import LoadedPredictionContext
from .contribution_calculator import ContributionCalculator
from .decision_window_builder import DecisionWindowBuilder
from .domain_router import DomainRouter
from .editorial_builder import EditorialOutputBuilder
from .editorial_service import PredictionEditorialService
from .event_detector import EventDetector
from .exceptions import PredictionContextError
from .explainability import ExplainabilityBuilder
from .impulse_signal_builder import ImpulseSignalBuilder
from .input_hash import compute_engine_input_hash
from .intraday_activation_builder import IntradayActivationBuilder
from .natal_sensitivity import NatalSensitivityCalculator
from .schemas import (
    AstroEvent,
    CoreEngineOutput,
    EffectiveContext,
    EngineInput,
    NatalChart,
    PersistablePredictionBundle,
    SamplePoint,
    V3DailyMetrics,
    V3EngineOutput,
    V3SignalLayer,
    V3ThemeSignal,
)
from .temporal_kernel import spread_event_weights
from .temporal_sampler import DayGrid, TemporalSampler
from .transit_signal_builder import TransitSignalBuilder
from .turning_point_detector import TurningPointDetector

_ZODIAC_SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

_PLANET_NAME_MAP = {
    "sun": "Sun",
    "moon": "Moon",
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
}


class EngineOrchestrator:
    """Orchestrates the prediction engine run."""

    def __init__(
        self,
        ruleset_context_loader: Callable[[str], RulesetContext | None] | None = None,
        prediction_context_loader: (
            Callable[[str, str, date], LoadedPredictionContext | None] | None
        ) = None,
        temporal_sampler: TemporalSampler | None = None,
        astro_calculator_factory: (
            Callable[[list[float], float, float], AstroCalculator] | None
        ) = None,
        event_detector_factory: (
            Callable[[LoadedPredictionContext, NatalChart], EventDetector] | None
        ) = None,
        natal_sensitivity_calculator: NatalSensitivityCalculator | None = None,
        domain_router: DomainRouter | None = None,
        contribution_calculator: ContributionCalculator | None = None,
        temporal_aggregator: TemporalAggregator | None = None,
        percentile_calibrator: PercentileCalibrator | None = None,
        turning_point_detector: TurningPointDetector | None = None,
        block_generator: BlockGenerator | None = None,
        explainability_builder: ExplainabilityBuilder | None = None,
        editorial_service: PredictionEditorialService | None = None,
        decision_window_builder: DecisionWindowBuilder | None = None,
        transit_signal_builder: TransitSignalBuilder | None = None,
        intraday_activation_builder: IntradayActivationBuilder | None = None,
        impulse_signal_builder: ImpulseSignalBuilder | None = None,
        v3_theme_aggregator: V3ThemeAggregator | None = None,
    ) -> None:
        self._ruleset_context_loader = ruleset_context_loader
        self._prediction_context_loader = prediction_context_loader
        self._temporal_sampler = temporal_sampler or TemporalSampler()
        self._astro_calculator_factory = astro_calculator_factory or AstroCalculator
        self._event_detector_factory = event_detector_factory or EventDetector
        self._natal_sensitivity_calculator = (
            natal_sensitivity_calculator or NatalSensitivityCalculator()
        )
        self._domain_router = domain_router or DomainRouter()
        self._contribution_calculator = contribution_calculator or ContributionCalculator()
        self._temporal_aggregator = temporal_aggregator or TemporalAggregator()
        self._percentile_calibrator = percentile_calibrator or PercentileCalibrator()
        self._turning_point_detector = turning_point_detector or TurningPointDetector()
        self._block_generator = block_generator or BlockGenerator()
        self._explainability_builder = explainability_builder or ExplainabilityBuilder()
        self._editorial_service = editorial_service or PredictionEditorialService()
        self._decision_window_builder = decision_window_builder or DecisionWindowBuilder()
        self._transit_signal_builder = (
            transit_signal_builder or TransitSignalBuilder(self._contribution_calculator)
        )
        self._intraday_activation_builder = (
            intraday_activation_builder or IntradayActivationBuilder(self._contribution_calculator)
        )
        self._impulse_signal_builder = (
            impulse_signal_builder or ImpulseSignalBuilder(
                self._domain_router, self._contribution_calculator
            )
        )
        self._v3_theme_aggregator = v3_theme_aggregator or V3ThemeAggregator()

    def with_context_loader(
        self,
        prediction_context_loader: "Callable[[str, str, date], LoadedPredictionContext | None]",
    ) -> "EngineOrchestrator":
        """Return a new orchestrator with a fresh context loader."""
        return EngineOrchestrator(
            prediction_context_loader=prediction_context_loader,
            temporal_sampler=self._temporal_sampler,
            astro_calculator_factory=self._astro_calculator_factory,
            event_detector_factory=self._event_detector_factory,
            natal_sensitivity_calculator=self._natal_sensitivity_calculator,
            domain_router=self._domain_router,
            contribution_calculator=self._contribution_calculator,
            temporal_aggregator=self._temporal_aggregator,
            percentile_calibrator=self._percentile_calibrator,
            turning_point_detector=self._turning_point_detector,
            block_generator=self._block_generator,
            explainability_builder=self._explainability_builder,
            editorial_service=self._editorial_service,
            decision_window_builder=self._decision_window_builder,
            transit_signal_builder=self._transit_signal_builder,
            intraday_activation_builder=self._intraday_activation_builder,
            impulse_signal_builder=self._impulse_signal_builder,
            v3_theme_aggregator=self._v3_theme_aggregator,
        )

    def run(
        self,
        engine_input: EngineInput,
        *,
        category_codes: tuple[str, ...] | None = None,
        include_editorial: bool = True,
        include_editorial_text: bool = False,
        editorial_text_lang: str = "fr",
        engine_mode: DailyEngineMode = DailyEngineMode.V2,
    ) -> PersistablePredictionBundle:
        """
        Executes the prediction engine for a given input and returns a complete bundle.
        """
        mode = DailyEngineMode(engine_mode)
        v3_versions = self._resolve_v3_versions(mode)

        input_hash = compute_engine_input_hash(
            natal_chart=engine_input.natal_chart,
            local_date=engine_input.local_date,
            timezone=engine_input.timezone,
            latitude=engine_input.latitude,
            longitude=engine_input.longitude,
            reference_version=engine_input.reference_version,
            ruleset_version=engine_input.ruleset_version,
            engine_mode=mode.value,
            engine_version=v3_versions["engine_version"],
            snapshot_version=v3_versions["snapshot_version"],
            evidence_pack_version=v3_versions["evidence_pack_version"],
        )
        jd_start, jd_end = self._local_date_to_ut_interval(
            engine_input.local_date, engine_input.timezone
        )
        loaded_context = self._load_prediction_context(engine_input)
        house_system_requested = self._resolve_house_system(
            engine_input.ruleset_version,
            loaded_context,
        )
        natal_cusps = self._extract_house_cusps(engine_input.natal_chart)
        natal_chart = self._build_natal_chart(engine_input.natal_chart, natal_cusps, loaded_context)
        day_grid = self._temporal_sampler.build_day_grid(
            engine_input.local_date,
            engine_input.timezone,
            engine_input.latitude,
            engine_input.longitude,
        )
        astro_calculator = self._astro_calculator_factory(
            natal_cusps,
            engine_input.latitude,
            engine_input.longitude,
        )
        astro_states = [
            astro_calculator.compute_step(sample.ut_time, sample.local_time)
            for sample in day_grid.samples
        ]
        event_detector = self._event_detector_factory(loaded_context, natal_chart)
        detected_events = event_detector.detect(astro_states, day_grid)
        detected_events = self._refine_detected_events(
            detected_events,
            astro_calculator,
            event_detector,
            engine_input.timezone,
        )
        house_system_effective = self._resolve_effective_house_system(
            house_system_requested,
            astro_states,
        )
        effective_context = EffectiveContext(
            house_system_requested=house_system_requested,
            house_system_effective=house_system_effective,
            local_date=engine_input.local_date,
            timezone=engine_input.timezone,
            input_hash=input_hash,
        )
        run_metadata = self._build_run_metadata(
            engine_input=engine_input,
            loaded_context=loaded_context,
            jd_start=jd_start,
            jd_end=jd_end,
            engine_mode=mode,
            v3_versions=v3_versions,
        )

        v3_core = None
        if mode in (DailyEngineMode.V3, DailyEngineMode.DUAL):
            v3_core = self._build_v3_core(
                astro_states=astro_states,
                natal_chart=natal_chart,
                loaded_context=loaded_context,
                detected_events=detected_events,
                samples=day_grid.samples,
                local_date=engine_input.local_date,
                timezone=engine_input.timezone,
                engine_mode=mode,
                v3_versions=v3_versions,
            )

        if mode == DailyEngineMode.V3:
            core_output = self._build_v3_legacy_core(
                effective_context=effective_context,
                run_metadata=run_metadata,
                detected_events=detected_events,
                samples=day_grid.samples,
                loaded_context=loaded_context,
                v3_core=v3_core,
            )
        else:
            core_output = self._build_v2_core_output(
                input_hash=input_hash,
                engine_input=engine_input,
                detected_events=detected_events,
                samples=day_grid.samples,
                natal_chart=natal_chart,
                loaded_context=loaded_context,
                requested_category_codes=category_codes,
                effective_context=effective_context,
                run_metadata=run_metadata,
            )

        if not include_editorial:
            return PersistablePredictionBundle(core=core_output, v3_core=v3_core)

        # AC1 - EditorialOutputBundle (Textes et résumés) via AC3 - PredictionEditorialService
        editorial_bundle = self._editorial_service.generate_bundle(
            core_output, lang=editorial_text_lang
        )

        # AC1 - PersistablePredictionBundle (Prêt à sauvegarder)
        return PersistablePredictionBundle(
            core=core_output,
            editorial=editorial_bundle,
            v3_core=v3_core,
        )

    def _resolve_v3_versions(self, engine_mode: DailyEngineMode) -> dict[str, str | None]:
        if engine_mode == DailyEngineMode.V2:
            return {
                "engine_version": None,
                "snapshot_version": None,
                "evidence_pack_version": None,
            }
        return {
            "engine_version": settings.v3_engine_version,
            "snapshot_version": settings.v3_snapshot_version,
            "evidence_pack_version": settings.v3_evidence_pack_version,
        }

    def _build_run_metadata(
        self,
        *,
        engine_input: EngineInput,
        loaded_context: LoadedPredictionContext,
        jd_start: float,
        jd_end: float,
        engine_mode: DailyEngineMode,
        v3_versions: dict[str, str | None],
    ) -> dict[str, object]:
        return {
            "run_id": None,
            "computed_at": self._local_date_start_utc(
                engine_input.local_date, engine_input.timezone
            ).isoformat(),
            "debug_mode": engine_input.debug_mode,
            "jd_interval": [jd_start, jd_end],
            "is_provisional_calibration": loaded_context.is_provisional_calibration,
            "calibration_label": loaded_context.calibration_label,
            "caution_category_codes": self._resolve_caution_category_codes(loaded_context),
            "engine_mode": engine_mode.value,
            "engine_version": v3_versions["engine_version"],
            "snapshot_version": v3_versions["snapshot_version"],
            "evidence_pack_version": v3_versions["evidence_pack_version"],
        }

    def _build_v3_core(
        self,
        *,
        astro_states: list,
        natal_chart: NatalChart,
        loaded_context: LoadedPredictionContext,
        detected_events: list[AstroEvent],
        samples: list[SamplePoint],
        local_date: date,
        timezone: str,
        engine_mode: DailyEngineMode,
        v3_versions: dict[str, str | None],
    ) -> V3EngineOutput:
        b_map = self._natal_sensitivity_calculator.compute_v3(natal_chart, loaded_context)
        transit_layer = self._transit_signal_builder.build(
            astro_states, natal_chart, loaded_context
        )
        t_timelines = transit_layer.timeline
        intraday_layer = self._intraday_activation_builder.build(
            astro_states,
            natal_chart,
            loaded_context,
            day_grid=self._build_day_grid_from_samples(samples, local_date, timezone),
            detected_events=detected_events,
        )
        a_timelines = intraday_layer.timeline
        e_timelines = self._impulse_signal_builder.build_timeline(
            detected_events, samples, b_map, loaded_context
        )

        theme_signals: dict[str, V3ThemeSignal] = {}
        for theme_code, b_out in b_map.items():
            t_timeline = t_timelines.get(theme_code, {})
            a_timeline = a_timelines.get(theme_code, {})
            e_timeline = e_timelines.get(theme_code, {})
            timeline: dict[datetime, V3SignalLayer] = {}
            for sample in samples:
                t_val = t_timeline.get(sample.local_time, 0.0)
                a_val = a_timeline.get(sample.local_time, 0.0)
                e_val = e_timeline.get(sample.local_time, 0.0)
                timeline[sample.local_time] = V3SignalLayer(
                    baseline=b_out.total_score,
                    transit=t_val,
                    aspect=a_val,
                    event=e_val,
                    composite=b_out.total_score + t_val + a_val + e_val,
                )
            theme_signals[theme_code] = V3ThemeSignal(theme_code=theme_code, timeline=timeline)

        daily_metrics = {
            theme_code: self._v3_theme_aggregator.aggregate_theme(theme_signal)
            for theme_code, theme_signal in theme_signals.items()
        }
        computed_at = self._local_date_start_utc(local_date, timezone)
        return V3EngineOutput(
            engine_version=v3_versions["engine_version"] or settings.v3_engine_version,
            snapshot_version=v3_versions["snapshot_version"] or settings.v3_snapshot_version,
            evidence_pack_version=(
                v3_versions["evidence_pack_version"] or settings.v3_evidence_pack_version
            ),
            theme_signals=theme_signals,
            daily_metrics=daily_metrics,
            run_metadata={
                "mode": engine_mode.value,
                "v3_natal_structural": {
                    theme_code: {
                        "total": structural_output.total_score,
                        "components": [
                            {
                                "factor": component.factor,
                                "contribution": component.contribution,
                                "desc": component.description,
                            }
                            for component in structural_output.components
                        ],
                    }
                    for theme_code, structural_output in b_map.items()
                },
                "v3_transit_signal": transit_layer.diagnostics,
                "v3_intraday_activation": intraday_layer.diagnostics,
            },
            computed_at=computed_at,
        )

    def _build_v2_core_output(
        self,
        *,
        input_hash: str,
        engine_input: EngineInput,
        detected_events: list[AstroEvent],
        samples: list[SamplePoint],
        natal_chart: NatalChart,
        loaded_context: LoadedPredictionContext,
        requested_category_codes: tuple[str, ...] | None,
        effective_context: EffectiveContext,
        run_metadata: dict[str, object],
    ) -> CoreEngineOutput:
        natal_sensitivity = self._natal_sensitivity_calculator.compute(
            natal_chart,
            loaded_context,
        )
        (
            _category_scores,
            notes_by_step,
            events_by_step,
            contributions_by_step,
            editorial_category_scores,
        ) = self._build_prediction_outputs(
            detected_events,
            samples,
            natal_sensitivity,
            loaded_context,
            requested_category_codes=requested_category_codes,
        )

        contributions_log = []
        for step_contributions in contributions_by_step:
            for event, cat_contributions in step_contributions:
                for cat_code, contrib in cat_contributions.items():
                    contributions_log.append((event, cat_code, contrib))

        raw_by_step = None
        if engine_input.debug_mode:
            raw_by_step = {
                sample.local_time.isoformat(): [
                    {
                        "event": {
                            "event_type": event.event_type,
                            "body": event.body,
                            "target": event.target,
                            "aspect": event.aspect,
                        },
                        "contributions": contribs,
                    }
                    for event, contribs in contributions_by_step[index]
                ]
                for index, sample in enumerate(samples)
            }

        explainability = self._explainability_builder.build(
            contributions_log=contributions_log,
            run_input_hash=input_hash,
            debug_mode=engine_input.debug_mode,
            raw_contributions_by_step=raw_by_step,
        )

        step_times = [sample.local_time for sample in samples]
        turning_points = self._turning_point_detector.detect(
            notes_by_step,
            events_by_step,
            step_times,
        )
        time_blocks = self._block_generator.generate(
            turning_points,
            notes_by_step,
            events_by_step,
            step_times,
            contributions_by_step,
        )
        decision_windows = self._decision_window_builder.build(
            time_blocks,
            turning_points,
            editorial_category_scores,
        )

        return CoreEngineOutput(
            effective_context=effective_context,
            run_metadata=run_metadata,
            category_scores=editorial_category_scores,
            time_blocks=time_blocks,
            turning_points=turning_points,
            decision_windows=decision_windows,
            detected_events=detected_events,
            sampling_timeline=list(samples),
            explainability=explainability,
        )

    def _build_v3_legacy_core(
        self,
        *,
        effective_context: EffectiveContext,
        run_metadata: dict[str, object],
        detected_events: list[AstroEvent],
        samples: list[SamplePoint],
        loaded_context: LoadedPredictionContext,
        v3_core: V3EngineOutput | None,
    ) -> CoreEngineOutput:
        metrics_by_theme = v3_core.daily_metrics if v3_core is not None else {}
        category_scores: dict[str, dict[str, float | int | bool]] = {}
        for category in loaded_context.prediction_context.categories:
            if not category.is_enabled:
                continue
            metrics = metrics_by_theme.get(category.code)
            if metrics is None:
                continue
            category_scores[category.code] = self._legacy_score_from_v3(
                category,
                metrics,
                is_provisional=loaded_context.is_provisional_calibration,
            )

        return CoreEngineOutput(
            effective_context=effective_context,
            run_metadata=run_metadata,
            category_scores=category_scores,
            time_blocks=[],
            turning_points=[],
            decision_windows=[],
            detected_events=detected_events,
            sampling_timeline=list(samples),
            explainability=self._explainability_builder.build(
                contributions_log=[],
                run_input_hash=effective_context.input_hash,
                debug_mode=False,
            ),
        )

    def _legacy_score_from_v3(
        self,
        category: object,
        metrics: V3DailyMetrics,
        *,
        is_provisional: bool,
    ) -> dict[str, float | int | bool]:
        return {
            "note_20": max(0, min(20, round(metrics.score_20))),
            "raw_score": metrics.avg_score,
            "normalized_score": metrics.avg_score,
            "power": metrics.intensity_20 / 20.0,
            "volatility": metrics.volatility,
            "sort_order": getattr(category, "sort_order", 0),
            "is_provisional": is_provisional,
        }

    def _refine_detected_events(
        self,
        detected_events: list[AstroEvent],
        astro_calculator: AstroCalculator,
        event_detector: EventDetector,
        tz_name: str,
    ) -> list[AstroEvent]:
        if not hasattr(self._temporal_sampler, "refine_around"):
            return detected_events
        if not hasattr(event_detector, "refine_exact_event"):
            return detected_events

        refined_events: list[AstroEvent] = []
        for event in detected_events:
            if event.event_type not in EventDetector.EXACT_EVENT_TYPES:
                refined_events.append(event)
                continue

            refined_points = self._temporal_sampler.refine_around(
                event.ut_time,
                radius_minutes=5,
                tz_name=tz_name,
            )
            refined_states = [
                astro_calculator.compute_step(sample.ut_time, sample.local_time)
                for sample in refined_points
            ]
            refined_events.append(event_detector.refine_exact_event(event, refined_states))

        refined_events.sort(key=lambda item: item.ut_time)
        return refined_events

    def _build_prediction_outputs(
        self,
        detected_events: list[AstroEvent],
        samples: list[SamplePoint],
        ns_map: dict[str, float],
        loaded_context: LoadedPredictionContext,
        *,
        requested_category_codes: tuple[str, ...] | None = None,
    ) -> tuple[
        dict[str, int],
        list[dict[str, int]],
        list[list[AstroEvent]],
        list[list[tuple[AstroEvent, dict[str, float]]]],
        dict[str, dict[str, float | int]],
    ]:
        available_category_codes = [
            category.code
            for category in loaded_context.prediction_context.categories
            if category.is_enabled
        ]
        if requested_category_codes is None:
            category_codes = available_category_codes
        else:
            allowed_codes = set(normalize_category_codes(requested_category_codes))
            unknown_codes = allowed_codes.difference(available_category_codes)
            if unknown_codes:
                unknown_codes_csv = ", ".join(sorted(unknown_codes))
                raise PredictionContextError(
                    "Requested category codes are not enabled in the prediction context: "
                    f"{unknown_codes_csv}"
                )
            category_codes = [
                category_code
                for category_code in available_category_codes
                if category_code in allowed_codes
            ]
        events_by_step: list[list[AstroEvent]] = [[] for _ in samples]
        contributions_by_step: list[list[tuple[AstroEvent, dict[str, float]]]] = [
            [] for _ in samples
        ]
        contribution_totals_by_step: list[dict[str, float]] = [{} for _ in samples]

        for event in detected_events:
            if not samples:
                break

            center_index = self._nearest_step_index(event.ut_time, samples)
            routed_categories = self._domain_router.route(event, loaded_context)
            contributions = self._contribution_calculator.compute(
                event,
                ns_map,
                routed_categories,
                loaded_context,
            )

            # Traceability: event and per-event contributions stay on the
            # nearest step only (AC4 — drivers remain identifiable).
            events_by_step[center_index].append(event)
            contributions_by_step[center_index].append((event, contributions))

            # Temporal spreading: contribution totals are distributed across
            # the influence window so notes_by_step shows a rise/peak/fall
            # curve instead of an isolated spike (AC3).
            spread = spread_event_weights(event, samples)
            for step_i, weight in spread:
                for category_code, contribution in contributions.items():
                    contribution_totals_by_step[step_i][category_code] = (
                        contribution_totals_by_step[step_i].get(category_code, 0.0)
                        + contribution * weight
                    )

        day_aggregation = self._temporal_aggregator.aggregate(
            contribution_totals_by_step,
            category_codes,
        )

        # Compute provisional metadata once — reused for day scores, notes_by_step,
        # editorial_category_scores, avoiding redundant recalculation.
        provisional_cats_list = self._percentile_calibrator.get_provisional_categories(
            category_codes, loaded_context.calibrations
        )
        day_relative_cal = None
        if len(provisional_cats_list) >= 3:
            raw_days = [
                day_aggregation.categories[cat].raw_day
                for cat in provisional_cats_list
                if cat in day_aggregation.categories
            ]
            day_relative_cal = self._percentile_calibrator.compute_day_relative_calibration(
                raw_days
            )
        provisional_cats = set(provisional_cats_list)

        category_scores = self._percentile_calibrator.calibrate_all_provisional_aware(
            day_aggregation,
            loaded_context.calibrations,
            provisional_cats=provisional_cats_list,
            day_relative_cal=day_relative_cal,
        )

        editorial_category_scores = {
            category.code: {
                "note_20": category_scores.get(category.code, 0),
                "raw_score": day_aggregation.categories.get(category.code).raw_day
                if category.code in day_aggregation.categories
                else 0.0,
                "normalized_score": day_aggregation.categories.get(category.code).raw_day
                if category.code in day_aggregation.categories
                else 0.0,
                "power": day_aggregation.categories.get(category.code).power
                if category.code in day_aggregation.categories
                else 0.0,
                "volatility": day_aggregation.categories.get(category.code).volatility
                if category.code in day_aggregation.categories
                else 0.0,
                "sort_order": category.sort_order,
                "is_provisional": category.code in provisional_cats,
            }
            for category in loaded_context.prediction_context.categories
            if category.is_enabled and category.code in category_codes
        }
        notes_by_step = [
            {
                category_code: self._percentile_calibrator.calibrate(
                    step_contributions.get(category_code, 0.0),
                    day_relative_cal
                    if category_code in provisional_cats and day_relative_cal
                    else loaded_context.calibrations.get(category_code),
                )
                for category_code in category_codes
            }
            for step_contributions in contribution_totals_by_step
        ]

        return (
            category_scores,
            notes_by_step,
            events_by_step,
            contributions_by_step,
            editorial_category_scores,
        )

    def _build_editorial_time_blocks(
        self,
        time_blocks: list,
        notes_by_step: list[dict[str, int]],
        step_times: list[datetime],
    ) -> list[SimpleNamespace]:
        editorial_blocks: list[SimpleNamespace] = []
        for block in time_blocks:
            step_indices = [
                step_index
                for step_index, step_time in enumerate(step_times)
                if block.start_local <= step_time < block.end_local
            ]
            category_means = self._category_means_for_steps(notes_by_step, step_indices)
            editorial_blocks.append(
                SimpleNamespace(
                    start_local=block.start_local,
                    end_local=block.end_local,
                    dominant_categories=list(block.dominant_categories),
                    tone_code=block.tone_code,
                    category_means=category_means,
                )
            )
        return editorial_blocks

    def _category_means_for_steps(
        self,
        notes_by_step: list[dict[str, int]],
        step_indices: list[int],
    ) -> dict[str, float]:
        if not step_indices:
            return {}

        sums: dict[str, float] = {}
        counts: dict[str, int] = {}
        for step_index in step_indices:
            for category_code, note in notes_by_step[step_index].items():
                sums[category_code] = sums.get(category_code, 0.0) + note
                counts[category_code] = counts.get(category_code, 0) + 1

        return {
            category_code: sums[category_code] / counts[category_code] for category_code in sums
        }

    def _resolve_caution_category_codes(
        self,
        loaded_context: LoadedPredictionContext,
    ) -> list[str]:
        raw_codes = loaded_context.ruleset_context.parameters.get("caution_category_codes")
        if isinstance(raw_codes, (list, tuple, set)):
            return normalize_category_codes(raw_codes)
        return list(EditorialOutputBuilder.DEFAULT_CAUTION_CODES)

    def _nearest_step_index(self, ut_time: float, samples: list[SamplePoint]) -> int:
        return min(
            range(len(samples)),
            key=lambda index: abs(samples[index].ut_time - ut_time),
        )

    def _build_day_grid_from_samples(
        self,
        samples: list[SamplePoint],
        local_date: date,
        timezone: str,
    ) -> DayGrid:
        if not samples:
            raise PredictionContextError("Cannot build a DayGrid from an empty sample list")

        return DayGrid(
            samples=samples,
            ut_start=samples[0].ut_time,
            ut_end=samples[-1].ut_time,
            sunrise_ut=None,
            sunset_ut=None,
            local_date=local_date,
            timezone=timezone,
        )

    def _local_date_to_ut_interval(self, local_date: date, tz_name: str) -> tuple[float, float]:
        """Converts a local date + timezone into a UT interval (Julian Day start/end)."""
        dt_start_utc = self._local_date_start_utc(local_date, tz_name)
        dt_end_utc = self._local_date_end_utc(local_date, tz_name)
        return self._datetime_to_julian_day(dt_start_utc), self._datetime_to_julian_day(dt_end_utc)

    def _local_date_start_utc(self, local_date: date, tz_name: str) -> datetime:
        return self._local_datetime_to_utc(datetime.combine(local_date, time.min), tz_name)

    def _local_date_end_utc(self, local_date: date, tz_name: str) -> datetime:
        next_day = local_date + timedelta(days=1)
        return self._local_datetime_to_utc(datetime.combine(next_day, time.min), tz_name)

    def _local_datetime_to_utc(self, local_dt: datetime, tz_name: str) -> datetime:
        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError as exc:
            raise PredictionContextError(f"Unknown IANA timezone: {tz_name!r}") from exc

        return local_dt.replace(tzinfo=tz).astimezone(UTC)

    def _datetime_to_julian_day(self, dt_utc: datetime) -> float:
        return swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )

    def _load_prediction_context(self, engine_input: EngineInput) -> LoadedPredictionContext:
        if self._prediction_context_loader is None:
            raise PredictionContextError(
                "Prediction context loader not configured for EngineOrchestrator"
            )

        loaded_context = self._prediction_context_loader(
            engine_input.reference_version,
            engine_input.ruleset_version,
            engine_input.local_date,
        )
        if loaded_context is None:
            raise PredictionContextError(
                "Prediction context not found for "
                f"reference={engine_input.reference_version!r} "
                f"ruleset={engine_input.ruleset_version!r}"
            )
        return loaded_context

    def _resolve_house_system(
        self,
        ruleset_version: str,
        loaded_context: LoadedPredictionContext | None = None,
    ) -> str:
        if loaded_context is not None:
            house_system = loaded_context.ruleset_context.ruleset.house_system.strip()
            if not house_system:
                raise PredictionContextError(
                    f"Ruleset {ruleset_version!r} does not define a house_system"
                )
            return house_system

        if self._ruleset_context_loader is None:
            return "placidus"

        ruleset_context = self._ruleset_context_loader(ruleset_version)
        if ruleset_context is None:
            raise PredictionContextError(
                f"Ruleset context not found for version {ruleset_version!r}"
            )

        house_system = ruleset_context.ruleset.house_system.strip()
        if not house_system:
            raise PredictionContextError(
                f"Ruleset {ruleset_version!r} does not define a house_system"
            )

        return house_system

    def _resolve_effective_house_system(
        self,
        house_system_requested: str,
        astro_states: list,
    ) -> str:
        if not astro_states:
            return house_system_requested

        effective_systems = {state.house_system_effective for state in astro_states}
        if len(effective_systems) == 1:
            return effective_systems.pop()
        if "porphyre" in effective_systems:
            return "porphyre"
        return astro_states[0].house_system_effective

    def _extract_house_cusps(self, natal_chart: dict) -> list[float]:
        raw_cusps = natal_chart.get("house_cusps")
        if raw_cusps is None:
            raw_houses = natal_chart.get("houses")
            if isinstance(raw_houses, list):
                raw_cusps = [
                    house.get("cusp_longitude")
                    for house in sorted(
                        raw_houses,
                        key=lambda item: int(item.get("number", 0)),
                    )
                ]

        if not isinstance(raw_cusps, list) or len(raw_cusps) != 12:
            raise PredictionContextError(
                "EngineInput.natal_chart must provide 12 house cusps via "
                "'house_cusps' or chart_json-style 'houses'"
            )

        try:
            return [self._coerce_longitude(value) for value in raw_cusps]
        except (TypeError, ValueError) as exc:
            raise PredictionContextError("Natal house cusps must be numeric") from exc

    def _build_natal_chart(
        self,
        natal_chart: dict,
        natal_cusps: list[float],
        loaded_context: LoadedPredictionContext,
    ) -> NatalChart:
        planet_positions = self._extract_named_longitudes(
            natal_chart.get("planets"),
            code_key="code",
        )

        # Normalize planet names
        normalized_positions: dict[str, float] = {}
        for code, longitude in planet_positions.items():
            canonical = self._canonical_planet_name(code)
            if canonical is not None:
                normalized_positions[canonical] = longitude
            else:
                normalized_positions[code] = longitude  # Keep original if not a planet (e.g. angle)

        # Include angles
        for angle_code, longitude in self._extract_angle_longitudes(natal_chart).items():
            normalized_positions[angle_code] = longitude

        # Calculate houses for ALL positions (planets + angles)
        point_houses = {
            code: self._house_for_longitude(lon, natal_cusps)
            for code, lon in normalized_positions.items()
        }

        house_sign_rulers = self._extract_house_sign_rulers(natal_chart, natal_cusps)

        # AC1 for Story 42.2: Compute natal aspects
        natal_aspects = self._compute_natal_aspects(normalized_positions, loaded_context)

        return NatalChart(
            planet_positions=normalized_positions,
            planet_houses=point_houses,
            house_sign_rulers=house_sign_rulers,
            natal_aspects=natal_aspects,
        )

    def _compute_natal_aspects(
        self,
        positions: dict[str, float],
        loaded_context: LoadedPredictionContext,
    ) -> list[AstroEvent]:
        """Compute major aspects between natal planets/angles."""
        aspects: list[AstroEvent] = []
        codes = list(positions.keys())
        aspect_profiles = loaded_context.prediction_context.aspect_profiles

        for i, code1 in enumerate(codes):
            for code2 in codes[i + 1 :]:
                lon1 = positions[code1]
                lon2 = positions[code2]

                for deg, name in EventDetector.ASPECTS_V1.items():
                    diff = abs(lon1 - lon2) % 360
                    if diff > 180:
                        diff = 360 - diff
                    orb = abs(diff - deg)

                    aspect_profile = self._lookup_mapping_value(aspect_profiles, name)
                    orb_max = 5.0
                    base_weight = 1.0
                    default_valence = None
                    if aspect_profile is not None:
                        orb_max *= float(getattr(aspect_profile, "orb_multiplier", 1.0) or 1.0)
                        base_weight = float(
                            getattr(aspect_profile, "intensity_weight", 1.0) or 1.0
                        )
                        default_valence = getattr(aspect_profile, "default_valence", None)

                    if orb <= orb_max:
                        aspects.append(
                            AstroEvent(
                                event_type="natal_aspect",
                                ut_time=0.0,
                                local_time=datetime(1970, 1, 1, tzinfo=UTC),
                                body=code1,
                                target=code2,
                                aspect=name,
                                orb_deg=orb,
                                priority=50,
                                base_weight=base_weight,
                                metadata={
                                    "is_natal": True,
                                    "default_valence": default_valence,
                                    "orb_max": orb_max,
                                },
                            )
                        )
        return aspects

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

    def _extract_named_longitudes(
        self,
        raw_value: object,
        *,
        code_key: str,
    ) -> dict[str, float]:
        if isinstance(raw_value, dict):
            return {
                str(code): self._coerce_longitude(longitude)
                for code, longitude in raw_value.items()
            }
        if isinstance(raw_value, list):
            positions: dict[str, float] = {}
            for item in raw_value:
                if not isinstance(item, dict) or code_key not in item or "longitude" not in item:
                    raise PredictionContextError(
                        "Natal chart planet entries must expose 'code' and 'longitude'"
                    )
                positions[str(item[code_key])] = self._coerce_longitude(item["longitude"])
            return positions
        raise PredictionContextError("EngineInput.natal_chart must provide planet positions")

    def _extract_angle_longitudes(self, natal_chart: dict) -> dict[str, float]:
        raw_angles = natal_chart.get("angles")
        if not isinstance(raw_angles, dict):
            return {}

        angle_positions: dict[str, float] = {}
        for raw_code, value in raw_angles.items():
            if value is None:
                continue
            normalized_code = str(raw_code).strip().upper()
            if normalized_code not in {"ASC", "MC"}:
                continue
            longitude_value = value.get("longitude") if isinstance(value, dict) else value
            angle_positions["Asc" if normalized_code == "ASC" else "MC"] = self._coerce_longitude(
                longitude_value
            )
        return angle_positions

    def _extract_house_sign_rulers(
        self,
        natal_chart: dict,
        natal_cusps: list[float],
    ) -> dict[int, str]:
        raw_house_sign_rulers = natal_chart.get("house_sign_rulers")
        if isinstance(raw_house_sign_rulers, dict):
            return {int(house_num): str(sign) for house_num, sign in raw_house_sign_rulers.items()}

        return {
            index + 1: _ZODIAC_SIGNS[int(cusp // 30) % len(_ZODIAC_SIGNS)]
            for index, cusp in enumerate(natal_cusps)
        }

    def _house_for_longitude(self, longitude: float, cusps: list[float]) -> int:
        normalized = longitude % 360.0
        for index, cusp_start in enumerate(cusps):
            cusp_end = cusps[(index + 1) % len(cusps)]
            if cusp_start < cusp_end:
                if cusp_start <= normalized < cusp_end:
                    return index + 1
            elif normalized >= cusp_start or normalized < cusp_end:
                return index + 1
        return 1

    def _canonical_planet_name(self, raw_code: str) -> str | None:
        return _PLANET_NAME_MAP.get(str(raw_code).strip().lower())

    def _coerce_longitude(self, value: object) -> float:
        if not isinstance(value, Real):
            raise TypeError(f"Longitude value must be numeric, got {type(value).__name__}")
        return float(value) % 360.0
