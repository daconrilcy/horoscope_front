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


def test_auto_upgrade_repairs_email_logs_sqlite_primary_key_shape(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-email-logs-repair.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    config = _alembic_config()
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    command.upgrade(config, "head")

    test_engine = create_engine(database_url, future=True)
    with test_engine.connect() as connection:
        before_type = {
            row[1]: row[2] for row in connection.execute(text("PRAGMA table_info(email_logs)"))
        }["id"]

    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        with test_engine.connect() as connection:
            after_type = {
                row[1]: row[2] for row in connection.execute(text("PRAGMA table_info(email_logs)"))
            }["id"]
        assert before_type == "BIGINT"
        assert after_type == "INTEGER"
    finally:
        test_engine.dispose()


def test_auto_upgrade_repairs_only_legacy_llm_call_logs_provider_column(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-llm-provider-repair.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    config = _alembic_config()
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    command.upgrade(config, "8a572a8336bf")

    test_engine = create_engine(database_url, future=True)
    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    with test_engine.begin() as connection:
        connection.execute(
            text("UPDATE alembic_version SET version_num = :version"),
            {"version": bootstrap._head_revision()},
        )
        before_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(llm_call_logs)"))
        }

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        with test_engine.connect() as connection:
            after_columns = {
                row[1] for row in connection.execute(text("PRAGMA table_info(llm_call_logs)"))
            }
            metadata_tables = set(inspect(test_engine).get_table_names())
        assert "provider" in before_columns
        assert "provider_compat" not in before_columns
        assert "provider" not in after_columns
        assert "provider_compat" not in after_columns
        assert "executed_provider_mode" not in after_columns
        assert "provider_error_code" not in after_columns
        assert "llm_call_log_operational_metadata" in metadata_tables
    finally:
        test_engine.dispose()


def test_auto_upgrade_repairs_stale_llm_call_logs_environment_constraint(
    monkeypatch: object, tmp_path: Path
) -> None:
    db_path = tmp_path / "bootstrap-llm-environment-repair.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    config = _alembic_config()
    monkeypatch.setattr(bootstrap.settings, "database_url", database_url)
    command.upgrade(config, "head")

    test_engine = create_engine(database_url, future=True)
    monkeypatch.setattr(bootstrap.settings, "app_env", "development")
    monkeypatch.setattr(bootstrap, "engine", test_engine)
    monkeypatch.setattr(bootstrap, "_is_pytest_runtime", lambda: False)

    with test_engine.begin() as connection:
        connection.execute(text("ALTER TABLE llm_call_logs RENAME TO llm_call_logs__old"))
        connection.execute(
            text(
                """
                CREATE TABLE llm_call_logs (
                    id NUMERIC NOT NULL PRIMARY KEY,
                    use_case VARCHAR(100) NOT NULL,
                    assembly_id NUMERIC NULL REFERENCES llm_assembly_configs (id),
                    feature VARCHAR(64) NULL,
                    subfeature VARCHAR(64) NULL,
                    "plan" VARCHAR(64) NULL,
                    template_source VARCHAR(32) NULL,
                    prompt_version_id NUMERIC NULL REFERENCES llm_prompt_versions (id),
                    persona_id NUMERIC NULL REFERENCES llm_personas (id),
                    model VARCHAR(100) NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    tokens_in INTEGER NOT NULL,
                    tokens_out INTEGER NOT NULL,
                    cost_usd_estimated FLOAT NOT NULL,
                    validation_status VARCHAR(14) NOT NULL,
                    repair_attempted BOOLEAN NOT NULL,
                    fallback_triggered BOOLEAN NOT NULL,
                    request_id VARCHAR(100) NOT NULL,
                    trace_id VARCHAR(100) NOT NULL,
                    input_hash VARCHAR(64) NOT NULL,
                    environment VARCHAR(20) NOT NULL,
                    evidence_warnings_count INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    expires_at DATETIME NOT NULL,
                    CONSTRAINT ck_llm_call_logs_environment CHECK (
                        environment IN ('dev', 'staging', 'prod', 'test', 'local')
                    )
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_call_logs
                SELECT
                    id, use_case, assembly_id, feature, subfeature, "plan", template_source,
                    prompt_version_id, persona_id, model, latency_ms, tokens_in, tokens_out,
                    cost_usd_estimated, validation_status, repair_attempted, fallback_triggered,
                    request_id, trace_id, input_hash, 'dev', evidence_warnings_count,
                    timestamp, expires_at
                FROM llm_call_logs__old
                """
            )
        )
        connection.execute(text("DROP TABLE llm_call_logs__old"))

    try:
        bootstrap.ensure_local_sqlite_schema_ready()

        with test_engine.begin() as connection:
            checks = connection.execute(
                text(
                    "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'llm_call_logs'"
                )
            ).scalar_one()
            connection.execute(
                text(
                    """
                    INSERT INTO llm_call_logs (
                        id, use_case, model, latency_ms, tokens_in, tokens_out, cost_usd_estimated,
                        validation_status, repair_attempted, fallback_triggered, request_id,
                        trace_id, input_hash, environment, evidence_warnings_count, timestamp,
                        expires_at
                    ) VALUES (
                        '00000000000000000000000000000001',
                        'bootstrap-test',
                        'gpt-4o',
                        0,
                        0,
                        0,
                        0.0,
                        'ERROR',
                        0,
                        0,
                        'req-bootstrap',
                        'trace-bootstrap',
                        'hash-bootstrap',
                        'development',
                        0,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    """
                )
            )
        assert "'development'" in checks
    finally:
        test_engine.dispose()
