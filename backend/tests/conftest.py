"""Fixtures et hooks partagés pour tout `backend/tests/` (integration, evaluation, …)."""

from __future__ import annotations

import pytest

from app.infra.db.bootstrap import (
    APP_TEST_SQLITE_ALLOWED_ORM_ONLY_TABLES,
    ensure_configured_sqlite_file_matches_alembic_head,
)


@pytest.fixture(scope="session", autouse=True)
def _ensure_sqlite_files_at_alembic_head_after_collection() -> None:
    """Après collecte complète (contrairement à `pytest_sessionstart`, qui est avant)."""
    ensure_configured_sqlite_file_matches_alembic_head(
        allowed_secondary_missing_tables_at_head=APP_TEST_SQLITE_ALLOWED_ORM_ONLY_TABLES
    )
