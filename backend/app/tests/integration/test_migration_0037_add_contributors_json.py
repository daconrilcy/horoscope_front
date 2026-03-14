from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_migration_0037_is_idempotent_when_column_already_exists(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "migration-0037.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260307_0036")

    engine = create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE daily_prediction_category_scores ADD COLUMN contributors_json TEXT")
        )

    command.upgrade(config, "head")

    with engine.connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        columns = {
            column["name"]
            for column in inspect(connection).get_columns("daily_prediction_category_scores")
        }

    assert revision == ScriptDirectory.from_config(config).get_current_head()
    assert "contributors_json" in columns
