from datetime import date

import pytest

from app.infra.db.repositories.prediction_schemas import (
    CategoryData,
    HouseCategoryWeightData,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.exceptions import PredictionContextError
from app.prediction.schemas import EngineInput, EngineOutput


def _build_loaded_context() -> LoadedPredictionContext:
    all_planet_profiles: dict[str, PlanetProfileData] = {}
    for planet_id, name in enumerate(
        (
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ),
        start=1,
    ):
        profile = PlanetProfileData(
            planet_id=planet_id,
            code=name.lower(),
            name=name,
            class_code="planet",
            speed_rank=planet_id,
            speed_class="variable",
            weight_intraday=1.0,
            weight_day_climate=1.0,
            typical_polarity=None,
            orb_active_deg=5.0,
            orb_peak_deg=1.5,
            keywords=(name.lower(),),
        )
        all_planet_profiles[name] = profile
        all_planet_profiles[name.lower()] = profile

    prediction_context = PredictionContext(
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
        planet_profiles=all_planet_profiles,
        house_profiles={},
        planet_category_weights=(
            PlanetCategoryWeightData(
                planet_id=1,
                planet_code="sun",
                category_id=1,
                category_code="work",
                weight=0.5,
                influence_role="driver",
            ),
        ),
        house_category_weights=(
            HouseCategoryWeightData(
                house_id=1,
                house_number=10,
                category_id=1,
                category_code="work",
                weight=1.0,
                routing_role="primary",
            ),
        ),
        sign_rulerships={
            "aries": "mars",
            "taurus": "venus",
            "gemini": "mercury",
            "cancer": "moon",
            "leo": "sun",
            "virgo": "mercury",
            "libra": "venus",
            "scorpio": "mars",
            "sagittarius": "jupiter",
            "capricorn": "saturn",
            "aquarius": "saturn",
            "pisces": "jupiter",
        },
        aspect_profiles={},
        astro_points={},
        point_category_weights=(),
    )
    ruleset_context = RulesetContext(
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
        parameters={
            "ns_weight_occ": 0.1,
            "ns_weight_rul": 0.1,
            "ns_weight_ang": 0.1,
            "ns_weight_dom": 0.0,
        },
        event_types={},
    )
    return LoadedPredictionContext(
        prediction_context=prediction_context,
        ruleset_context=ruleset_context,
        calibrations={"work": None},
        is_provisional_calibration=True,
    )


@pytest.fixture
def orchestrator():
    return EngineOrchestrator(
        prediction_context_loader=lambda *_: _build_loaded_context()
    )


@pytest.fixture
def base_input():
    return EngineInput(
        natal_chart={
            "planets": [
                {"code": "sun", "longitude": 80.5, "house": 3},
                {"code": "moon", "longitude": 120.2, "house": 5},
                {"code": "saturn", "longitude": 275.0, "house": 1},
            ],
            "houses": [
                {"number": house_number, "cusp_longitude": float((house_number - 1) * 30)}
                for house_number in range(1, 13)
            ],
            "angles": {
                "ASC": {"longitude": 0.0},
                "MC": {"longitude": 270.0},
            },
        },
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
    """Integrated run returns the mandatory EngineOutput fields."""
    output = orchestrator.run(base_input)
    assert isinstance(output, EngineOutput)
    assert "run_metadata" in output.__dict__
    assert output.run_metadata["computed_at"] == "2026-03-06T23:00:00+00:00"
    assert output.run_metadata["is_provisional_calibration"] is True
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
    assert len(output.sampling_timeline) == 96
    assert len(output.detected_events) >= 24
    assert output.category_scores["work"] > 0.0


def test_house_system_fields_present(orchestrator, base_input):
    """AC5 - house_system_requested and effective present."""
    output = orchestrator.run(base_input)
    ctx = output.effective_context
    assert ctx.house_system_requested == "whole_sign"
    assert ctx.house_system_effective == "placidus"


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


def test_missing_prediction_context_raises_prediction_context_error(base_input):
    """Un contexte introuvable doit lever une erreur métier stable."""
    orchestrator = EngineOrchestrator(prediction_context_loader=lambda *_: None)

    with pytest.raises(PredictionContextError, match="Prediction context not found"):
        orchestrator.run(base_input)


def test_run_integrates_chapter_33_components(orchestrator, base_input):
    """The orchestrator wires the chapter 33 components into a real pipeline."""
    output = orchestrator.run(base_input)

    planetary_hours = [
        event for event in output.detected_events if event.event_type == "planetary_hour_change"
    ]
    assert len(planetary_hours) == 24
    assert output.effective_context.house_system_effective == "placidus"
