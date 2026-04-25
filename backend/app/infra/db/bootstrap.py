"""Bootstrap SQLite local et rattrapages de drift connus du backend."""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class SqliteAlignmentStatus:
    database_url: str
    file_path: Path | None
    exists: bool
    existing_table_count: int
    current_revision: str | None
    head_revision: str
    missing_tables: tuple[str, ...]

    @property
    def is_aligned(self) -> bool:
        return (
            self.exists and self.current_revision == self.head_revision and not self.missing_tables
        )

    @property
    def is_orm_aligned(self) -> bool:
        return self.exists and not self.missing_tables

    def as_debug_string(self) -> str:
        file_label = str(self.file_path) if self.file_path is not None else "<memory-or-non-file>"
        return (
            f"url={self.database_url} file={file_label} exists={self.exists} "
            f"existing_table_count={self.existing_table_count} "
            f"current_revision={self.current_revision} head_revision={self.head_revision} "
            f"missing_tables={list(self.missing_tables)}"
        )


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
    resolved_database_url = database_url if database_url is not None else settings.database_url
    config.attributes["configured_sqlalchemy_url"] = resolved_database_url
    config.set_main_option("sqlalchemy.url", resolved_database_url)
    return config


def _head_revision() -> str:
    return ScriptDirectory.from_config(_alembic_config()).get_current_head()


def _sqlite_file_path_from_url(database_url: str) -> Path | None:
    if not database_url.startswith("sqlite:///"):
        return None
    raw_path = database_url.removeprefix("sqlite:///")
    if raw_path == ":memory:":
        return None
    return Path(raw_path)


def sqlite_alignment_status(database_url: str) -> SqliteAlignmentStatus:
    head_revision = _head_revision()
    file_path = _sqlite_file_path_from_url(database_url)
    if file_path is not None and not file_path.exists():
        return SqliteAlignmentStatus(
            database_url=database_url,
            file_path=file_path,
            exists=False,
            existing_table_count=0,
            current_revision=None,
            head_revision=head_revision,
            missing_tables=tuple(sorted(Base.metadata.tables)),
        )

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False, "timeout": 30}

    sync_engine = create_engine(
        database_url,
        connect_args=connect_args,
        future=True,
    )
    try:
        inspector = inspect(sync_engine)
        existing_tables = set(inspector.get_table_names())
        current_revision: str | None = None
        if "alembic_version" in existing_tables:
            with sync_engine.connect() as connection:
                current_revision = connection.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar_one_or_none()
        missing_tables = tuple(sorted(set(Base.metadata.tables) - existing_tables))
        return SqliteAlignmentStatus(
            database_url=database_url,
            file_path=file_path,
            exists=True,
            existing_table_count=len(existing_tables),
            current_revision=current_revision,
            head_revision=head_revision,
            missing_tables=missing_tables,
        )
    finally:
        sync_engine.dispose()


def configured_sqlite_alignment_statuses() -> tuple[SqliteAlignmentStatus, ...]:
    from app.infra.db import session as session_module

    candidate_urls = [str(session_module.engine.url), settings.database_url]
    seen: set[str] = set()
    statuses: list[SqliteAlignmentStatus] = []
    for url in candidate_urls:
        if url in seen:
            continue
        seen.add(url)
        if not url.startswith("sqlite"):
            continue
        if ":memory:" in url:
            continue
        statuses.append(sqlite_alignment_status(url))
    return tuple(statuses)


def _is_strictly_aligned_configured_sqlite(
    status: SqliteAlignmentStatus,
    *,
    primary_database_url: str,
    allowed_secondary_missing_tables_at_head: frozenset[str] = frozenset(),
) -> bool:
    if (
        allowed_secondary_missing_tables_at_head
        and status.database_url != primary_database_url
        and status.exists
        and status.current_revision == status.head_revision
        and set(status.missing_tables).issubset(allowed_secondary_missing_tables_at_head)
    ):
        return True
    return status.is_aligned


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


def _repair_missing_tables_for_database_url(
    database_url: str,
    *,
    missing_tables: set[str],
) -> None:
    """Crée les tables ORM manquantes uniquement sur une SQLite secondaire ciblée."""
    if not missing_tables:
        return

    tables_to_create = [
        table for table in Base.metadata.sorted_tables if table.name in missing_tables
    ]
    if not tables_to_create:
        return

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False, "timeout": 30}

    sync_engine = create_engine(
        database_url,
        connect_args=connect_args,
        future=True,
    )
    try:
        Base.metadata.create_all(bind=sync_engine, tables=tables_to_create, checkfirst=True)
    finally:
        sync_engine.dispose()


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
    """Nettoie les reliquats legacy connus sur `llm_call_logs` sans les recréer."""
    inspector = inspect(engine)
    if "llm_call_logs" not in inspector.get_table_names():
        return False

    columns = _table_columns("llm_call_logs")
    if "provider" not in columns and "provider_compat" not in columns:
        return False

    with engine.begin() as connection:
        logger.warning("local_sqlite_schema_repair_llm_call_logs legacy_provider_columns_detected")
        if "provider" in columns:
            connection.execute(text("ALTER TABLE llm_call_logs DROP COLUMN provider"))
        if "provider_compat" in columns:
            connection.execute(text("ALTER TABLE llm_call_logs DROP COLUMN provider_compat"))
    return True


def _repair_llm_call_logs_environment_constraint() -> bool:
    """Reconstruit `llm_call_logs` si une ancienne contrainte d'environnement subsiste."""
    inspector = inspect(engine)
    if "llm_call_logs" not in inspector.get_table_names():
        return False

    with engine.connect() as connection:
        create_sql = connection.execute(
            text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'llm_call_logs'")
        ).scalar_one_or_none()

    if not create_sql or "'development'" in create_sql:
        return False
    if "ck_llm_call_logs_environment" not in create_sql:
        return False

    logger.warning("local_sqlite_schema_repair_llm_call_logs_environment_constraint")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE llm_call_logs__rebuild (
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
                        environment IN (
                            'development', 'dev', 'staging', 'production',
                            'prod', 'test', 'testing', 'local'
                        )
                    )
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO llm_call_logs__rebuild (
                    id,
                    use_case,
                    assembly_id,
                    feature,
                    subfeature,
                    "plan",
                    template_source,
                    prompt_version_id,
                    persona_id,
                    model,
                    latency_ms,
                    tokens_in,
                    tokens_out,
                    cost_usd_estimated,
                    validation_status,
                    repair_attempted,
                    fallback_triggered,
                    request_id,
                    trace_id,
                    input_hash,
                    environment,
                    evidence_warnings_count,
                    timestamp,
                    expires_at
                )
                SELECT
                    id,
                    use_case,
                    assembly_id,
                    feature,
                    subfeature,
                    "plan",
                    template_source,
                    prompt_version_id,
                    persona_id,
                    model,
                    latency_ms,
                    tokens_in,
                    tokens_out,
                    cost_usd_estimated,
                    validation_status,
                    repair_attempted,
                    fallback_triggered,
                    request_id,
                    trace_id,
                    input_hash,
                    environment,
                    evidence_warnings_count,
                    timestamp,
                    expires_at
                FROM llm_call_logs
                """
            )
        )
        connection.execute(text("DROP TABLE llm_call_logs"))
        connection.execute(text("ALTER TABLE llm_call_logs__rebuild RENAME TO llm_call_logs"))
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_llm_call_logs_request_id "
                "ON llm_call_logs (request_id)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_llm_call_logs_timestamp ON llm_call_logs (timestamp)"
            )
        )
        connection.execute(
            text("CREATE INDEX IF NOT EXISTS ix_llm_call_logs_trace_id ON llm_call_logs (trace_id)")
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_llm_call_logs_scope_timestamp "
                'ON llm_call_logs (feature, subfeature, "plan", timestamp)'
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_llm_call_logs_prompt_v_timestamp "
                "ON llm_call_logs (prompt_version_id, timestamp)"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_llm_call_logs_status_timestamp "
                "ON llm_call_logs (validation_status, timestamp)"
            )
        )
    return True


def _repair_local_sqlite_known_drift() -> bool:
    repaired = False
    repaired = _repair_email_logs_primary_key() or repaired
    repaired = _repair_llm_call_logs_columns() or repaired
    repaired = _repair_llm_call_logs_environment_constraint() or repaired
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


def ensure_configured_sqlite_file_matches_alembic_head(
    *, allowed_secondary_missing_tables_at_head: frozenset[str] = frozenset()
) -> None:
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
    statuses = configured_sqlite_alignment_statuses()
    for status in statuses:
        url = status.database_url
        config = _alembic_config(database_url=url)
        if status.exists and status.current_revision is None and status.existing_table_count > 0:
            logger.warning(
                (
                    "configured_sqlite_schema_stamp_existing_metadata "
                    "database_url=%s existing_table_count=%s missing_tables=%s"
                ),
                url,
                status.existing_table_count,
                sorted(status.missing_tables),
            )
            _repair_missing_tables_for_database_url(
                url,
                missing_tables=set(status.missing_tables),
            )
            command.stamp(config, "head")
            continue

        command.upgrade(config, "head")

    settings_url = settings.database_url
    repaired_secondary_urls: set[str] = set()
    intermediate_statuses = configured_sqlite_alignment_statuses()
    for status in intermediate_statuses:
        if status.database_url == settings_url:
            continue
        if not status.exists:
            continue
        if status.current_revision != status.head_revision:
            continue
        if not status.missing_tables:
            continue
        if status.database_url in repaired_secondary_urls:
            continue
        _repair_missing_tables_for_database_url(
            status.database_url,
            missing_tables=set(status.missing_tables),
        )
        repaired_secondary_urls.add(status.database_url)

    post_statuses = configured_sqlite_alignment_statuses()
    misaligned = [
        status
        for status in post_statuses
        if not _is_strictly_aligned_configured_sqlite(
            status,
            primary_database_url=settings_url,
            allowed_secondary_missing_tables_at_head=allowed_secondary_missing_tables_at_head,
        )
    ]
    if misaligned:
        formatted = "; ".join(status.as_debug_string() for status in misaligned)
        raise RuntimeError(
            "Configured SQLite files are not aligned with Alembic head and ORM metadata: "
            f"{formatted}"
        )
