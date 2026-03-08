from __future__ import annotations

import logging
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.config import settings
from app.infra.db.session import engine

logger = logging.getLogger(__name__)

_REQUIRED_AUTH_TABLES = {"users", "user_refresh_tokens"}


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


def _missing_required_tables() -> set[str]:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    return _REQUIRED_AUTH_TABLES - existing_tables


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def ensure_local_sqlite_schema_ready() -> None:
    if not _should_auto_upgrade_local_sqlite():
        return

    missing_tables = _missing_required_tables()
    if not missing_tables:
        return

    logger.warning(
        "local_sqlite_schema_auto_upgrade database_url=%s missing_tables=%s",
        settings.database_url,
        sorted(missing_tables),
    )
    command.upgrade(_alembic_config(), "head")
