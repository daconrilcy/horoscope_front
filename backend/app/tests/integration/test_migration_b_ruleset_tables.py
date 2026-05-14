"""Tests du schéma historique de la migration B des rulesets de prédiction."""

from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings

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
    command.upgrade(_alembic_config(), "20260308_0041")
    return _sqlite_engine(database_url)


def _seed_reference_version(session: Session, *, version: str, is_locked: bool) -> SimpleNamespace:
    result = session.execute(
        text(
            """
            INSERT INTO reference_versions (version, description, is_locked, created_at)
            VALUES (:version, :description, :is_locked, :created_at)
            """
        ),
        {
            "version": version,
            "description": f"Seed for {version}",
            "is_locked": is_locked,
            "created_at": datetime.now(timezone.utc),
        },
    )
    session.commit()
    return SimpleNamespace(id=result.lastrowid, version=version, is_locked=is_locked)


def _seed_ruleset(
    session: Session, ref_version: SimpleNamespace, *, version: str = "1.0.0"
) -> SimpleNamespace:
    result = session.execute(
        text(
            """
            INSERT INTO prediction_rulesets (
                version,
                reference_version_id,
                zodiac_type,
                coordinate_mode,
                house_system,
                time_step_minutes,
                description,
                is_locked
            )
            VALUES (
                :version,
                :reference_version_id,
                'tropical',
                'geocentric',
                'placidus',
                30,
                'Test ruleset',
                0
            )
            """
        ),
        {"version": version, "reference_version_id": ref_version.id},
    )
    session.commit()
    return SimpleNamespace(id=result.lastrowid, version=version)


def _seed_prediction_category(session: Session, ref_version: SimpleNamespace) -> SimpleNamespace:
    result = session.execute(
        text(
            """
            INSERT INTO prediction_categories (
                reference_version_id,
                code,
                name,
                display_name
            )
            VALUES (:reference_version_id, 'career', 'Career', 'Career')
            """
        ),
        {"reference_version_id": ref_version.id},
    )
    session.commit()
    return SimpleNamespace(id=result.lastrowid, code="career")


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

        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    """
                    INSERT INTO prediction_rulesets (
                        version,
                        reference_version_id,
                        zodiac_type,
                        coordinate_mode,
                        house_system,
                        time_step_minutes,
                        is_locked
                    )
                    VALUES (
                        '1.0.0',
                        :reference_version_id,
                        'tropical',
                        'geocentric',
                        'placidus',
                        30,
                        0
                    )
                    """
                ),
                {"reference_version_id": ref_version.id},
            )
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

        session.execute(
            text(
                """
                INSERT INTO ruleset_event_types (ruleset_id, code, name, base_weight)
                VALUES (:ruleset_id, 'aspect_exact', 'Aspect Exact', 2.0)
                """
            ),
            {"ruleset_id": ruleset.id},
        )
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    """
                    INSERT INTO ruleset_event_types (ruleset_id, code, name)
                    VALUES (:ruleset_id, 'aspect_exact', 'Duplicate')
                    """
                ),
                {"ruleset_id": ruleset.id},
            )
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

        session.execute(
            text(
                """
                INSERT INTO ruleset_parameters (ruleset_id, param_key, param_value, data_type)
                VALUES (:ruleset_id, 'orb_multiplier', '1.2', 'float')
                """
            ),
            {"ruleset_id": ruleset.id},
        )
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    """
                    INSERT INTO ruleset_parameters (ruleset_id, param_key, param_value)
                    VALUES (:ruleset_id, 'orb_multiplier', '1.5')
                    """
                ),
                {"ruleset_id": ruleset.id},
            )
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

        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    """
                    INSERT INTO ruleset_parameters (ruleset_id, param_key, param_value, data_type)
                    VALUES (:ruleset_id, 'bad_param', 'value', 'invalid_type')
                    """
                ),
                {"ruleset_id": ruleset.id},
            )
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

        category = _seed_prediction_category(session, ref_version)

        session.execute(
            text(
                """
                INSERT INTO category_calibrations (ruleset_id, category_id, p50, valid_from)
                VALUES (:ruleset_id, :category_id, 50.0, :valid_from)
                """
            ),
            {
                "ruleset_id": ruleset.id,
                "category_id": category.id,
                "valid_from": date(2024, 1, 1),
            },
        )
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(
                text(
                    """
                    INSERT INTO category_calibrations (ruleset_id, category_id, p50, valid_from)
                    VALUES (:ruleset_id, :category_id, 60.0, :valid_from)
                    """
                ),
                {
                    "ruleset_id": ruleset.id,
                    "category_id": category.id,
                    "valid_from": date(2024, 1, 1),
                },
            )
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
