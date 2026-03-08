from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models import (
    AspectModel,
    AspectProfileModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    PredictionRulesetModel,
    ReferenceVersionModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
    SignRulershipModel,
)
from app.services.reference_data_service import ReferenceDataService
from scripts.seed_31_prediction_reference_v2 import SeedAbortError, run_seed


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _sqlite_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _setup_engine(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, db_name: str) -> Engine:
    db_path = tmp_path / db_name
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    # Upgrade to the latest migration before seed
    command.upgrade(_alembic_config(), "head")
    return _sqlite_engine(database_url)


def test_seed_31_prediction_v2_full_flow(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    engine = _setup_engine(monkeypatch, tmp_path, "test-seed-v2.db")

    with Session(engine) as session:
        # 1. Setup V1.0.0
        ReferenceDataService.seed_reference_version(session, "1.0.0")
        session.commit()

        # 2. Run seed script logic
        run_seed(session)
        session.commit()

        # 3. Verify counts
        v2 = session.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0")
        )
        assert v2 is not None
        assert v2.is_locked is True
        assert v2.description == (
            "Moteur de prédiction quotidienne v1 — référentiel sémantique complet"
        )

        assert (
            session.scalar(
                select(func.count())
                .select_from(PredictionCategoryModel)
                .where(PredictionCategoryModel.reference_version_id == v2.id)
            )
            == 12
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(PlanetProfileModel)
                .join(PlanetModel, PlanetProfileModel.planet_id == PlanetModel.id)
                .where(PlanetModel.reference_version_id == v2.id)
            )
            == 10
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(HouseProfileModel)
                .join(HouseModel, HouseProfileModel.house_id == HouseModel.id)
                .where(HouseModel.reference_version_id == v2.id)
            )
            == 12
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(AspectProfileModel)
                .join(AspectModel, AspectProfileModel.aspect_id == AspectModel.id)
                .where(AspectModel.reference_version_id == v2.id)
            )
            == 5
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(AstroPointModel)
                .where(AstroPointModel.reference_version_id == v2.id)
            )
            == 4
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(SignRulershipModel)
                .where(SignRulershipModel.reference_version_id == v2.id)
            )
            == 12
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(PlanetCategoryWeightModel)
                .join(PlanetModel, PlanetCategoryWeightModel.planet_id == PlanetModel.id)
                .where(PlanetModel.reference_version_id == v2.id)
            )
            >= 30
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(HouseCategoryWeightModel)
                .join(HouseModel, HouseCategoryWeightModel.house_id == HouseModel.id)
                .where(HouseModel.reference_version_id == v2.id)
            )
            >= 20
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(PointCategoryWeightModel)
                .join(AstroPointModel, PointCategoryWeightModel.point_id == AstroPointModel.id)
                .where(AstroPointModel.reference_version_id == v2.id)
            )
            == 8
        )

        ruleset_v1 = session.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "1.0.0"
            )
        )
        assert ruleset_v1 is not None
        
        ruleset_v2 = session.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "2.0.0"
            )
        )
        assert ruleset_v2 is not None

        assert (
            session.scalar(
                select(func.count())
                .select_from(RulesetEventTypeModel)
                .where(RulesetEventTypeModel.ruleset_id.in_([ruleset_v1.id, ruleset_v2.id]))
            )
            == 16
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(RulesetParameterModel)
                .where(RulesetParameterModel.ruleset_id.in_([ruleset_v1.id, ruleset_v2.id]))
            )
            == 16
        )

        # 4. Verify idempotence (already seeded and locked)
        # Should not raise any error and just return
        run_seed(session)

    engine.dispose()


def test_seed_31_prediction_v2_idempotence_corrupted_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    engine = _setup_engine(monkeypatch, tmp_path, "test-seed-v2-corrupted.db")

    with Session(engine) as session:
        # 1. Setup V1.0.0
        ReferenceDataService.seed_reference_version(session, "1.0.0")

        # 2. Partially seed V2.0.0 manually
        v2 = ReferenceVersionModel(version="2.0.0", description="Corrupted", is_locked=False)
        session.add(v2)
        session.commit()

        # 3. Running run_seed should raise SeedAbortError as per AC15 case 3
        with pytest.raises(SeedAbortError):
            run_seed(session)

    engine.dispose()
