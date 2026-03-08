import json
from datetime import date
from pathlib import Path

import pytest

from app.prediction.schemas import EngineInput
from app.tests.regression.helpers import (
    assert_clamps,
    compute_ns_bounds,
    create_orchestrator,
    create_session,
    serialize_output,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_fixtures():
    return sorted(FIXTURES_DIR.glob("F*.json"))


def get_snapshots():
    return sorted(FIXTURES_DIR.glob("snapshot_full_day_*.json"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_engine_input(config: dict) -> EngineInput:
    return EngineInput(
        natal_chart=config["natal_chart"],
        local_date=date.fromisoformat(config["local_date"]),
        timezone=config["timezone"],
        latitude=config["latitude"],
        longitude=config["longitude"],
        reference_version=config["reference_version"],
        ruleset_version=config["ruleset_version"],
        debug_mode=config["debug_mode"],
    )


@pytest.fixture(scope="module")
def session():
    db_session = create_session()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="module")
def orchestrator(session):
    return create_orchestrator(session)


@pytest.mark.regression
@pytest.mark.parametrize("fixture_file", get_fixtures())
def test_case_type(orchestrator, fixture_file):
    """AC1, AC2, AC3, AC5 - Regression test for standard fixtures."""
    data = load_json(fixture_file)
    config = data["input"]
    expected = data["expected"]

    engine_input = build_engine_input(config)
    output1 = orchestrator.run(engine_input)
    output2 = orchestrator.run(engine_input)

    assert output1 == output2
    assert output1.effective_context.input_hash == expected["input_hash"]
    assert output1.category_scores == output2.category_scores
    assert output1.turning_points == output2.turning_points
    assert output1.time_blocks == output2.time_blocks

    assert_clamps(orchestrator, engine_input, output1)
    assert len(output1.turning_points) == expected["turning_points_count"]

    if "category_scores" in expected:
        for cat, score in expected["category_scores"].items():
            assert output1.category_scores[cat] == score
    if "detected_events_count" in expected:
        assert len(output1.detected_events) == expected["detected_events_count"]
    if "sample_count" in expected:
        assert len(output1.sampling_timeline) == expected["sample_count"]
    if "is_provisional_calibration" in expected:
        assert (
            output1.run_metadata["is_provisional_calibration"]
            == expected["is_provisional_calibration"]
        )
    if "required_event_types" in expected:
        event_types = {event.event_type for event in output1.detected_events}
        assert set(expected["required_event_types"]).issubset(event_types)


@pytest.mark.regression
@pytest.mark.parametrize("snapshot_file", get_snapshots())
def test_full_snapshot(orchestrator, snapshot_file):
    """AC6 - Full snapshot comparison."""
    data = load_json(snapshot_file)
    config = data["input"]
    expected_output = data["expected_output"]

    engine_input = build_engine_input(config)
    result = orchestrator.run(engine_input)
    serialized_result = serialize_output(result)

    assert serialized_result == expected_output


@pytest.mark.regression
def test_hash_changes_on_version_change(orchestrator):
    """AC4 - ruleset_version différent → input_hash différent."""
    # Le hash doit refléter le versionning métier, indépendamment du contenu DB.
    natal = {"planets": [], "houses": [], "angles": {}}

    input1 = EngineInput(
        natal_chart=natal,
        local_date=date.fromisoformat("2026-03-07"),
        timezone="Europe/Paris",
        latitude=48.85,
        longitude=2.35,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    input2 = EngineInput(
        natal_chart=natal,
        local_date=date.fromisoformat("2026-03-07"),
        timezone="Europe/Paris",
        latitude=48.85,
        longitude=2.35,
        reference_version="2.0.0",
        ruleset_version="2.0.1",  # Different version
    )

    hash1 = orchestrator._compute_hash(input1)
    hash2 = orchestrator._compute_hash(input2)

    assert hash1 != hash2


@pytest.mark.regression
@pytest.mark.parametrize("fixture_file", get_fixtures())
def test_ns_bounds_all_fixtures(orchestrator, fixture_file):
    """AC2 - NS(c) doit toujours rester dans les bornes."""
    engine_input = build_engine_input(load_json(fixture_file)["input"])
    ns_map = compute_ns_bounds(orchestrator, engine_input)
    assert all(0.75 <= value <= 1.25 for value in ns_map.values())


@pytest.mark.regression
@pytest.mark.parametrize("fixture_file", get_fixtures())
def test_pivots_stable(orchestrator, fixture_file):
    """AC3 - même liste de pivots à version identique."""
    engine_input = build_engine_input(load_json(fixture_file)["input"])
    output1 = orchestrator.run(engine_input)
    output2 = orchestrator.run(engine_input)
    assert serialize_output(output1.turning_points) == serialize_output(output2.turning_points)
