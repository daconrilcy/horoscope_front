# backend/app/tests/integration/test_daily_prediction_qa.py
import statistics
import time
import uuid
from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import DailyEngineMode, settings
from app.core.versions import ACTIVE_REFERENCE_VERSION, ACTIVE_RULESET_VERSION
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    SignRulershipModel,
)
from app.infra.db.models.prediction_ruleset import (
    CategoryCalibrationModel,
    PredictionRulesetModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel
from app.infra.db.session import SessionLocal
from app.main import app
from app.prediction.schemas import CoreEngineOutput, EffectiveContext, PersistablePredictionBundle
from app.services.auth_service import AuthService
from app.services.reference_data_service import ReferenceDataService
from app.tests.fixtures.intraday_qa_fixtures import (
    get_active_day,
    get_ambiguous_day,
    get_calm_day,
    get_flat_day_no_signal,
    get_flat_day_with_micro_trends,
    get_intense_neutral_day,
    get_transition_day,
)
from app.tests.helpers.intraday_qa_report import (
    assert_fixture_expectations,
    assert_within_budget,
    build_report,
)
from scripts.seed_31_prediction_reference_v2 import run_seed

client = TestClient(app)

LEGACY_REFERENCE_VERSION = "1.0.0"
LEGACY_RULESET_VERSION = "1.0.0"
FIXTURE_BUILDERS = {
    "active_day": get_active_day,
    "calm_day": get_calm_day,
    "transition_day": get_transition_day,
    "flat_day_with_micro_trends": get_flat_day_with_micro_trends,
    "flat_day_no_signal": get_flat_day_no_signal,
    "ambiguous_day": get_ambiguous_day,
    "intense_neutral_day": get_intense_neutral_day,
}


def _build_mock_bundle(fixture_data: dict) -> PersistablePredictionBundle:
    target_date = date.fromisoformat(fixture_data["target_date"])
    avg_notes: dict[str, float] = {}
    for step in fixture_data["notes_by_step"]:
        for category_code, note in step.items():
            avg_notes[category_code] = avg_notes.get(category_code, 0.0) + float(note)

    for category_code in avg_notes:
        avg_notes[category_code] /= len(fixture_data["notes_by_step"])

    sorted_cats = sorted(avg_notes.items(), key=lambda item: item[1], reverse=True)
    editorial_category_scores = {
        category_code: {
            "note_20": int(note),
            "raw_score": float(note),
            "power": 1.0,
            "volatility": 0.0,
            "rank": index + 1,
            "is_provisional": False,
        }
        for index, (category_code, note) in enumerate(sorted_cats)
    }

    return PersistablePredictionBundle(
        core=CoreEngineOutput(
            effective_context=EffectiveContext(
                house_system_requested="placidus",
                house_system_effective="placidus",
                local_date=target_date,
                timezone="Europe/Paris",
                input_hash="mock_hash",
            ),
            run_metadata={
                "is_provisional_calibration": False,
                "calibration_label": "v2",
                "computed_at": datetime.now().isoformat(),
            },
            category_scores=editorial_category_scores,
            time_blocks=[
                {
                    "block_index": 0,
                    "start_at_local": datetime.combine(target_date, datetime.min.time()),
                    "end_at_local": datetime.combine(target_date, datetime.max.time()),
                    "tone_code": "neutral",
                    "dominant_categories": [],
                    "summary": "Calme",
                }
            ],
            turning_points=[],
            decision_windows=[],
            detected_events=[],
            sampling_timeline=[],
            explainability=None,
        ),
        editorial=None,
    )


def _reset_prediction_reference(db) -> None:
    """Ensure the prediction reference used by the QA flow is fully re-seeded."""
    db.execute(delete(CategoryCalibrationModel))
    db.execute(delete(RulesetParameterModel))
    db.execute(delete(RulesetEventTypeModel))
    db.execute(delete(PredictionRulesetModel))

    db.execute(delete(PointCategoryWeightModel))
    db.execute(delete(AstroPointModel))
    db.execute(delete(HouseCategoryWeightModel))
    db.execute(delete(PlanetCategoryWeightModel))
    db.execute(delete(PlanetProfileModel))
    db.execute(delete(HouseProfileModel))
    db.execute(delete(SignRulershipModel))
    db.execute(delete(AspectProfileModel))
    db.execute(delete(PredictionCategoryModel))
    db.execute(delete(AstroCharacteristicModel))
    db.execute(delete(AspectModel))
    db.execute(delete(HouseModel))
    db.execute(delete(SignModel))
    db.execute(delete(PlanetModel))
    db.execute(delete(ReferenceVersionModel))
    db.flush()


def _ensure_prediction_reference_seed(db) -> None:
    ReferenceDataService._clear_cache_for_tests()
    _reset_prediction_reference(db)
    db.commit()
    db.expire_all()
    ReferenceDataService.seed_reference_version(db, LEGACY_RULESET_VERSION)
    ReferenceDataService.seed_reference_version(db, ACTIVE_REFERENCE_VERSION)

    # Unlock the active reference to allow run_seed to populate prediction-specific rulesets.
    from app.infra.db.repositories.reference_repository import ReferenceRepository

    repo = ReferenceRepository(db)
    active_reference = repo.get_version(ACTIVE_REFERENCE_VERSION)
    if active_reference:
        active_reference.is_locked = False
        db.commit()

    run_seed(db)
    db.commit()


@pytest.fixture(autouse=True)
def setup_db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "active_reference_version", ACTIVE_REFERENCE_VERSION)
    monkeypatch.setattr(settings, "ruleset_version", ACTIVE_RULESET_VERSION)
    with SessionLocal() as db:
        db.execute(delete(DailyPredictionRunModel))
        db.execute(delete(UserPredictionBaselineModel))
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(ChartResultModel))
        db.execute(delete(UserModel))
        db.commit()
        _ensure_prediction_reference_seed(db)


def _setup_qa_user_and_natal(db, *, fixture_data: dict | None = None):
    auth = AuthService.register(
        db,
        email=f"qa-integration-{uuid.uuid4()}@example.com",
        password="strong-pass-123",
        role="user",
    )
    db.commit()

    natal = (
        fixture_data["simulated_natal_profile"]
        if fixture_data
        else {
            "birth_date": date(1990, 1, 1),
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "birth_lat": 48.85,
            "birth_lon": 2.35,
            "current_lat": 48.85,
            "current_lon": 2.35,
            "current_timezone": "Europe/Paris",
        }
    )

    # Create birth profile
    birth_profile = UserBirthProfileModel(
        user_id=auth.user.id,
        birth_date=date.fromisoformat(natal["birth_date"])
        if isinstance(natal["birth_date"], str)
        else natal["birth_date"],
        birth_place=natal["birth_place"],
        birth_timezone=natal["birth_timezone"],
        birth_lat=natal["birth_lat"],
        birth_lon=natal["birth_lon"],
        current_lat=natal["current_lat"],
        current_lon=natal["current_lon"],
        current_timezone=natal["current_timezone"],
    )
    db.add(birth_profile)

    # Create chart result
    chart_result = ChartResultModel(
        user_id=auth.user.id,
        chart_id=str(uuid.uuid4()),
        reference_version=settings.active_reference_version,
        ruleset_version=settings.active_ruleset_version,
        input_hash="integration_qa_hash",
        result_payload={
            "planets": {"Sun": 15.5, "Moon": 220.3},
            "house_cusps": [
                102.0,
                132.0,
                162.0,
                192.0,
                222.0,
                252.0,
                282.0,
                312.0,
                342.0,
                12.0,
                42.0,
                72.0,
            ],
        },
    )
    db.add(chart_result)
    db.commit()

    # Seed baselines if present in fixture
    if fixture_data and fixture_data.get("baselines"):
        from app.infra.db.repositories.prediction_reference_repository import (
            PredictionReferenceRepository,
        )
        from app.infra.db.repositories.prediction_ruleset_repository import (
            PredictionRulesetRepository,
        )
        from app.infra.db.repositories.reference_repository import ReferenceRepository

        ref_repo = ReferenceRepository(db)
        ruleset_repo = PredictionRulesetRepository(db)
        pred_ref_repo = PredictionReferenceRepository(db)

        ref_v = ref_repo.get_version(settings.active_reference_version)
        ruleset = ruleset_repo.get_ruleset(settings.ruleset_version)
        categories = pred_ref_repo.get_categories(ref_v.id)
        cat_map = {c.code: c.id for c in categories}

        target_date = date.fromisoformat(fixture_data["target_date"])
        window_days = 365
        start_date = target_date - timedelta(days=window_days - 1)

        for cat_code, stats in fixture_data["baselines"].items():
            cat_id = cat_map.get(cat_code)
            if not cat_id:
                continue

            baseline = UserPredictionBaselineModel(
                user_id=auth.user.id,
                category_id=cat_id,
                reference_version_id=ref_v.id,
                ruleset_id=ruleset.id,
                house_system_effective="placidus",
                window_days=window_days,
                window_start_date=start_date,
                window_end_date=target_date,
                mean_raw_score=stats["mean_raw_score"],
                std_raw_score=stats["std_raw_score"],
                mean_note_20=stats.get("mean_note_20", 10.0),
                std_note_20=stats.get("std_note_20", 2.0),
                p10=stats["p10"],
                p50=stats["p50"],
                p90=stats["p90"],
                sample_size_days=window_days,
            )
            db.add(baseline)
        db.flush()
        db.commit()

    return auth.tokens.access_token


def _fetch_prediction_for_fixture(fixture_name: str) -> dict:
    fixture_data = FIXTURE_BUILDERS[fixture_name]()
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db, fixture_data=fixture_data)

    with SessionLocal() as db:
        db.execute(delete(DailyPredictionRunModel))
        db.commit()

    # AC3: If fixture asks for mock engine, we mock EngineOrchestrator.run
    # This allows testing the assembler safeguards on controlled engine output.
    if fixture_data.get("mock_engine"):
        mock_bundle = _build_mock_bundle(fixture_data)

        with patch(
            "app.services.prediction_compute_runner.EngineOrchestrator.run",
            return_value=mock_bundle,
        ):
            response = client.get(
                "/v1/predictions/daily",
                headers={"Authorization": f"Bearer {token}"},
                params={"date": fixture_data["target_date"]},
            )
    else:
        response = client.get(
            "/v1/predictions/daily",
            headers={"Authorization": f"Bearer {token}"},
            params={"date": fixture_data["target_date"]},
        )

    assert response.status_code == 200
    return {"fixture": fixture_data, "payload": response.json()}


def test_categories_all_present():
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db)

    response = client.get(
        "/v1/predictions/daily",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": "2026-03-08"},
    )

    assert response.status_code == 200
    data = response.json()
    # Reference v2 defines exactly these 12 categories
    expected_codes = {
        "energy",
        "mood",
        "health",
        "work",
        "career",
        "money",
        "love",
        "sex_intimacy",
        "family_home",
        "social_network",
        "communication",
        "pleasure_creativity",
    }
    codes = {c["code"] for c in data["categories"]}
    assert codes == expected_codes, f"Expected categories {expected_codes}, got {codes}"


def test_legacy_ruleset_1_0_0_still_supported(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "ruleset_version", LEGACY_RULESET_VERSION)

    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db)

    response = client.get(
        "/v1/predictions/daily",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": "2026-03-08"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["reference_version"] == ACTIVE_REFERENCE_VERSION
    assert data["meta"]["ruleset_version"] == LEGACY_RULESET_VERSION
    assert data["categories"]


def test_notes_in_valid_range():
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db)

    response = client.get(
        "/v1/predictions/daily",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": "2026-03-08"},
    )

    assert response.status_code == 200
    data = response.json()
    for cat in data["categories"]:
        note = cat["note_20"]
        assert 1 <= note <= 20


def test_timeline_no_overlap():
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db)

    response = client.get(
        "/v1/predictions/daily",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": "2026-03-08"},
    )

    assert response.status_code == 200
    data = response.json()
    blocks = data["timeline"]
    for i in range(len(blocks) - 1):
        end_current = blocks[i]["end_local"]
        start_next = blocks[i + 1]["start_local"]
        # Comparison of ISO strings
        assert end_current <= start_next


def test_caution_flags_consistent():
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db)

    response = client.get(
        "/v1/predictions/daily",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": "2026-03-08"},
    )

    assert response.status_code == 200
    data = response.json()

    # Each category must expose the required fields
    for cat in data["categories"]:
        assert "code" in cat
        assert "note_20" in cat
        assert "summary" in cat

    # bottom_categories must be a valid list of known category codes (at most 2)
    all_codes = {c["code"] for c in data["categories"]}
    bottom_categories = data["summary"]["bottom_categories"]
    assert isinstance(bottom_categories, list)
    assert len(bottom_categories) <= 2
    for code in bottom_categories:
        assert code in all_codes, f"bottom_categories contains unknown code '{code}'"

    # The lowest-scoring category must appear in bottom_categories when present
    if bottom_categories and data["categories"]:
        sorted_by_note = sorted(data["categories"], key=lambda c: c["note_20"])
        worst_code = sorted_by_note[0]["code"]
        assert worst_code in bottom_categories, (
            f"Lowest-scoring category '{worst_code}' (note={sorted_by_note[0]['note_20']}) "
            f"absent from bottom_categories {bottom_categories}"
        )


# --- QA Actionability & Noise Budget Tests (Story 41.5) ---

MAX_DECISION_WINDOWS = 6
MAX_IDENTICAL_CONSECUTIVE_BLOCKS = 2
MAX_TECHNICAL_DRIVERS_VISIBLE = 0


def test_decision_windows_within_budget():
    result = _fetch_prediction_for_fixture("active_day")
    decision_windows = result["payload"].get("decision_windows") or []

    assert len(decision_windows) <= MAX_DECISION_WINDOWS
    for dw in decision_windows:
        assert dw["window_type"] in {"favorable", "prudence", "pivot"}


@pytest.mark.parametrize(
    "fixture_name",
    ["calm_day", "active_day", "transition_day", "ambiguous_day", "intense_neutral_day"],
)
def test_fixture_expectations_match_api_response(fixture_name: str):
    result = _fetch_prediction_for_fixture(fixture_name)
    fixture_data = result["fixture"]
    report = build_report(result["payload"])

    # AC2 Story 42.17: More flexible ranges for V2/V3 comparison
    pivot_range = fixture_data["expected_pivot_range"]
    window_range = fixture_data["expected_window_range"]

    if fixture_name == "active_day":
        pivot_range = (pivot_range[0], 6)
        window_range = (window_range[0], 6)

    assert_fixture_expectations(
        report,
        expected_pivot_range=pivot_range,
        expected_window_range=window_range,
    )


def test_intraday_go_nogo():
    # Active days must respect windows/identical blocks budget
    for fixture_name in ["active_day", "transition_day", "ambiguous_day", "intense_neutral_day"]:
        result = _fetch_prediction_for_fixture(fixture_name)
        fixture_data = result["fixture"]
        report = build_report(result["payload"])

        try:
            assert_within_budget(
                report,
                max_windows=MAX_DECISION_WINDOWS,
                max_identical_blocks=MAX_IDENTICAL_CONSECUTIVE_BLOCKS,
                max_technical_drivers=MAX_TECHNICAL_DRIVERS_VISIBLE,
            )
        except AssertionError as e:
            pytest.fail(
                f"QA Go/No-Go failed for {fixture_name} ({fixture_data['target_date']}):\n{str(e)}"
            )

    # Flat days must respect micro-trend budget (max 3)
    for fixture_name in ["flat_day_with_micro_trends", "flat_day_no_signal"]:
        result = _fetch_prediction_for_fixture(fixture_name)
        fixture_data = result["fixture"]
        report = build_report(result["payload"])

        try:
            assert_within_budget(
                report,
                max_windows=0,  # AC2: No windows on flat days
                max_identical_blocks=MAX_IDENTICAL_CONSECUTIVE_BLOCKS,
                max_technical_drivers=MAX_TECHNICAL_DRIVERS_VISIBLE,
                max_micro_trends=3,  # Story 41.14 AC3
            )
        except AssertionError as e:
            pytest.fail(
                f"QA Go/No-Go failed for {fixture_name} ({fixture_data['target_date']}):\n{str(e)}"
            )


# --- Relative Calibration QA Tests (Story 41.16) ---


def test_flat_day_with_micro_trends_qa():
    """
    Vérifie qu'une journée plate avec signal relatif expose des micro-tendances
    et respecte les garde-fous (pas de best_window, pas de pivots).
    """
    result = _fetch_prediction_for_fixture("flat_day_with_micro_trends")
    payload = result["payload"]

    # 1. Vérification du flag flat_day (AC1)
    assert payload["summary"]["flat_day"] is True

    # 2. Vérification des micro-tendances (AC1)
    assert payload["micro_trends"] is not None
    assert len(payload["micro_trends"]) > 0
    # On a seedé "love" avec un Z-score de 2.5
    love_trend = next((t for t in payload["micro_trends"] if t["category_code"] == "love"), None)
    assert love_trend is not None
    assert love_trend["z_score"] == 2.5

    # 3. Garde-fous (AC2)
    assert payload["summary"]["best_window"] is None
    assert payload["decision_windows"] is None or payload["decision_windows"] == []
    assert payload["turning_points"] == []

    # 4. Cohérence éditoriale (AC2)
    assert payload["summary"]["relative_summary"] is not None
    assert "amour" in payload["summary"]["relative_summary"].lower()


def test_flat_day_no_signal_qa():
    """
    Vérifie qu'une journée plate SANS signal relatif n'expose pas de micro-tendances.
    """
    result = _fetch_prediction_for_fixture("flat_day_no_signal")
    payload = result["payload"]

    assert payload["summary"]["flat_day"] is True
    # Z-score pour "love" est 0 (10-10)/2
    # La policy filtre les Z < 0.5
    assert payload["micro_trends"] == [] or payload["micro_trends"] is None


def test_active_day_unchanged_by_relative_calibration():
    """
    Vérifie qu'une journée active garde ses fenêtres absolues et n'est pas marquée 'flat_day'.
    """
    result = _fetch_prediction_for_fixture("active_day")
    payload = result["payload"]

    assert payload["summary"]["flat_day"] is False
    assert payload["summary"]["best_window"] is not None
    assert len(payload.get("decision_windows", [])) > 0
    # Même si on a une baseline, on n'affiche pas les micro-tendances sur journée active
    assert payload["micro_trends"] is None


def test_v2_v3_dual_comparison_qa():
    """
    AC1/AC3 Story 42.17: Compare V2 and V3 in DUAL mode.
    Implements all Gates from v3-migration-gates.md.
    """
    from app.prediction.context_loader import PredictionContextLoader
    from app.services.prediction_compute_runner import PredictionComputeRunner
    from app.services.prediction_request_resolver import PredictionRequestResolver

    # Use calm_day for Sobriety check
    fixture_data = get_calm_day()

    with SessionLocal() as db:
        _setup_qa_user_and_natal(db, fixture_data=fixture_data)
        resolver = PredictionRequestResolver()
        resolved = resolver.resolve(
            db,
            user_id=1,
            date_local=date.fromisoformat(fixture_data["target_date"]),
            include_engine_input=True,
        )

        runner = PredictionComputeRunner(context_loader=PredictionContextLoader())
        # AC1: Use DUAL mode
        result = runner.run_with_timeout(
            db, resolved.engine_input, engine_mode=DailyEngineMode.DUAL
        )
        bundle = result.bundle

        assert bundle.core is not None  # V2
        assert bundle.v3_core is not None  # V3

        # GATE 1: Pivot Sobriety (Ratio V3/V2 < 0.5 on calm days)
        # Note: If V2 has 0 pivots, ratio is undefined, we expect V3 to also have 0 or very few.
        v2_pivots = len(bundle.core.turning_points)
        v3_pivots = len(bundle.v3_core.turning_points)

        if v2_pivots > 0:
            ratio = v3_pivots / v2_pivots
            assert ratio <= 0.5, f"Sobriety Gate failed: Ratio V3/V2={ratio} > 0.5"
        else:
            assert v3_pivots <= 1, (
                "Sobriety Gate failed: V3 produced pivots on calm day where V2 produced 0"
            )

        # GATE 2: Scoring Expressivity (StdDev V3 > StdDev V2)
        v2_scores = [c["raw_score"] for c in bundle.core.category_scores.values()]
        v3_scores = [c.avg_score for c in bundle.v3_core.daily_metrics.values()]

        v2_std = statistics.stdev(v2_scores) if len(v2_scores) > 1 else 0
        v3_std = statistics.stdev(v3_scores) if len(v3_scores) > 1 else 0

        assert v3_std >= v2_std, (
            f"Expressivity Gate failed: V3 StdDev({v3_std}) < V2 StdDev({v2_std})"
        )

        # GATE 3: Window Precision (confidence > 0.7 for V3)
        if bundle.v3_core.decision_windows:
            for dw in bundle.v3_core.decision_windows:
                assert dw.confidence >= 0.7, (
                    f"Precision Gate failed: Window confidence {dw.confidence} < 0.7"
                )

        # GATE 4: Flat Day Integrity (No windows on intensity < 3.0)
        # We simulate this by checking calm_day (which is low intensity)
        if True:  # logic placeholder for calm day
            assert len(bundle.v3_core.decision_windows) == 0, (
                "Flat Day Integrity Gate failed: V3 produced windows on calm day"
            )

        print("\nQA V3 Gates Validation Success:")
        print(f"  Pivots: V2={v2_pivots}, V3={v3_pivots}")
        print(f"  Expressivity: V2 StdDev={v2_std:.2f}, V3 StdDev={v3_std:.2f}")


def test_v3_inter_run_stability():
    """
    Task 4 Story 42.17: Vérifier la stabilité inter-runs (idempotence).
    """
    from app.prediction.context_loader import PredictionContextLoader
    from app.services.prediction_compute_runner import PredictionComputeRunner
    from app.services.prediction_request_resolver import PredictionRequestResolver

    with SessionLocal() as db:
        _setup_qa_user_and_natal(db)
        resolver = PredictionRequestResolver()
        resolved = resolver.resolve(
            db, user_id=1, date_local=date(2026, 3, 8), include_engine_input=True
        )

        runner = PredictionComputeRunner(context_loader=PredictionContextLoader())

        # Run 1
        res1 = runner.run_with_timeout(db, resolved.engine_input, engine_mode=DailyEngineMode.V3)
        # Run 2
        res2 = runner.run_with_timeout(db, resolved.engine_input, engine_mode=DailyEngineMode.V3)

        # Compare category scores
        scores1 = {c_code: s.avg_score for c_code, s in res1.bundle.v3_core.daily_metrics.items()}
        scores2 = {c_code: s.avg_score for c_code, s in res2.bundle.v3_core.daily_metrics.items()}

        assert scores1 == scores2, (
            "Stability check failed: consecutive runs produced different scores"
        )
        assert len(res1.bundle.v3_core.turning_points) == len(res2.bundle.v3_core.turning_points)


def test_v3_runtime_slo():
    """
    Task 4 Story 42.17: Vérifier le respect des SLO runtime clés pour le run V3 end-to-end.

    Note:
    - Le budget micro-performance <100ms reste couvert par les tests unitaires ciblés.
    - Ici on verrouille un budget d'intégration plus stable en suite complète Windows/CI.
    """
    from app.prediction.context_loader import PredictionContextLoader
    from app.services.prediction_compute_runner import PredictionComputeRunner
    from app.services.prediction_request_resolver import PredictionRequestResolver

    with SessionLocal() as db:
        _setup_qa_user_and_natal(db)
        resolver = PredictionRequestResolver()
        resolved = resolver.resolve(
            db, user_id=1, date_local=date(2026, 3, 8), include_engine_input=True
        )

        runner = PredictionComputeRunner(context_loader=PredictionContextLoader())

        # Warmup
        runner.run_with_timeout(db, resolved.engine_input, engine_mode=DailyEngineMode.V3)

        samples_ms: list[float] = []
        for _ in range(3):
            start = time.perf_counter()
            runner.run_with_timeout(db, resolved.engine_input, engine_mode=DailyEngineMode.V3)
            samples_ms.append((time.perf_counter() - start) * 1000)

        median_ms = statistics.median(samples_ms)

        print(f"\nV3 Runtime samples: {[round(sample, 2) for sample in samples_ms]}")
        print(f"V3 Runtime median: {median_ms:.2f}ms")
        assert median_ms < 250.0, (
            f"Runtime SLO failed: median {median_ms:.2f}ms > 250ms (samples={samples_ms!r})"
        )
