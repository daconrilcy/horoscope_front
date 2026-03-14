import uuid
from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel


def create_user(db: Session, email: str = "test@example.com") -> UserModel:
    user = UserModel(email=email, password_hash="...", role="user")
    db.add(user)
    db.flush()
    return user


def create_user_birth_profile(db: Session, user_id: int) -> UserBirthProfileModel:
    profile = UserBirthProfileModel(
        user_id=user_id,
        birth_date=date(1990, 1, 1),
        birth_time=None,
        birth_place="Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
        birth_timezone="Europe/Paris",
    )
    db.add(profile)
    db.flush()
    return profile


def create_chart_result(db: Session, user_id: int) -> ChartResultModel:
    payload = {
        "planets": [
            {"code": "sun", "longitude": 10.0},
            {"code": "moon", "longitude": 20.0},
            {"code": "mercury", "longitude": 30.0},
            {"code": "venus", "longitude": 40.0},
            {"code": "mars", "longitude": 50.0},
            {"code": "jupiter", "longitude": 60.0},
            {"code": "saturn", "longitude": 70.0},
            {"code": "uranus", "longitude": 80.0},
            {"code": "neptune", "longitude": 90.0},
            {"code": "pluto", "longitude": 100.0},
        ],
        "angles": {"asc": {"longitude": 0.0}, "mc": {"longitude": 270.0}},
        "house_cusps": [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    }
    chart = ChartResultModel(
        user_id=user_id,
        chart_id=str(uuid.uuid4()),
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        input_hash="hash_natal",
        result_payload=payload,
        created_at=datetime.now(UTC),
    )
    db.add(chart)
    db.flush()
    return chart


def create_reference_version(db: Session, version: str = "1.0.0") -> ReferenceVersionModel:
    ref = ReferenceVersionModel(version=version, is_locked=False)
    db.add(ref)
    db.flush()
    return ref


def create_prediction_ruleset(
    db: Session, ref_id: int, version: str = "1.0.0"
) -> PredictionRulesetModel:
    ruleset = PredictionRulesetModel(
        reference_version_id=ref_id, version=version, house_system="placidus"
    )
    db.add(ruleset)
    db.flush()
    return ruleset


def create_prediction_category(
    db: Session, ref_id: int, code: str = "work"
) -> PredictionCategoryModel:
    cat = PredictionCategoryModel(
        reference_version_id=ref_id,
        code=code,
        name=code.capitalize(),
        display_name=code.capitalize(),
        sort_order=1,
        is_enabled=True,
    )
    db.add(cat)
    db.flush()
    return cat
