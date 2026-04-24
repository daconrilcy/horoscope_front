from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.core.config import settings
from app.infra.db import session as session_module
from app.infra.db.base import Base
from app.infra.db.bootstrap import (
    SqliteAlignmentStatus,
    _is_strictly_aligned_configured_sqlite,
    ensure_configured_sqlite_file_matches_alembic_head,
    sqlite_alignment_status,
)


def test_backend_horoscope_db_is_aligned_with_backend_application() -> None:
    backend_root = Path(__file__).resolve().parents[2]
    backend_db_path = backend_root / "horoscope.db"

    assert backend_db_path.exists(), f"backend SQLite database not found: {backend_db_path}"

    ensure_configured_sqlite_file_matches_alembic_head()

    status = sqlite_alignment_status(f"sqlite:///{backend_db_path.as_posix()}")

    assert status.exists, status.as_debug_string()
    assert status.current_revision == status.head_revision, status.as_debug_string()
    assert status.missing_tables == (), status.as_debug_string()
    assert status.is_aligned, status.as_debug_string()


def test_secondary_sqlite_file_must_also_match_alembic_head() -> None:
    secondary = SqliteAlignmentStatus(
        database_url="sqlite:///tmp-secondary.sqlite3",
        file_path=Path("tmp-secondary.sqlite3"),
        exists=True,
        current_revision=None,
        head_revision="head-123",
        missing_tables=(),
    )

    assert (
        _is_strictly_aligned_configured_sqlite(
            secondary,
            primary_database_url="sqlite:///primary.sqlite3",
        )
        is False
    )


def test_secondary_sqlite_file_at_head_can_be_bounded_for_app_test_harness() -> None:
    secondary = SqliteAlignmentStatus(
        database_url="sqlite:///tmp-secondary.sqlite3",
        file_path=Path("tmp-secondary.sqlite3"),
        exists=True,
        current_revision="head-123",
        head_revision="head-123",
        missing_tables=("chat_messages",),
    )

    assert (
        _is_strictly_aligned_configured_sqlite(
            secondary,
            primary_database_url="sqlite:///primary.sqlite3",
            allowed_secondary_missing_tables_at_head=frozenset({"chat_messages"}),
        )
        is True
    )


def test_secondary_sqlite_file_at_head_still_fails_for_unexpected_missing_tables() -> None:
    secondary = SqliteAlignmentStatus(
        database_url="sqlite:///tmp-secondary.sqlite3",
        file_path=Path("tmp-secondary.sqlite3"),
        exists=True,
        current_revision="head-123",
        head_revision="head-123",
        missing_tables=("rogue_runtime_table",),
    )

    assert (
        _is_strictly_aligned_configured_sqlite(
            secondary,
            primary_database_url="sqlite:///primary.sqlite3",
            allowed_secondary_missing_tables_at_head=frozenset({"chat_messages"}),
        )
        is False
    )


def test_secondary_sqlite_file_with_orm_tables_but_without_alembic_head_fails_guard(
    tmp_path: Path,
    monkeypatch,
) -> None:
    sqlite_path = tmp_path / "sqlite-alignment-secondary.sqlite3"
    database_url = f"sqlite:///{sqlite_path.as_posix()}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    finally:
        engine.dispose()

    before_status = sqlite_alignment_status(database_url)
    assert before_status.current_revision is None, before_status.as_debug_string()
    assert before_status.missing_tables == (), before_status.as_debug_string()

    patched_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )
    monkeypatch.setattr(session_module, "engine", patched_engine)
    monkeypatch.setattr(settings, "database_url", database_url)

    with pytest.raises(Exception):
        ensure_configured_sqlite_file_matches_alembic_head()

    status = sqlite_alignment_status(database_url)
    assert status.current_revision is None, status.as_debug_string()

    patched_engine.dispose()


def test_secondary_sqlite_file_at_head_is_repaired_with_missing_orm_tables(
    tmp_path: Path,
    monkeypatch,
) -> None:
    sqlite_path = tmp_path / "sqlite-alignment-secondary-repair.sqlite3"
    database_url = f"sqlite:///{sqlite_path.as_posix()}"
    patched_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
        future=True,
    )
    monkeypatch.setattr(session_module, "engine", patched_engine)

    try:
        ensure_configured_sqlite_file_matches_alembic_head()
        status = sqlite_alignment_status(database_url)
        assert status.current_revision == status.head_revision, status.as_debug_string()
        assert status.missing_tables == (), status.as_debug_string()
    finally:
        patched_engine.dispose()
