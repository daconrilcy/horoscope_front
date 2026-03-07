from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import (
    CategoryCalibrationModel,
    PredictionRulesetModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.models.reference import ReferenceVersionModel

NEW_TABLES_B = [
    "prediction_rulesets",
    "ruleset_event_types",
    "ruleset_parameters",
    "category_calibrations",
]

EXPECTED_INDEXES_B = {
    "prediction_rulesets": {"ix_prediction_rulesets_reference_version_id"},
    "ruleset_event_types": {"ix_ruleset_event_types_ruleset_id"},
    "ruleset_parameters": {"ix_ruleset_parameters_ruleset_id"},
    "category_calibrations": {
        "ix_category_calibrations_category_id",
        "ix_category_calibrations_ruleset_id",
    },
}


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _sqlite_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        del _
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _setup_engine(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, db_name: str) -> Engine:
    db_path = tmp_path / db_name
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    command.upgrade(_alembic_config(), "20260307_0033")
    return _sqlite_engine(database_url)


def _seed_reference_version(
    session: Session, *, version: str, is_locked: bool
) -> ReferenceVersionModel:
    reference_version = ReferenceVersionModel(
        version=version,
        description=f"Seed for {version}",
        is_locked=is_locked,
        created_at=datetime.now(timezone.utc),
    )
    session.add(reference_version)
    session.commit()
    return reference_version


def _seed_ruleset(
    session: Session, ref_version: ReferenceVersionModel, *, version: str = "1.0.0"
) -> PredictionRulesetModel:
    ruleset = PredictionRulesetModel(
        version=version,
        reference_version_id=ref_version.id,
        description="Test ruleset",
    )
    session.add(ruleset)
    session.commit()
    return ruleset


def test_migration_b_tables_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-tables.db")
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())
    for table in NEW_TABLES_B:
        assert table in tables, f"Table {table} was not created by Alembic"

    for table_name, expected_indexes in EXPECTED_INDEXES_B.items():
        index_names = {index["name"] for index in inspector.get_indexes(table_name)}
        assert expected_indexes.issubset(index_names), (
            f"Missing indexes on {table_name}: {expected_indexes - index_names}"
        )

    engine.dispose()


def test_migration_b_ruleset_unique_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-ruleset-unique.db")

    with Session(engine) as session:
        ref_version = _seed_reference_version(session, version="1.0.0", is_locked=False)
        _seed_ruleset(session, ref_version, version="1.0.0")

        duplicate = PredictionRulesetModel(
            version="1.0.0",
            reference_version_id=ref_version.id,
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    engine.dispose()


def test_migration_b_event_type_unique_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-event-unique.db")

    with Session(engine) as session:
        ref_version = _seed_reference_version(session, version="1.0.0", is_locked=False)
        ruleset = _seed_ruleset(session, ref_version)

        session.add(
            RulesetEventTypeModel(
                ruleset_id=ruleset.id, code="aspect_exact", name="Aspect Exact", base_weight=2.0
            )
        )
        session.commit()

        duplicate = RulesetEventTypeModel(
            ruleset_id=ruleset.id, code="aspect_exact", name="Duplicate"
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    engine.dispose()


def test_migration_b_parameter_unique_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-param-unique.db")

    with Session(engine) as session:
        ref_version = _seed_reference_version(session, version="1.0.0", is_locked=False)
        ruleset = _seed_ruleset(session, ref_version)

        session.add(
            RulesetParameterModel(
                ruleset_id=ruleset.id,
                param_key="orb_multiplier",
                param_value="1.2",
                data_type="float",
            )
        )
        session.commit()

        duplicate = RulesetParameterModel(
            ruleset_id=ruleset.id, param_key="orb_multiplier", param_value="1.5"
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    engine.dispose()


def test_migration_b_parameter_data_type_check_constraint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-param-check.db")

    with Session(engine) as session:
        ref_version = _seed_reference_version(session, version="1.0.0", is_locked=False)
        ruleset = _seed_ruleset(session, ref_version)

        invalid = RulesetParameterModel(
            ruleset_id=ruleset.id,
            param_key="bad_param",
            param_value="value",
            data_type="invalid_type",
        )
        session.add(invalid)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    engine.dispose()


def test_migration_b_calibration_unique_constraint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-b-calib-unique.db")

    with Session(engine) as session:
        ref_version = _seed_reference_version(session, version="1.0.0", is_locked=False)
        ruleset = _seed_ruleset(session, ref_version)

        category = PredictionCategoryModel(
            reference_version_id=ref_version.id,
            code="career",
            name="Career",
            display_name="Career",
        )
        session.add(category)
        session.commit()

        session.add(
            CategoryCalibrationModel(
                ruleset_id=ruleset.id,
                category_id=category.id,
                p50=50.0,
                valid_from=date(2024, 1, 1),
            )
        )
        session.commit()

        duplicate = CategoryCalibrationModel(
            ruleset_id=ruleset.id,
            category_id=category.id,
            valid_from=date(2024, 1, 1),
            p50=60.0,
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    engine.dispose()


def test_migration_b_downgrade_and_reupgrade(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test-b-downgrade.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260307_0033")
    command.downgrade(config, "20260307_0032")

    engine = _sqlite_engine(database_url)
    tables_after_downgrade = set(inspect(engine).get_table_names())
    for table in NEW_TABLES_B:
        assert table not in tables_after_downgrade, f"Table {table} still exists after downgrade"
    engine.dispose()

    # Verify the migration can be re-applied cleanly (idempotency cycle)
    command.upgrade(config, "20260307_0033")
    engine = _sqlite_engine(database_url)
    tables_after_reupgrade = set(inspect(engine).get_table_names())
    for table in NEW_TABLES_B:
        assert table in tables_after_reupgrade, f"Table {table} missing after re-upgrade"
    engine.dispose()
