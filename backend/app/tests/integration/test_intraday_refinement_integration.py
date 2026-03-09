from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

from app.infra.db.repositories.prediction_schemas import (
    CategoryData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.schemas import (
    AstroEvent,
    EngineInput,
    PlanetState,
    SamplePoint,
    StepAstroState,
)
from app.prediction.temporal_sampler import DayGrid, TemporalSampler

BASE_UTC = datetime(2026, 3, 7, 0, 0, tzinfo=UTC)


class StubTemporalSampler(TemporalSampler):
    def build_day_grid(
        self,
        local_date: date,
        tz_name: str,
        latitude: float,
        longitude: float,
    ) -> DayGrid:
        start = BASE_UTC
        samples = [
            SamplePoint(ut_time=self._datetime_to_jd(start), local_time=start),
            SamplePoint(
                ut_time=self._datetime_to_jd(start + timedelta(minutes=15)),
                local_time=start + timedelta(minutes=15),
            ),
            SamplePoint(
                ut_time=self._datetime_to_jd(start + timedelta(minutes=30)),
                local_time=start + timedelta(minutes=30),
            ),
        ]
        return DayGrid(
            samples=samples,
            ut_start=samples[0].ut_time,
            ut_end=samples[-1].ut_time,
            sunrise_ut=None,
            sunset_ut=None,
            local_date=local_date,
            timezone=tz_name,
        )


class StubAstroCalculator:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        pass

    def compute_step(self, ut_jd: float, local_time: datetime) -> StepAstroState:
        # Minimum orb occurs one minute after the coarse exact candidate.
        minutes_from_start = round((local_time - BASE_UTC).total_seconds() / 60)
        longitude = 10.0 + abs(minutes_from_start - 16) * 0.1
        return StepAstroState(
            ut_jd=ut_jd,
            local_time=local_time,
            ascendant_deg=0.0,
            mc_deg=270.0,
            house_cusps=[float(index * 30) for index in range(12)],
            house_system_effective="placidus",
            planets={
                "Sun": PlanetState(
                    code="Sun",
                    longitude=longitude,
                    speed_lon=1.0,
                    is_retrograde=False,
                    sign_code=0,
                    natal_house_transited=10,
                )
            },
        )


class StubEventDetector:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self._target_event = AstroEvent(
            event_type="aspect_exact_to_angle",  # MC is an angle target
            ut_time=StubTemporalSampler()._datetime_to_jd(BASE_UTC + timedelta(minutes=15)),
            local_time=BASE_UTC + timedelta(minutes=15),
            body="Sun",
            target="MC",
            aspect="conjunction",
            orb_deg=0.1,
            priority=80,
            base_weight=1.0,
            metadata={"phase": "applying"},
        )

    def detect(self, steps: list[StepAstroState], _day_grid: DayGrid) -> list[AstroEvent]:
        return [replace(self._target_event, ut_time=steps[1].ut_jd, local_time=steps[1].local_time)]

    def refine_exact_event(
        self,
        coarse_event: AstroEvent,
        refined_steps: list[StepAstroState],
    ) -> AstroEvent:
        best_step = min(refined_steps, key=lambda step: abs(step.planets["Sun"].longitude - 10.0))
        return replace(
            coarse_event,
            ut_time=best_step.ut_jd,
            local_time=best_step.local_time,
            orb_deg=abs(best_step.planets["Sun"].longitude - 10.0),
            metadata={**coarse_event.metadata, "refined": True},
        )


def _loaded_context() -> LoadedPredictionContext:
    return LoadedPredictionContext(
        prediction_context=PredictionContext(
            categories=(
                CategoryData(
                    id=1,
                    code="work",
                    name="Work",
                    display_name="Work",
                    sort_order=1,
                    is_enabled=True,
                ),
            ),
            planet_profiles={},
            house_profiles={},
            planet_category_weights=(),
            house_category_weights=(),
            sign_rulerships={},
            aspect_profiles={},
            astro_points={},
            point_category_weights=(),
        ),
        ruleset_context=RulesetContext(
            ruleset=RulesetData(
                id=1,
                version="1.0.0",
                reference_version_id=1,
                zodiac_type="tropical",
                coordinate_mode="geocentric",
                house_system="placidus",
                time_step_minutes=15,
                is_locked=True,
            ),
            parameters={},
            event_types={},
        ),
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
        )

def test_intraday_refinement_changes_exact_event_timestamp_in_output() -> None:
    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: _loaded_context(),
        temporal_sampler=StubTemporalSampler(),
        astro_calculator_factory=StubAstroCalculator,
        event_detector_factory=StubEventDetector,
    )
    engine_input = EngineInput(
        natal_chart={
            "planets": [{"code": "sun", "longitude": 10.0, "house": 10}],
            "houses": [
                {"number": house_number, "cusp_longitude": float((house_number - 1) * 30)}
                for house_number in range(1, 13)
            ],
            "angles": {"ASC": {"longitude": 0.0}, "MC": {"longitude": 10.0}},
        },
        local_date=date(2026, 3, 7),
        timezone="UTC",
        latitude=48.8566,
        longitude=2.3522,
        reference_version="1.0.0",
        ruleset_version="1.0.0",
    )

    output = orchestrator.run(engine_input)

    exact_events = [event for event in output.detected_events if event.event_type == "aspect_exact_to_angle"]
    assert len(exact_events) == 1
    assert exact_events[0].metadata["refined"] is True
    assert exact_events[0].local_time.minute == 16
    assert exact_events[0].local_time.minute % 15 != 0
