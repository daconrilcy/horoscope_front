from datetime import datetime, timezone
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.prediction_reference import (
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PredictionCategoryModel,
)
from app.infra.db.models.reference import PlanetModel, ReferenceVersionModel

NEW_TABLES = [
    "prediction_categories",
    "planet_profiles",
    "house_profiles",
    "planet_category_weights",
    "house_category_weights",
    "astro_points",
    "point_category_weights",
    "sign_rulerships",
    "aspect_profiles",
]

EXPECTED_INDEXES = {
    "prediction_categories": {"ix_prediction_categories_reference_version_id"},
    "planet_profiles": {"ix_planet_profiles_planet_id"},
    "house_profiles": {"ix_house_profiles_house_id"},
    "planet_category_weights": {
        "ix_planet_category_weights_category_id",
        "ix_planet_category_weights_planet_id",
    },
    "house_category_weights": {
        "ix_house_category_weights_category_id",
        "ix_house_category_weights_house_id",
    },
    "astro_points": {"ix_astro_points_reference_version_id"},
    "point_category_weights": {
        "ix_point_category_weights_category_id",
        "ix_point_category_weights_point_id",
    },
    "sign_rulerships": {
        "ix_sign_rulerships_planet_id",
        "ix_sign_rulerships_reference_version_id",
        "ix_sign_rulerships_sign_id",
    },
    "aspect_profiles": {"ix_aspect_profiles_aspect_id"},
}


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _sqlite_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)

    @sa.event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        del _
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


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


def test_migration_a_prediction_tables_creation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test-migration-a.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260307_0032")

    engine = _sqlite_engine(database_url)
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())
    for table in NEW_TABLES:
        assert table in tables, f"Table {table} was not created by Alembic"

    for table_name, expected_indexes in EXPECTED_INDEXES.items():
        index_names = {index["name"] for index in inspector.get_indexes(table_name)}
        assert expected_indexes.issubset(index_names), (
            f"Missing indexes on {table_name}: {expected_indexes - index_names}"
        )

    with Session(engine) as session:
        unlocked_version = _seed_reference_version(session, version="1.0.0", is_locked=False)

        category = PredictionCategoryModel(
            reference_version_id=unlocked_version.id,
            code="love",
            name="Love",
            display_name="Love",
        )
        session.add(category)
        session.commit()

        duplicate_category = PredictionCategoryModel(
            reference_version_id=unlocked_version.id,
            code="love",
            name="Love Duplicate",
            display_name="Love Duplicate",
        )
        session.add(duplicate_category)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        planet = PlanetModel(
            reference_version_id=unlocked_version.id,
            code="sun",
            name="Sun",
        )
        session.add(planet)
        session.commit()

        category_weight = PlanetCategoryWeightModel(
            planet_id=planet.id,
            category_id=category.id,
            weight=0.8,
            influence_role="primary",
        )
        session.add(category_weight)
        session.commit()

        duplicate_weight = PlanetCategoryWeightModel(
            planet_id=planet.id,
            category_id=category.id,
            weight=0.4,
            influence_role="secondary",
        )
        session.add(duplicate_weight)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        invalid_profile = PlanetProfileModel(
            planet_id=999_999,
            class_code="luminary",
            speed_class="fast",
        )
        session.add(invalid_profile)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        locked_version = _seed_reference_version(session, version="2.0.0", is_locked=True)

        locked_category = PredictionCategoryModel(
            reference_version_id=locked_version.id,
            code="health",
            name="Health",
            display_name="Health",
        )
        session.add(locked_category)
        session.commit()

        locked_category.name = "Health Modified"
        with pytest.raises(ValueError, match="reference version is immutable"):
            session.commit()
        session.rollback()

        locked_planet = PlanetModel(
            reference_version_id=locked_version.id,
            code="moon",
            name="Moon",
        )
        session.add(locked_planet)
        session.commit()

        unlocked_profile = PlanetProfileModel(
            planet_id=locked_planet.id,
            class_code="luminary",
            speed_class="fast",
        )
        session.add(unlocked_profile)
        session.commit()

        unlocked_profile.class_code = "personal"
        session.commit()

    engine.dispose()


def test_migration_a_prediction_tables_downgrade(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test-migration-a-down.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260307_0032")
    command.downgrade(config, "20260307_0031")

    engine = _sqlite_engine(database_url)
    tables = set(inspect(engine).get_table_names())

    for table in NEW_TABLES:
        assert table not in tables, f"Table {table} still exists after downgrade"

    engine.dispose()
