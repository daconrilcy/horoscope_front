from __future__ import annotations

from dataclasses import asdict, is_dataclass, replace
from datetime import date, datetime
from pathlib import Path
from tempfile import mkdtemp
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.prediction.aggregator import RAW_DAY_MAX, RAW_STEP_MAX, DayAggregation
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.natal_sensitivity import NatalSensitivityCalculator
from app.prediction.schemas import EngineInput, EngineOutput
from app.services.reference_data_service import ReferenceDataService
from scripts.seed_31_prediction_reference_v2 import run_seed

BACKEND_DIR = Path(__file__).resolve().parents[3]

NS_MIN = 0.75
NS_MAX = 1.25
CONTRIBUTION_MIN = -1.0
CONTRIBUTION_MAX = 1.0


def serialize_output(engine_output: EngineOutput) -> dict[str, Any]:
    """Sérialisation JSON-safe déterministe de tous les champs pertinents."""

    if hasattr(engine_output, "to_engine_output"):
        legacy_output = engine_output.to_engine_output()
        run_metadata = dict(legacy_output.run_metadata)
        run_metadata.pop("caution_category_codes", None)
        run_metadata.pop("overall_summary", None)
        engine_output = replace(
            legacy_output,
            run_metadata=run_metadata,
            editorial_text=None,
        )

    def _to_dict(obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if is_dataclass(obj):
            return {key: _to_dict(value) for key, value in asdict(obj).items()}
        if isinstance(obj, dict):
            return {str(key): _to_dict(value) for key, value in sorted(obj.items(), key=_sort_key)}
        if isinstance(obj, (list, tuple)):
            return [_to_dict(value) for value in obj]
        return obj

    return _to_dict(engine_output)


def create_session() -> Session:
    temp_dir = Path(mkdtemp(prefix="prediction-regression-"))
    db_path = temp_dir / "regression.db"
    database_url = f"sqlite:///{db_path.as_posix()}"

    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    ReferenceDataService._clear_cache_for_tests()
    ReferenceDataService.seed_reference_version(session, "1.0.0")
    run_seed(session)
    session.commit()

    session.info["engine"] = engine
    session.info["temp_dir"] = temp_dir
    return session


def create_orchestrator(session: Session) -> EngineOrchestrator:
    loader = PredictionContextLoader()
    return EngineOrchestrator(
        prediction_context_loader=lambda ref, ruleset, when: loader.load(
            session, ref, ruleset, when
        )
    )


def load_context(session: Session, engine_input: EngineInput):
    return PredictionContextLoader().load(
        session,
        engine_input.reference_version,
        engine_input.ruleset_version,
        engine_input.local_date,
    )


def compute_ns_bounds(
    orchestrator: EngineOrchestrator, engine_input: EngineInput
) -> dict[str, float]:
    loaded_context = orchestrator._load_prediction_context(engine_input)
    natal_cusps = orchestrator._extract_house_cusps(engine_input.natal_chart)
    natal_chart = orchestrator._build_natal_chart(
        engine_input.natal_chart,
        natal_cusps,
        loaded_context,
    )
    return NatalSensitivityCalculator().compute(natal_chart, loaded_context)


def compute_day_aggregation(
    orchestrator: EngineOrchestrator,
    engine_input: EngineInput,
) -> tuple[DayAggregation, list[list[tuple[Any, dict[str, float]]]]]:
    loaded_context = orchestrator._load_prediction_context(engine_input)
    natal_cusps = orchestrator._extract_house_cusps(engine_input.natal_chart)
    natal_chart = orchestrator._build_natal_chart(
        engine_input.natal_chart,
        natal_cusps,
        loaded_context,
    )
    day_grid = orchestrator._temporal_sampler.build_day_grid(
        engine_input.local_date,
        engine_input.timezone,
        engine_input.latitude,
        engine_input.longitude,
    )
    astro_calculator = orchestrator._astro_calculator_factory(
        natal_cusps,
        engine_input.latitude,
        engine_input.longitude,
    )
    astro_states = [
        astro_calculator.compute_step(sample.ut_time, sample.local_time)
        for sample in day_grid.samples
    ]
    event_detector = orchestrator._event_detector_factory(loaded_context, natal_chart)
    detected_events = event_detector.detect(astro_states, day_grid)
    ns_map = orchestrator._natal_sensitivity_calculator.compute(natal_chart, loaded_context)
    category_codes = [
        category.code
        for category in loaded_context.prediction_context.categories
        if category.is_enabled
    ]

    contributions_by_step: list[dict[str, float]] = [{} for _ in day_grid.samples]
    raw_contributions_by_step: list[list[tuple[Any, dict[str, float]]]] = [
        [] for _ in day_grid.samples
    ]

    for event in detected_events:
        step_index = orchestrator._nearest_step_index(event.ut_time, day_grid.samples)
        routed_categories = orchestrator._domain_router.route(event, loaded_context)
        contributions = orchestrator._contribution_calculator.compute(
            event,
            ns_map,
            routed_categories,
            loaded_context,
        )
        raw_contributions_by_step[step_index].append((event, contributions))
        for category_code, contribution in contributions.items():
            contributions_by_step[step_index][category_code] = (
                contributions_by_step[step_index].get(category_code, 0.0) + contribution
            )

    day_aggregation = orchestrator._temporal_aggregator.aggregate(
        contributions_by_step,
        category_codes,
    )
    return day_aggregation, raw_contributions_by_step


def assert_clamps(
    orchestrator: EngineOrchestrator, engine_input: EngineInput, output: EngineOutput
) -> None:
    """Vérifie les bornes AC2 sur les structures réellement utilisées par le moteur."""

    ns_map = compute_ns_bounds(orchestrator, engine_input)
    for ns_value in ns_map.values():
        assert NS_MIN <= ns_value <= NS_MAX

    day_aggregation, raw_contributions_by_step = compute_day_aggregation(orchestrator, engine_input)
    for step_contributions in raw_contributions_by_step:
        for _, contributions in step_contributions:
            for value in contributions.values():
                assert CONTRIBUTION_MIN <= value <= CONTRIBUTION_MAX

    for category in day_aggregation.categories.values():
        for raw_step in category.raw_steps:
            assert -RAW_STEP_MAX <= raw_step <= RAW_STEP_MAX
        assert -RAW_DAY_MAX <= category.raw_day <= RAW_DAY_MAX

    for score in output.category_scores.values():
        assert 1 <= score["note_20"] <= 20


def _sort_key(item: tuple[object, object]) -> str:
    return str(item[0])
