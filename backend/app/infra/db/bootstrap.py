from __future__ import annotations

import logging
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
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


def _alembic_config() -> Config:
    backend_root = _resolve_backend_root()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
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


def ensure_local_sqlite_schema_ready() -> None:
    if not _should_auto_upgrade_local_sqlite():
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_tables = _missing_declared_tables()
    current_revision = _current_revision()
    head_revision = _head_revision()
    if not missing_tables and current_revision == head_revision:
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
        return

    if current_revision != head_revision:
        command.upgrade(_alembic_config(), "head")
        return

    if missing_tables:
        logger.warning(
            "local_sqlite_schema_repair_create_all database_url=%s missing_tables=%s",
            settings.database_url,
            sorted(missing_tables),
        )
        _repair_missing_tables(missing_tables)
