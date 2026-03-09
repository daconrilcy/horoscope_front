from pathlib import Path

from sqlalchemy import create_engine, inspect

from app.infra.db import bootstrap


def test_auto_upgrade_creates_auth_tables_for_local_sqlite(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-local.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    test_engine = create_engine(database_url, future=True)

    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        tables = set(inspect(test_engine).get_table_names())
        assert "users" in tables
        assert "user_refresh_tokens" in tables
        assert "audit_events" in tables
    finally:
        test_engine.dispose()


def test_auto_upgrade_creates_required_llm_tables_for_local_sqlite(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-local-llm.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    test_engine = create_engine(database_url, future=True)

    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        tables = set(inspect(test_engine).get_table_names())
        assert "llm_personas" in tables
        assert "llm_use_case_configs" in tables
        assert "llm_prompt_versions" in tables
    finally:
        test_engine.dispose()
