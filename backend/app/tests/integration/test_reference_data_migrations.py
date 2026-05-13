from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.core.config import settings


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_reference_migrations_upgrade_and_downgrade(monkeypatch: object, tmp_path: Path) -> None:
    db_path = tmp_path / "migration-reference-test.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.downgrade(config, "base")
    command.upgrade(config, "20260218_0001")

    engine = create_engine(database_url, future=True)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "reference_versions" in tables
    assert "planets" in tables
    assert "signs" in tables
    assert "houses" in tables
    assert "aspects" in tables
    assert "astro_characteristics" in tables
    engine.dispose()

    command.upgrade(config, "head")

    head_engine = create_engine(database_url, future=True)
    head_inspector = inspect(head_engine)
    head_tables = set(head_inspector.get_table_names())
    assert "reference_versions" in head_tables
    assert "astro_characteristics" not in head_tables
    for table_name in ("planets", "signs", "houses", "aspects", "astro_points"):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" not in columns
    for table_name in (
        "planet_profiles",
        "house_profiles",
        "aspect_profiles",
        "planet_category_weights",
        "house_category_weights",
        "point_category_weights",
    ):
        columns = {column["name"] for column in head_inspector.get_columns(table_name)}
        assert "reference_version_id" in columns
    head_engine.dispose()

    command.downgrade(config, "base")

    downgraded_engine = create_engine(database_url, future=True)
    downgraded_tables = set(inspect(downgraded_engine).get_table_names())
    assert "reference_versions" not in downgraded_tables
    downgraded_engine.dispose()
