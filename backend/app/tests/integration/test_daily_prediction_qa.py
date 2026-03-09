# backend/app/tests/integration/test_daily_prediction_qa.py
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
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
from app.infra.db.session import SessionLocal
from app.main import app
from app.services.auth_service import AuthService
from app.services.reference_data_service import ReferenceDataService
from app.tests.fixtures.intraday_qa_fixtures import (
    get_active_day,
    get_calm_day,
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
}


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
    return auth.tokens.access_token


def _fetch_prediction_for_fixture(fixture_name: str) -> dict:
    fixture_data = FIXTURE_BUILDERS[fixture_name]()
    with SessionLocal() as db:
        token = _setup_qa_user_and_natal(db, fixture_data=fixture_data)

    with SessionLocal() as db:
        db.execute(delete(DailyPredictionRunModel))
        db.commit()

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


@pytest.mark.parametrize("fixture_name", ["calm_day", "active_day", "transition_day"])
def test_fixture_expectations_match_api_response(fixture_name: str):
    result = _fetch_prediction_for_fixture(fixture_name)
    fixture_data = result["fixture"]
    report = build_report(result["payload"])

    assert_fixture_expectations(
        report,
        expected_pivot_range=fixture_data["expected_pivot_range"],
        expected_window_range=fixture_data["expected_window_range"],
    )


def test_intraday_go_nogo():
    for fixture_name in ["active_day", "transition_day"]:
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
