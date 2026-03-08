# backend/app/tests/integration/test_daily_prediction_qa.py
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
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
from scripts.seed_31_prediction_reference_v2 import run_seed

client = TestClient(app)


def _reset_prediction_reference(db) -> None:
    """Ensure the prediction reference used by the QA flow is fully re-seeded."""
    rulesets = (
        db.query(PredictionRulesetModel)
        .filter(PredictionRulesetModel.version.in_(["1.0.0", "2.0.0"]))
        .all()
    )
    for ruleset in rulesets:
        db.execute(
            delete(CategoryCalibrationModel).where(
                CategoryCalibrationModel.ruleset_id == ruleset.id
            )
        )
        db.execute(
            delete(RulesetParameterModel).where(RulesetParameterModel.ruleset_id == ruleset.id)
        )
        db.execute(
            delete(RulesetEventTypeModel).where(RulesetEventTypeModel.ruleset_id == ruleset.id)
        )
        db.delete(ruleset)
    db.flush()

    version = (
        db.query(ReferenceVersionModel)
        .filter(ReferenceVersionModel.version == "2.0.0")
        .first()
    )
    if version is None:
        return

    db.execute(
        delete(PointCategoryWeightModel).where(
            PointCategoryWeightModel.point_id.in_(
                db.query(AstroPointModel.id).filter(
                    AstroPointModel.reference_version_id == version.id
                )
            )
        )
    )
    db.execute(delete(AstroPointModel).where(AstroPointModel.reference_version_id == version.id))
    db.execute(
        delete(HouseCategoryWeightModel).where(
            HouseCategoryWeightModel.house_id.in_(
                db.query(HouseModel.id).filter(HouseModel.reference_version_id == version.id)
            )
        )
    )
    db.execute(
        delete(PlanetCategoryWeightModel).where(
            PlanetCategoryWeightModel.planet_id.in_(
                db.query(PlanetModel.id).filter(PlanetModel.reference_version_id == version.id)
            )
        )
    )
    db.execute(
        delete(PlanetProfileModel).where(
            PlanetProfileModel.planet_id.in_(
                db.query(PlanetModel.id).filter(PlanetModel.reference_version_id == version.id)
            )
        )
    )
    db.execute(
        delete(HouseProfileModel).where(
            HouseProfileModel.house_id.in_(
                db.query(HouseModel.id).filter(HouseModel.reference_version_id == version.id)
            )
        )
    )
    db.execute(
        delete(SignRulershipModel).where(SignRulershipModel.reference_version_id == version.id)
    )
    db.execute(
        delete(AspectProfileModel).where(
            AspectProfileModel.aspect_id.in_(
                db.query(AspectModel.id).filter(AspectModel.reference_version_id == version.id)
            )
        )
    )
    db.execute(
        delete(PredictionCategoryModel).where(
            PredictionCategoryModel.reference_version_id == version.id
        )
    )
    db.execute(
        delete(AstroCharacteristicModel).where(
            AstroCharacteristicModel.reference_version_id == version.id
        )
    )
    db.execute(delete(AspectModel).where(AspectModel.reference_version_id == version.id))
    db.execute(delete(HouseModel).where(HouseModel.reference_version_id == version.id))
    db.execute(delete(SignModel).where(SignModel.reference_version_id == version.id))
    db.execute(delete(PlanetModel).where(PlanetModel.reference_version_id == version.id))
    db.delete(version)
    db.flush()


def _ensure_prediction_reference_seed(db) -> None:
    ReferenceDataService._clear_cache_for_tests()
    _reset_prediction_reference(db)
    ReferenceDataService.seed_reference_version(db, "1.0.0")
    run_seed(db)
    db.commit()


@pytest.fixture(autouse=True)
def setup_db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "active_reference_version", "2.0.0")
    monkeypatch.setattr(settings, "ruleset_version", "1.0.0")
    with SessionLocal() as db:
        db.execute(delete(DailyPredictionRunModel))
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(ChartResultModel))
        db.execute(delete(UserModel))
        db.commit()
        _ensure_prediction_reference_seed(db)


def _setup_qa_user_and_natal(db):
    auth = AuthService.register(
        db, email="qa-integration@example.com", password="strong-pass-123", role="user"
    )
    db.commit()

    # Create birth profile
    birth_profile = UserBirthProfileModel(
        user_id=auth.user.id,
        birth_date=date(1990, 1, 1),
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.85,
        birth_lon=2.35,
        current_lat=48.85,
        current_lon=2.35,
        current_timezone="Europe/Paris",
    )
    db.add(birth_profile)

    # Create chart result
    chart_result = ChartResultModel(
        user_id=auth.user.id,
        chart_id=str(uuid.uuid4()),
        reference_version="2.0.0",
        ruleset_version="1.0.0",
        input_hash="integration_qa_hash",
        result_payload={
            "planets": {"Sun": 15.5, "Moon": 220.3},
            "house_cusps": [
                102.0, 132.0, 162.0, 192.0, 222.0, 252.0, 282.0, 312.0, 342.0, 12.0, 42.0, 72.0
            ],
        },
    )
    db.add(chart_result)
    db.commit()
    return auth.tokens.access_token


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
        "communication", "pleasure_creativity",
    }
    codes = {c["code"] for c in data["categories"]}
    assert codes == expected_codes, f"Expected categories {expected_codes}, got {codes}"


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
        assert code in all_codes, (
            f"bottom_categories contains unknown code '{code}'"
        )

    # The lowest-scoring category must appear in bottom_categories when present
    if bottom_categories and data["categories"]:
        sorted_by_note = sorted(data["categories"], key=lambda c: c["note_20"])
        worst_code = sorted_by_note[0]["code"]
        assert worst_code in bottom_categories, (
            f"Lowest-scoring category '{worst_code}' (note={sorted_by_note[0]['note_20']}) "
            f"absent from bottom_categories {bottom_categories}"
        )
