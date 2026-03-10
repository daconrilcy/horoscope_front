from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta
from numbers import Real
from types import SimpleNamespace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

from app.infra.db.repositories.prediction_schemas import RulesetContext

from .aggregator import TemporalAggregator
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
from .input_hash import compute_engine_input_hash
from .natal_sensitivity import NatalSensitivityCalculator
from .schemas import (
    AstroEvent,
    CoreEngineOutput,
    EffectiveContext,
    EngineInput,
    NatalChart,
    PersistablePredictionBundle,
    SamplePoint,
)
from .temporal_kernel import spread_event_weights
from .temporal_sampler import TemporalSampler
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
        )

    def run(
        self,
        engine_input: EngineInput,
        *,
        category_codes: tuple[str, ...] | None = None,
        include_editorial: bool = True,
        include_editorial_text: bool = False,
        editorial_text_lang: str = "fr",
    ) -> PersistablePredictionBundle:
        """
        Executes the prediction engine for a given input and returns a complete bundle.
        """
        # 1. AC3 - Compute hash
        input_hash = compute_engine_input_hash(
            natal_chart=engine_input.natal_chart,
            local_date=engine_input.local_date,
            timezone=engine_input.timezone,
            latitude=engine_input.latitude,
            longitude=engine_input.longitude,
            reference_version=engine_input.reference_version,
            ruleset_version=engine_input.ruleset_version,
        )

        # 2. AC4 - Convert local date to UT interval (JD)
        jd_start, jd_end = self._local_date_to_ut_interval(
            engine_input.local_date, engine_input.timezone
        )

        loaded_context = self._load_prediction_context(engine_input)
        house_system_requested = self._resolve_house_system(
            engine_input.ruleset_version,
            loaded_context,
        )

        natal_cusps = self._extract_house_cusps(engine_input.natal_chart)
        natal_chart = self._build_natal_chart(engine_input.natal_chart, natal_cusps)

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
            day_grid.samples,
            natal_sensitivity,
            loaded_context,
            requested_category_codes=category_codes,
        )

        # 3. Build explainability report
        contributions_log = []
        for step_contributions in contributions_by_step:
            for event, cat_contributions in step_contributions:
                for cat_code, contrib in cat_contributions.items():
                    contributions_log.append((event, cat_code, contrib))

        # Format raw contributions for debug mode
        raw_by_step = None
        if engine_input.debug_mode:
            raw_by_step = {
                sample.local_time.isoformat(): [
                    {
                        "event": {
                            "event_type": ev.event_type,
                            "body": ev.body,
                            "target": ev.target,
                            "aspect": ev.aspect,
                        },
                        "contributions": contribs,
                    }
                    for ev, contribs in contributions_by_step[i]
                ]
                for i, sample in enumerate(day_grid.samples)
            }

        explainability = self._explainability_builder.build(
            contributions_log=contributions_log,
            run_input_hash=input_hash,
            debug_mode=engine_input.debug_mode,
            raw_contributions_by_step=raw_by_step,
        )

        step_times = [sample.local_time for sample in day_grid.samples]
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

        run_metadata = {
            "run_id": None,
            "computed_at": self._local_date_start_utc(
                engine_input.local_date, engine_input.timezone
            ).isoformat(),
            "debug_mode": engine_input.debug_mode,
            "jd_interval": [jd_start, jd_end],
            "is_provisional_calibration": loaded_context.is_provisional_calibration,
            "calibration_label": loaded_context.calibration_label,
            "caution_category_codes": self._resolve_caution_category_codes(loaded_context),
        }

        # AC1 - CoreEngineOutput (Calcul pur sans texte)
        core_output = CoreEngineOutput(
            effective_context=effective_context,
            run_metadata=run_metadata,
            category_scores=editorial_category_scores,
            time_blocks=time_blocks,
            turning_points=turning_points,
            decision_windows=decision_windows,
            detected_events=detected_events,
            sampling_timeline=list(day_grid.samples),
            explainability=explainability,
        )

        if not include_editorial:
            return PersistablePredictionBundle(core=core_output)

        # AC1 - EditorialOutputBundle (Textes et résumés) via AC3 - PredictionEditorialService
        editorial_bundle = self._editorial_service.generate_bundle(
            core_output, lang=editorial_text_lang
        )

        # AC1 - PersistablePredictionBundle (Prêt à sauvegarder)
        return PersistablePredictionBundle(
            core=core_output,
            editorial=editorial_bundle,
        )

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

    def _build_natal_chart(self, natal_chart: dict, natal_cusps: list[float]) -> NatalChart:
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

        return NatalChart(
            planet_positions=normalized_positions,
            planet_houses=point_houses,
            house_sign_rulers=house_sign_rulers,
        )

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
