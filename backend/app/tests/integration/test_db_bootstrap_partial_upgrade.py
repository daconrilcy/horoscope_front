from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.infra.db import bootstrap


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def test_auto_upgrade_moves_existing_local_sqlite_from_intermediate_revision_to_head(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-partial-upgrade.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    config = _alembic_config()
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    command.upgrade(config, "20260307_0036")

    test_engine = create_engine(database_url, future=True)
    with test_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (email, password_hash, role, created_at, updated_at) "
                "VALUES ("
                "'bootstrap@example.com', 'hash', 'user', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP"
                ")"
            )
        )

    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        with test_engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            user_count = connection.execute(
                text("SELECT COUNT(*) FROM users WHERE email='bootstrap@example.com'")
            ).scalar_one()
        assert revision == bootstrap._head_revision()
        assert user_count == 1
    finally:
        test_engine.dispose()


def test_auto_upgrade_repairs_missing_llm_tables_even_when_revision_is_head(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-head-missing-llm.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    config = _alembic_config()
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    command.upgrade(config, "head")

    test_engine = create_engine(database_url, future=True)
    with test_engine.begin() as connection:
        connection.execute(text("DROP TABLE llm_prompt_versions"))

    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        tables = set(inspect(test_engine).get_table_names())
        assert "llm_prompt_versions" in tables
    finally:
        test_engine.dispose()
