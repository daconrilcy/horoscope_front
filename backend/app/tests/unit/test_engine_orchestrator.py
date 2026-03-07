from datetime import date

import pytest

from app.infra.db.repositories.prediction_schemas import RulesetContext, RulesetData
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.exceptions import PredictionContextError
from app.prediction.schemas import EngineInput, EngineOutput


@pytest.fixture
def orchestrator():
    return EngineOrchestrator(
        ruleset_context_loader=lambda _: RulesetContext(
            ruleset=RulesetData(
                id=1,
                version="1.0.0",
                reference_version_id=1,
                zodiac_type="tropical",
                coordinate_mode="geocentric",
                house_system="whole_sign",
                time_step_minutes=60,
                is_locked=True,
            ),
            parameters={},
            event_types={},
        )
    )


@pytest.fixture
def base_input():
    return EngineInput(
        natal_chart={"planets": {"sun": 80.5, "moon": 120.2}},
        local_date=date(2026, 3, 7),
        timezone="Europe/Paris",
        latitude=48.8566,
        longitude=2.3522,
        reference_version="1.0.0",
        ruleset_version="1.0.0",
        debug_mode=False,
    )


def test_hash_stable(orchestrator, base_input):
    """AC3 - Same input × 2 → same hash."""
    hash1 = orchestrator._compute_hash(base_input)
    hash2 = orchestrator._compute_hash(base_input)
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_hash_changes_on_diff(orchestrator, base_input):
    """AC3 - Changing local_date → different hash."""
    hash1 = orchestrator._compute_hash(base_input)

    modified_input = EngineInput(
        natal_chart=base_input.natal_chart,
        local_date=date(2026, 3, 8),  # Changed date
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        debug_mode=base_input.debug_mode,
    )
    hash2 = orchestrator._compute_hash(modified_input)
    assert hash1 != hash2


def test_local_to_ut_paris(orchestrator):
    """AC4 - 2026-03-07 + Europe/Paris → intervalle UT exact attendu."""
    local_date = date(2026, 3, 7)
    timezone = "Europe/Paris"

    jd_start, jd_end = orchestrator._local_date_to_ut_interval(local_date, timezone)

    assert jd_start == pytest.approx(2461106.4583333335, abs=1e-6)
    assert jd_end == pytest.approx(2461107.4583333335, abs=1e-6)
    assert jd_end - jd_start == pytest.approx(1.0, abs=1e-5)


def test_output_has_mandatory_fields(orchestrator, base_input):
    """AC2 - All EngineOutput fields present."""
    output = orchestrator.run(base_input)
    assert isinstance(output, EngineOutput)
    assert "run_metadata" in output.__dict__
    assert output.run_metadata["computed_at"] == "2026-03-06T23:00:00+00:00"
    assert output.run_metadata["jd_interval"] == [
        pytest.approx(2461106.4583333335, abs=1e-6),
        pytest.approx(2461107.4583333335, abs=1e-6),
    ]
    assert output.effective_context is not None
    assert isinstance(output.sampling_timeline, list)
    assert isinstance(output.detected_events, list)
    assert isinstance(output.category_scores, dict)
    assert isinstance(output.time_blocks, list)
    assert isinstance(output.turning_points, list)


def test_house_system_fields_present(orchestrator, base_input):
    """AC5 - house_system_requested and effective present."""
    output = orchestrator.run(base_input)
    ctx = output.effective_context
    assert ctx.house_system_requested == "whole_sign"
    assert ctx.house_system_effective == "whole_sign"


def test_determinism(orchestrator, base_input):
    """AC6 - Two identical runs → identical EngineOutput."""
    output1 = orchestrator.run(base_input)
    output2 = orchestrator.run(base_input)

    assert output1 == output2


def test_debug_mode_propagated(orchestrator, base_input):
    """Le debug_mode d'entrée est propagé dans run_metadata."""
    debug_input = EngineInput(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        debug_mode=True,
    )

    output = orchestrator.run(debug_input)

    assert output.run_metadata["debug_mode"] is True


def test_invalid_timezone_raises_prediction_context_error(orchestrator, base_input):
    """Un fuseau IANA invalide doit lever une erreur métier stable."""
    invalid_input = EngineInput(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone="Mars/Olympus_Mons",
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        debug_mode=base_input.debug_mode,
    )

    with pytest.raises(PredictionContextError, match="Unknown IANA timezone"):
        orchestrator.run(invalid_input)


def test_missing_ruleset_context_raises_prediction_context_error(base_input):
    """Un ruleset introuvable doit lever une erreur métier stable."""
    orchestrator = EngineOrchestrator(ruleset_context_loader=lambda _: None)

    with pytest.raises(PredictionContextError, match="Ruleset context not found"):
        orchestrator.run(base_input)
