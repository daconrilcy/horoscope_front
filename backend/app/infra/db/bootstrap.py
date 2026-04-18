from __future__ import annotations

import logging
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.session import engine

logger = logging.getLogger(__name__)


def _is_pytest_runtime() -> bool:
    return "pytest" in sys.modules


def _should_auto_upgrade_local_sqlite() -> bool:
    if _is_pytest_runtime():
        return False
    if settings.app_env not in {"development", "dev", "local"}:
        return False
    if not settings._is_local_sqlite_database_url(settings.database_url):
        return False
    return ":memory:" not in settings.database_url


def _missing_declared_tables() -> set[str]:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    declared_tables = set(Base.metadata.tables)
    return declared_tables - existing_tables


def _current_revision() -> str | None:
    inspector = inspect(engine)
    if "alembic_version" not in inspector.get_table_names():
        return None

    with engine.connect() as connection:
        return connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()


def _iter_backend_root_candidates() -> tuple[Path, ...]:
    cwd = Path.cwd().resolve()
    module_path = Path(__file__).resolve()
    candidates: list[Path] = []

    for candidate in (cwd, cwd / "backend", *module_path.parents):
        if candidate not in candidates:
            candidates.append(candidate)

    return tuple(candidates)


def _resolve_backend_root() -> Path:
    for candidate in _iter_backend_root_candidates():
        if (candidate / "alembic.ini").exists() and (candidate / "migrations").exists():
            return candidate

    searched_locations = ", ".join(str(path) for path in _iter_backend_root_candidates())
    raise FileNotFoundError(
        f"Unable to locate backend root containing alembic.ini and migrations. "
        f"Searched: {searched_locations}"
    )


def _alembic_config(*, database_url: str | None = None) -> Config:
    backend_root = _resolve_backend_root()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option(
        "sqlalchemy.url", database_url if database_url is not None else settings.database_url
    )
    return config


def _head_revision() -> str:
    return ScriptDirectory.from_config(_alembic_config()).get_current_head()


def _repair_missing_tables(missing_tables: set[str]) -> None:
    tables_to_create = [
        table for table in Base.metadata.sorted_tables if table.name in missing_tables
    ]
    for table in tables_to_create:
        try:
            Base.metadata.create_all(bind=engine, tables=[table], checkfirst=True)
        except OperationalError as error:
            if "already exists" in str(error).lower():
                logger.warning(
                    "local_sqlite_schema_repair_table_exists database_url=%s table=%s",
                    settings.database_url,
                    table.name,
                )
                continue
            raise


def _table_columns(table_name: str) -> dict[str, dict[str, object]]:
    inspector = inspect(engine)
    return {str(column["name"]): column for column in inspector.get_columns(table_name)}


def _repair_email_logs_primary_key() -> bool:
    inspector = inspect(engine)
    if "email_logs" not in inspector.get_table_names():
        return False

    columns = _table_columns("email_logs")
    id_column = columns.get("id")
    if not id_column:
        return False

    column_type = str(id_column["type"]).upper()
    if column_type == "INTEGER":
        return False

    logger.warning(
        "local_sqlite_schema_repair_rebuild_email_logs old_id_type=%s",
        column_type,
    )
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE email_logs__rebuild (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NULL REFERENCES users (id),
                    email_type VARCHAR(50) NOT NULL,
                    recipient_email VARCHAR(255) NOT NULL,
                    sent_at DATETIME NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    provider_message_id VARCHAR(255) NULL,
                    error_message TEXT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO email_logs__rebuild (
                    id,
                    user_id,
                    email_type,
                    recipient_email,
                    sent_at,
                    status,
                    provider_message_id,
                    error_message
                )
                SELECT
                    CAST(id AS INTEGER),
                    user_id,
                    email_type,
                    recipient_email,
                    sent_at,
                    status,
                    provider_message_id,
                    error_message
                FROM email_logs
                """
            )
        )
        connection.execute(text("DROP TABLE email_logs"))
        connection.execute(text("ALTER TABLE email_logs__rebuild RENAME TO email_logs"))
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_email_logs_user_type "
                "ON email_logs (user_id, email_type)"
            )
        )
    return True


def _repair_llm_call_logs_columns() -> bool:
    inspector = inspect(engine)
    if "llm_call_logs" not in inspector.get_table_names():
        return False

    columns = _table_columns("llm_call_logs")
    required_columns = {
        "provider": "ALTER TABLE llm_call_logs ADD COLUMN provider VARCHAR(32) DEFAULT 'openai'",
        "pipeline_kind": "ALTER TABLE llm_call_logs ADD COLUMN pipeline_kind VARCHAR(32)",
        "execution_path_kind": (
            "ALTER TABLE llm_call_logs ADD COLUMN execution_path_kind VARCHAR(40)"
        ),
        "fallback_kind": "ALTER TABLE llm_call_logs ADD COLUMN fallback_kind VARCHAR(40)",
        "requested_provider": "ALTER TABLE llm_call_logs ADD COLUMN requested_provider VARCHAR(32)",
        "resolved_provider": "ALTER TABLE llm_call_logs ADD COLUMN resolved_provider VARCHAR(32)",
        "executed_provider": "ALTER TABLE llm_call_logs ADD COLUMN executed_provider VARCHAR(32)",
        "context_quality": "ALTER TABLE llm_call_logs ADD COLUMN context_quality VARCHAR(32)",
        "context_compensation_status": (
            "ALTER TABLE llm_call_logs ADD COLUMN context_compensation_status VARCHAR(32)"
        ),
        "max_output_tokens_source": (
            "ALTER TABLE llm_call_logs ADD COLUMN max_output_tokens_source VARCHAR(32)"
        ),
        "max_output_tokens_final": (
            "ALTER TABLE llm_call_logs ADD COLUMN max_output_tokens_final INTEGER"
        ),
        "executed_provider_mode": (
            "ALTER TABLE llm_call_logs ADD COLUMN executed_provider_mode VARCHAR(32)"
        ),
        "attempt_count": "ALTER TABLE llm_call_logs ADD COLUMN attempt_count INTEGER",
        "provider_error_code": (
            "ALTER TABLE llm_call_logs ADD COLUMN provider_error_code VARCHAR(50)"
        ),
        "breaker_state": "ALTER TABLE llm_call_logs ADD COLUMN breaker_state VARCHAR(20)",
        "breaker_scope": "ALTER TABLE llm_call_logs ADD COLUMN breaker_scope VARCHAR(100)",
        "active_snapshot_id": "ALTER TABLE llm_call_logs ADD COLUMN active_snapshot_id NUMERIC",
        "active_snapshot_version": (
            "ALTER TABLE llm_call_logs ADD COLUMN active_snapshot_version VARCHAR(64)"
        ),
        "manifest_entry_id": (
            "ALTER TABLE llm_call_logs ADD COLUMN manifest_entry_id VARCHAR(100)"
        ),
    }

    missing_columns = [name for name in required_columns if name not in columns]
    if not missing_columns:
        return False

    logger.warning(
        "local_sqlite_schema_repair_llm_call_logs missing_columns=%s",
        sorted(missing_columns),
    )
    with engine.begin() as connection:
        for column_name in missing_columns:
            connection.execute(text(required_columns[column_name]))
    return True


def _repair_local_sqlite_known_drift() -> bool:
    repaired = False
    repaired = _repair_email_logs_primary_key() or repaired
    repaired = _repair_llm_call_logs_columns() or repaired
    return repaired


def ensure_local_sqlite_schema_ready() -> None:
    if not _should_auto_upgrade_local_sqlite():
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_tables = _missing_declared_tables()
    current_revision = _current_revision()
    head_revision = _head_revision()
    if not missing_tables and current_revision == head_revision:
        _repair_local_sqlite_known_drift()
        return

    logger.warning(
        (
            "local_sqlite_schema_auto_upgrade database_url=%s missing_tables=%s "
            "current_revision=%s head_revision=%s"
        ),
        settings.database_url,
        sorted(missing_tables),
        current_revision,
        head_revision,
    )

    if current_revision is None and existing_tables:
        logger.warning(
            "local_sqlite_schema_stamp_existing_metadata database_url=%s table_count=%s",
            settings.database_url,
            len(existing_tables),
        )
        _repair_missing_tables(missing_tables)
        command.stamp(_alembic_config(), "head")
        _repair_local_sqlite_known_drift()
        return

    if current_revision != head_revision:
        command.upgrade(_alembic_config(), "head")
        _repair_local_sqlite_known_drift()
        return

    if missing_tables:
        logger.warning(
            "local_sqlite_schema_repair_create_all database_url=%s missing_tables=%s",
            settings.database_url,
            sorted(missing_tables),
        )
        _repair_missing_tables(missing_tables)
        _repair_local_sqlite_known_drift()


def ensure_configured_sqlite_file_matches_alembic_head() -> None:
    """
    À appeler depuis les conftest lorsque les tests utilisent `SessionLocal` /
    le moteur SQLAlchemy applicatif (fichier SQLite).

    Migrer **chaque** fichier SQLite pertinent : le moteur courant (`session.engine`)
    et `settings.database_url` peuvent différer (`app/tests/conftest.py` remplace le
    moteur par une base temporaire après l’import initial). Certains modules de test
    conservent une référence à l’ancien `SessionLocal` (import à la collecte) pointant
    encore vers `DATABASE_URL`, tandis que d’autres chemins utilisent le moteur patché.

    Hors pytest, `ensure_local_sqlite_schema_ready()` aligne déjà le schéma ; pendant
    pytest cette voie est désactivée (`_should_auto_upgrade_local_sqlite`), ce qui
    provoque des « no such table » si une migration n'a pas été appliquée manuellement.
    """
    from app.infra.db import session as session_module

    candidate_urls = [str(session_module.engine.url), settings.database_url]
    seen: set[str] = set()
    for url in candidate_urls:
        if url in seen:
            continue
        seen.add(url)
        if not url.startswith("sqlite"):
            continue
        if ":memory:" in url:
            continue

        command.upgrade(_alembic_config(database_url=url), "head")

    # Sur la base SQLite « secondaire » (souvent le fichier temporaire injecté par
    # `app/tests/conftest.py`), un filet ORM évite des tables manquantes si Alembic
    # et le moteur patché divergent. On ne le fait pas sur `settings.database_url`
    # pour ne pas perturber les tests qui s’appuient sur un schéma uniquement Alembic.
    connect_args: dict[str, object] = {}
    if _is_pytest_runtime():
        connect_args = {"check_same_thread": False, "timeout": 30}

    settings_url = settings.database_url
    for url in seen:
        if url == settings_url:
            continue
        sync_engine = create_engine(
            url,
            connect_args=connect_args,
            future=True,
        )
        try:
            Base.metadata.create_all(bind=sync_engine, checkfirst=True)
        finally:
            sync_engine.dispose()
