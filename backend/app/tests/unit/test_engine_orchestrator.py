from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.infra.db.repositories.prediction_schemas import (
    AspectProfileData,
    CategoryData,
    EventTypeData,
    HouseCategoryWeightData,
    HouseProfileData,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.engine_orchestrator import DailyEngineMode, EngineOrchestrator
from app.prediction.exceptions import PredictionContextError
from app.prediction.input_hash import compute_engine_input_hash
from app.prediction.schemas import (
    AstroEvent,
    EngineInput,
    PersistablePredictionBundle,
    PlanetState,
    SamplePoint,
)
from app.prediction.temporal_sampler import DayGrid


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
        calibration_label="provisional",
    )


@pytest.fixture
def orchestrator():
    return EngineOrchestrator(prediction_context_loader=lambda *_: _build_loaded_context())


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
    hash1 = compute_engine_input_hash(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
    )
    hash2 = compute_engine_input_hash(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
    )
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_hash_changes_on_diff(orchestrator, base_input):
    """AC3 - Changing local_date → different hash."""
    hash1 = compute_engine_input_hash(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
    )

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
    hash2 = compute_engine_input_hash(
        natal_chart=modified_input.natal_chart,
        local_date=modified_input.local_date,
        timezone=modified_input.timezone,
        latitude=modified_input.latitude,
        longitude=modified_input.longitude,
        reference_version=modified_input.reference_version,
        ruleset_version=modified_input.ruleset_version,
    )
    assert hash1 != hash2


def test_hash_changes_when_engine_identity_changes(base_input) -> None:
    hash_v2 = compute_engine_input_hash(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        engine_mode="v2",
    )
    hash_v3 = compute_engine_input_hash(
        natal_chart=base_input.natal_chart,
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        engine_mode="v3",
        engine_version="v3.1.0",
        snapshot_version="2.0",
        evidence_pack_version="3.0",
    )

    assert hash_v2 != hash_v3


def test_hash_canonicalizes_nested_values_and_enums() -> None:
    class HouseSystem(Enum):
        PLACIDUS = "placidus"

    hash1 = compute_engine_input_hash(
        natal_chart={
            "angles": {},
            "metadata": {"house_system": HouseSystem.PLACIDUS, "as_of": date(2026, 3, 8)},
            "planets": [{"code": "sun", "longitude": 1.0}],
        },
        local_date=date(2026, 3, 8),
        timezone="Europe/Paris",
        latitude=48.8566,
        longitude=2.3522,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )
    hash2 = compute_engine_input_hash(
        natal_chart={
            "planets": [{"longitude": 1.0, "code": "sun"}],
            "metadata": {"as_of": date(2026, 3, 8), "house_system": HouseSystem.PLACIDUS},
            "angles": {},
        },
        local_date=date(2026, 3, 8),
        timezone="Europe/Paris",
        latitude=48.8566,
        longitude=2.3522,
        reference_version="2.0.0",
        ruleset_version="2.0.0",
    )

    assert hash1 == hash2


def test_local_to_ut_paris(orchestrator):
    """AC4 - 2026-03-07 + Europe/Paris → intervalle UT exact attendu."""
    local_date = date(2026, 3, 7)
    timezone = "Europe/Paris"

    jd_start, jd_end = orchestrator._local_date_to_ut_interval(local_date, timezone)

    assert jd_start == pytest.approx(2461106.4583333335, abs=1e-6)
    assert jd_end == pytest.approx(2461107.4583333335, abs=1e-6)
    assert jd_end - jd_start == pytest.approx(1.0, abs=1e-5)


def test_output_has_mandatory_fields(orchestrator, base_input):
    """Integrated run returns the mandatory fields via PersistablePredictionBundle."""
    bundle = orchestrator.run(base_input)
    assert isinstance(bundle, PersistablePredictionBundle)
    core = bundle.core
    assert "run_metadata" in core.__dict__
    assert core.run_metadata["computed_at"] == "2026-03-06T23:00:00+00:00"
    assert core.run_metadata["is_provisional_calibration"] is True
    assert core.run_metadata["jd_interval"] == [
        pytest.approx(2461106.4583333335, abs=1e-6),
        pytest.approx(2461107.4583333335, abs=1e-6),
    ]
    assert core.effective_context is not None
    assert isinstance(core.sampling_timeline, list)
    assert isinstance(core.detected_events, list)
    assert isinstance(core.category_scores, dict)
    assert isinstance(bundle.editorial, object)
    assert isinstance(core.time_blocks, list)
    assert isinstance(core.turning_points, list)
    assert len(core.sampling_timeline) == 96
    assert len(core.detected_events) >= 24
    assert 1 <= core.category_scores["work"]["note_20"] <= 20
    assert core.category_scores["work"]["raw_score"] is not None
    assert core.category_scores["work"]["power"] is not None
    assert bundle.editorial is not None
    assert bundle.editorial.data.overall_tone in {"positive", "negative", "mixed", "neutral"}
    assert len(core.time_blocks) >= 1


def test_house_system_fields_present(orchestrator, base_input):
    """AC5 - house_system_requested and effective present."""
    bundle = orchestrator.run(base_input)
    ctx = bundle.core.effective_context
    assert ctx.house_system_requested == "whole_sign"
    assert ctx.house_system_effective == "placidus"


def test_determinism(orchestrator, base_input):
    """AC6 - Two identical runs → identical result."""
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

    bundle = orchestrator.run(debug_input)

    assert bundle.core.run_metadata["debug_mode"] is True


def test_run_can_skip_editorial_generation(orchestrator, base_input):
    bundle = orchestrator.run(base_input, include_editorial=False)

    assert bundle.editorial is None


def test_run_can_render_editorial_text_with_configurable_language(base_input):
    captured = {}

    class StubEditorialService:
        def generate_bundle(self, core_output, lang: str = "fr"):
            captured["core"] = core_output
            captured["lang"] = lang
            return MagicMock()

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: _build_loaded_context(),
        editorial_service=StubEditorialService(),
    )

    bundle = orchestrator.run(
        base_input,
        include_editorial_text=True,
        editorial_text_lang="en",
    )

    assert bundle.editorial is not None
    assert captured["lang"] == "en"


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
    bundle = orchestrator.run(base_input)
    core = bundle.core

    planetary_hours = [
        event for event in core.detected_events if event.event_type == "planetary_hour_change"
    ]
    assert len(planetary_hours) == 24
    assert core.effective_context.house_system_effective == "placidus"


def test_run_integrates_prediction_scoring_pipeline_with_lowercase_reference_codes(base_input):
    profile = PlanetProfileData(
        planet_id=1,
        code="sun",
        name="Sun",
        class_code="planet",
        speed_rank=1,
        speed_class="variable",
        weight_intraday=1.2,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    loaded_context = LoadedPredictionContext(
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
            planet_profiles={"sun": profile},
            house_profiles={
                10: HouseProfileData(
                    house_id=10,
                    number=10,
                    name="Career",
                    house_kind="angular",
                    visibility_weight=1.0,
                    base_priority=5,
                    keywords=("career",),
                ),
            },
            planet_category_weights=(
                PlanetCategoryWeightData(
                    planet_id=1,
                    planet_code="sun",
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    influence_role="driver",
                ),
            ),
            house_category_weights=(
                HouseCategoryWeightData(
                    house_id=10,
                    house_number=10,
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    routing_role="primary",
                ),
            ),
            sign_rulerships={"leo": "sun"},
            aspect_profiles={
                "conjunction": AspectProfileData(
                    aspect_id=1,
                    code="conjunction",
                    intensity_weight=1.0,
                    default_valence="positive",
                    orb_multiplier=1.0,
                    phase_sensitive=True,
                ),
            },
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
                house_system="whole_sign",
                time_step_minutes=15,
                is_locked=True,
            ),
            parameters={
                "ns_weight_occ": 0.0,
                "ns_weight_rul": 0.0,
                "ns_weight_ang": 0.0,
                "ns_weight_dom": 0.0,
            },
            event_types={
                "exact": EventTypeData(
                    id=1,
                    code="exact",
                    name="Exact",
                    event_group="aspect",
                    priority=90,
                    base_weight=1.0,
                )
            },
        ),
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )
    samples = [
        SamplePoint(
            ut_time=float(index),
            local_time=datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
            + timedelta(minutes=15 * index),
        )
        for index in range(4)
    ]

    class StubTemporalSampler:
        def build_day_grid(self, *_args):
            return DayGrid(
                samples=samples,
                ut_start=0.0,
                ut_end=3.0,
                sunrise_ut=None,
                sunset_ut=None,
                local_date=date(2026, 3, 7),
                timezone="UTC",
            )

    class StubAstroCalculator:
        def __init__(self, *_args):
            pass

        def compute_step(self, ut_time: float, local_time: datetime):
            return SimpleNamespace(
                ut_jd=ut_time,
                local_time=local_time,
                house_system_effective="placidus",
            )

    class StubEventDetector:
        def __init__(self, *_args):
            pass

        def detect(self, *_args):
            return [
                AstroEvent(
                    event_type="aspect_exact_to_angle",  # MC is an angle target
                    ut_time=0.0,
                    local_time=samples[0].local_time,
                    body="Sun",
                    target="MC",
                    aspect="conjunction",
                    orb_deg=0.0,
                    priority=90,
                    base_weight=1.0,
                    metadata={
                        "phase": "exact",
                        "natal_house_target": 10,
                        "natal_house_transited": 10,
                    },
                )
            ]

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: loaded_context,
        temporal_sampler=StubTemporalSampler(),
        astro_calculator_factory=lambda *_: StubAstroCalculator(),
        event_detector_factory=lambda *_: StubEventDetector(),
    )

    bundle = orchestrator.run(base_input)
    core = bundle.core

    assert core.category_scores["work"]["note_20"] > 10
    assert bundle.editorial is not None
    assert bundle.editorial.data.top3_categories[0].code == "work"
    # Temporal spreading smooths the 4-step signal: no step-to-step delta >= 2
    # → 0 turning points; block generator produces 1 block for the whole mini-day.
    assert len(core.turning_points) == 0
    assert len(core.time_blocks) == 1


def test_run_v3_coexistence(orchestrator, base_input):
    """AC2/AC7 - Test that V3 core is returned when requested, without breaking V2."""
    bundle = orchestrator.run(base_input, engine_mode=DailyEngineMode.DUAL)

    assert bundle.core is not None
    assert bundle.v3_core is not None
    assert bundle.v3_core.engine_version == settings.v3_engine_version
    assert bundle.v3_core.run_metadata["mode"] == DailyEngineMode.DUAL.value
    assert bundle.core.run_metadata["engine_mode"] == DailyEngineMode.DUAL.value


def test_run_v3_only_returns_v3_skeleton(orchestrator, base_input):
    """AC2 - Test V3 ONLY mode."""
    bundle = orchestrator.run(base_input, engine_mode=DailyEngineMode.V3)

    assert bundle.v3_core is not None
    assert bundle.v3_core.engine_version == settings.v3_engine_version
    assert bundle.core is not None
    assert bundle.core.turning_points == []
    assert bundle.core.time_blocks == []
    assert bundle.core.run_metadata["engine_mode"] == DailyEngineMode.V3.value


def test_run_v3_only_skips_v2_pipeline(base_input):
    turning_point_detector = MagicMock()
    block_generator = MagicMock()
    decision_window_builder = MagicMock()

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: _build_loaded_context(),
        turning_point_detector=turning_point_detector,
        block_generator=block_generator,
        decision_window_builder=decision_window_builder,
    )

    orchestrator.run(base_input, engine_mode=DailyEngineMode.V3)

    turning_point_detector.detect.assert_not_called()
    block_generator.generate.assert_not_called()
    decision_window_builder.build.assert_not_called()


def test_run_v3_is_deterministic(orchestrator, base_input):
    output1 = orchestrator.run(base_input, engine_mode=DailyEngineMode.V3)
    output2 = orchestrator.run(base_input, engine_mode=DailyEngineMode.V3)

    assert output1 == output2


def test_build_natal_chart_uses_contextual_aspect_profiles(base_input):
    loaded_context = _build_loaded_context()
    loaded_context = replace(
        loaded_context,
        prediction_context=replace(
            loaded_context.prediction_context,
            aspect_profiles={
                "square": AspectProfileData(
                    aspect_id=2,
                    code="square",
                    intensity_weight=1.8,
                    default_valence="negative",
                    orb_multiplier=0.5,
                    phase_sensitive=False,
                )
            },
        ),
    )
    orchestrator = EngineOrchestrator(prediction_context_loader=lambda *_: loaded_context)

    natal_chart_payload = {
        "planets": [
            {"code": "sun", "longitude": 0.0, "house": 1},
            {"code": "moon", "longitude": 92.0, "house": 4},
        ],
        "houses": base_input.natal_chart["houses"],
        "angles": base_input.natal_chart["angles"],
    }
    natal_cusps = orchestrator._extract_house_cusps(natal_chart_payload)

    natal_chart = orchestrator._build_natal_chart(
        natal_chart_payload,
        natal_cusps,
        loaded_context,
    )

    square = next(
        aspect for aspect in natal_chart.natal_aspects if aspect.aspect == "square"
    )
    assert square.base_weight == pytest.approx(1.8)
    assert square.metadata["default_valence"] == "negative"
    assert square.metadata["orb_max"] == pytest.approx(2.5)


def test_run_v3_exposes_transit_diagnostics_and_signal(base_input):
    profile = PlanetProfileData(
        planet_id=1,
        code="sun",
        name="Sun",
        class_code="planet",
        speed_rank=1,
        speed_class="variable",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=4.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    loaded_context = LoadedPredictionContext(
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
            planet_profiles={"sun": profile, "Sun": profile},
            house_profiles={
                10: HouseProfileData(
                    house_id=10,
                    number=10,
                    name="Career",
                    house_kind="angular",
                    visibility_weight=1.0,
                    base_priority=5,
                    keywords=("career",),
                ),
            },
            planet_category_weights=(
                PlanetCategoryWeightData(
                    planet_id=1,
                    planet_code="sun",
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    influence_role="primary",
                ),
            ),
            house_category_weights=(
                HouseCategoryWeightData(
                    house_id=10,
                    house_number=10,
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    routing_role="primary",
                ),
            ),
            sign_rulerships={"leo": "sun"},
            aspect_profiles={
                "conjunction": AspectProfileData(
                    aspect_id=1,
                    code="conjunction",
                    intensity_weight=1.0,
                    default_valence="positive",
                    orb_multiplier=1.0,
                    phase_sensitive=True,
                ),
            },
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
                house_system="whole_sign",
                time_step_minutes=15,
                is_locked=True,
            ),
            parameters={
                "v3_b_weight_occ": 0.0,
                "v3_b_weight_rul": 0.0,
                "v3_b_weight_ang": 0.0,
                "v3_b_weight_asp": 0.0,
            },
            event_types={
                "aspect_exact_to_luminary": EventTypeData(
                    id=1,
                    code="aspect_exact_to_luminary",
                    name="Exact luminary",
                    event_group="aspect",
                    priority=90,
                    base_weight=1.0,
                ),
                "aspect_exact_to_angle": EventTypeData(
                    id=2,
                    code="aspect_exact_to_angle",
                    name="Exact angle",
                    event_group="aspect",
                    priority=90,
                    base_weight=1.0,
                ),
                "aspect_exact_to_personal": EventTypeData(
                    id=3,
                    code="aspect_exact_to_personal",
                    name="Exact personal",
                    event_group="aspect",
                    priority=90,
                    base_weight=1.0,
                ),
            },
        ),
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )
    samples = [
        SamplePoint(
            ut_time=float(index),
            local_time=datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
            + timedelta(minutes=15 * index),
        )
        for index in range(3)
    ]

    longitudes = [102.0, 100.0, 102.0]

    class StubTemporalSampler:
        def build_day_grid(self, *_args):
            return DayGrid(
                samples=samples,
                ut_start=0.0,
                ut_end=2.0,
                sunrise_ut=None,
                sunset_ut=None,
                local_date=date(2026, 3, 7),
                timezone="UTC",
            )

    class StubAstroCalculator:
        def __init__(self, *_args):
            self._index = 0

        def compute_step(self, ut_time: float, local_time: datetime):
            longitude = longitudes[self._index]
            self._index += 1
            return SimpleNamespace(
                ut_jd=ut_time,
                local_time=local_time,
                house_system_effective="placidus",
                ascendant_deg=0.0,
                mc_deg=270.0,
                house_cusps=[],
                planets={
                    "Sun": PlanetState(
                        code="Sun",
                        longitude=longitude,
                        speed_lon=1.0,
                        is_retrograde=False,
                        sign_code=3,
                        natal_house_transited=10,
                    )
                },
            )

    class StubEventDetector:
        def __init__(self, *_args):
            pass

        def detect(self, *_args):
            return []

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: loaded_context,
        temporal_sampler=StubTemporalSampler(),
        astro_calculator_factory=lambda *_: StubAstroCalculator(),
        event_detector_factory=lambda *_: StubEventDetector(),
    )
    engine_input = EngineInput(
        natal_chart={
            "planets": [{"code": "sun", "longitude": 100.0, "house": 10}],
            "houses": base_input.natal_chart["houses"],
            "angles": base_input.natal_chart["angles"],
        },
        local_date=base_input.local_date,
        timezone=base_input.timezone,
        latitude=base_input.latitude,
        longitude=base_input.longitude,
        reference_version=base_input.reference_version,
        ruleset_version=base_input.ruleset_version,
        debug_mode=False,
    )

    bundle = orchestrator.run(
        engine_input,
        engine_mode=DailyEngineMode.V3,
        include_editorial=False,
    )

    transit_values = [
        layer.transit for layer in bundle.v3_core.theme_signals["work"].timeline.values()
    ]
    assert max(transit_values) > 0.0
    assert bundle.v3_core.run_metadata["v3_transit_signal"]["performance"]["sample_count"] == 3
    assert bundle.v3_core.run_metadata["v3_transit_signal"]["themes"]["work"]["top_contributors"]


def test_run_v3_exposes_intraday_activation_diagnostics_and_secondary_runtime(base_input):
    profile = PlanetProfileData(
        planet_id=1,
        code="sun",
        name="Sun",
        class_code="luminary",
        speed_rank=1,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=4.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    loaded_context = LoadedPredictionContext(
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
            planet_profiles={"sun": profile, "Sun": profile},
            house_profiles={},
            planet_category_weights=(
                PlanetCategoryWeightData(
                    planet_id=1,
                    planet_code="Sun",
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    influence_role="primary",
                ),
            ),
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
                house_system="whole_sign",
                time_step_minutes=15,
                is_locked=True,
            ),
            parameters={
                "v3_b_weight_occ": 0.0,
                "v3_b_weight_rul": 0.0,
                "v3_b_weight_ang": 0.0,
                "v3_b_weight_asp": 0.0,
            },
            event_types={
                "planetary_hour_change": EventTypeData(
                    id=1,
                    code="planetary_hour_change",
                    name="Planetary hour change",
                    event_group="timing",
                    priority=20,
                    base_weight=0.8,
                ),
                "asc_sign_change": EventTypeData(
                    id=2,
                    code="asc_sign_change",
                    name="Asc sign change",
                    event_group="ingress",
                    priority=50,
                    base_weight=1.0,
                ),
            },
        ),
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )
    samples = [
        SamplePoint(
            ut_time=float(index),
            local_time=datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
            + timedelta(minutes=15 * index),
        )
        for index in range(2)
    ]

    class StubTemporalSampler:
        def build_day_grid(self, *_args):
            return DayGrid(
                samples=samples,
                ut_start=0.0,
                ut_end=1.0,
                sunrise_ut=0.0,
                sunset_ut=0.5,
                local_date=date(2026, 3, 7),
                timezone="UTC",
            )

    class StubAstroCalculator:
        def __init__(self, *_args):
            pass

        def compute_step(self, ut_time: float, local_time: datetime):
            return SimpleNamespace(
                ut_jd=ut_time,
                local_time=local_time,
                house_system_effective="placidus",
                ascendant_deg=0.0,
                mc_deg=0.0,
                house_cusps=[],
                planets={},
            )

    class StubEventDetector:
        def __init__(self, *_args):
            pass

        def detect(self, *_args):
            return [
                AstroEvent(
                    event_type="planetary_hour_change",
                    ut_time=0.0,
                    local_time=samples[0].local_time,
                    body="Sun",
                    target=None,
                    aspect=None,
                    orb_deg=0.0,
                    priority=20,
                    base_weight=0.8,
                    metadata={"hour_number": 1},
                )
            ]

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: loaded_context,
        temporal_sampler=StubTemporalSampler(),
        astro_calculator_factory=lambda *_: StubAstroCalculator(),
        event_detector_factory=lambda *_: StubEventDetector(),
    )

    bundle = orchestrator.run(
        base_input,
        engine_mode=DailyEngineMode.V3,
        include_editorial=False,
    )

    aspect_values = [
        layer.aspect for layer in bundle.v3_core.theme_signals["work"].timeline.values()
    ]
    assert max(aspect_values) > 0.0
    assert (
        bundle.v3_core.run_metadata["v3_intraday_activation"]["performance"]["sample_count"] == 2
    )
    assert bundle.v3_core.run_metadata["v3_intraday_activation"]["themes"]["work"][
        "top_contributors"
    ]


def test_run_v3_exposes_impulse_diagnostics_and_keeps_moon_ingress_out_of_a_layer(base_input):
    sun_profile = PlanetProfileData(
        planet_id=1,
        code="sun",
        name="Sun",
        class_code="luminary",
        speed_rank=1,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    moon_profile = PlanetProfileData(
        planet_id=2,
        code="moon",
        name="Moon",
        class_code="luminary",
        speed_rank=2,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("moon",),
    )
    loaded_context = LoadedPredictionContext(
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
            planet_profiles={
                "Sun": sun_profile,
                "sun": sun_profile,
                "Moon": moon_profile,
                "moon": moon_profile,
            },
            house_profiles={},
            planet_category_weights=(
                PlanetCategoryWeightData(
                    planet_id=1,
                    planet_code="Sun",
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    influence_role="primary",
                ),
            ),
            house_category_weights=(
                HouseCategoryWeightData(
                    house_id=10,
                    house_number=10,
                    category_id=1,
                    category_code="work",
                    weight=1.0,
                    routing_role="primary",
                ),
            ),
            sign_rulerships={},
            aspect_profiles={
                "conjunction": AspectProfileData(
                    aspect_id=1,
                    code="conjunction",
                    intensity_weight=1.0,
                    default_valence="positive",
                    orb_multiplier=1.0,
                    phase_sensitive=True,
                ),
            },
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
                house_system="whole_sign",
                time_step_minutes=15,
                is_locked=True,
            ),
            parameters={
                "v3_b_weight_occ": 0.0,
                "v3_b_weight_rul": 0.0,
                "v3_b_weight_ang": 0.0,
                "v3_b_weight_asp": 0.0,
            },
            event_types={
                "aspect_exact_to_angle": EventTypeData(
                    id=1,
                    code="aspect_exact_to_angle",
                    name="Exact angle",
                    event_group="aspect",
                    priority=90,
                    base_weight=1.0,
                ),
                "moon_sign_ingress": EventTypeData(
                    id=2,
                    code="moon_sign_ingress",
                    name="Moon ingress",
                    event_group="ingress",
                    priority=60,
                    base_weight=0.6,
                ),
            },
        ),
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )
    samples = [
        SamplePoint(
            ut_time=float(index),
            local_time=datetime(2026, 3, 7, 0, 0, tzinfo=timezone.utc)
            + timedelta(minutes=15 * index),
        )
        for index in range(2)
    ]

    class StubTemporalSampler:
        def build_day_grid(self, *_args):
            return DayGrid(
                samples=samples,
                ut_start=0.0,
                ut_end=1.0,
                sunrise_ut=None,
                sunset_ut=None,
                local_date=date(2026, 3, 7),
                timezone="UTC",
            )

    class StubAstroCalculator:
        def __init__(self, *_args):
            pass

        def compute_step(self, ut_time: float, local_time: datetime):
            return SimpleNamespace(
                ut_jd=ut_time,
                local_time=local_time,
                house_system_effective="placidus",
                ascendant_deg=0.0,
                mc_deg=0.0,
                house_cusps=[],
                planets={
                    "Sun": PlanetState(
                        code="Sun",
                        longitude=80.5,
                        speed_lon=1.0,
                        is_retrograde=False,
                        sign_code=2,
                        natal_house_transited=10,
                    )
                },
            )

    class StubEventDetector:
        def __init__(self, *_args):
            pass

        def detect(self, *_args):
            return [
                AstroEvent(
                    event_type="aspect_exact_to_angle",
                    ut_time=0.0,
                    local_time=samples[0].local_time,
                    body="Sun",
                    target="Asc",
                    aspect="conjunction",
                    orb_deg=0.0,
                    priority=90,
                    base_weight=1.0,
                    metadata={
                        "phase": "exact",
                        "natal_house_target": 10,
                        "natal_house_transited": 10,
                    },
                ),
                AstroEvent(
                    event_type="moon_sign_ingress",
                    ut_time=0.0,
                    local_time=samples[0].local_time,
                    body="Moon",
                    target=None,
                    aspect=None,
                    orb_deg=0.0,
                    priority=60,
                    base_weight=0.6,
                    metadata={"from_sign": 1, "to_sign": 2, "natal_house_target": 10},
                ),
            ]

    orchestrator = EngineOrchestrator(
        prediction_context_loader=lambda *_: loaded_context,
        temporal_sampler=StubTemporalSampler(),
        astro_calculator_factory=lambda *_: StubAstroCalculator(),
        event_detector_factory=lambda *_: StubEventDetector(),
    )

    bundle = orchestrator.run(
        base_input,
        engine_mode=DailyEngineMode.V3,
        include_editorial=False,
    )

    first_layer = next(iter(bundle.v3_core.theme_signals["work"].timeline.values()))
    assert first_layer.transit > 0.0
    assert first_layer.aspect == 0.0
    assert first_layer.event > 0.0
    assert (
        bundle.v3_core.run_metadata["v3_impulse_signal"]["performance"]["impulse_event_count"]
        == 2
    )
    assert bundle.v3_core.run_metadata["v3_impulse_signal"]["themes"]["work"]["top_contributors"]
