from __future__ import annotations

from pathlib import Path

from app.infra.db.bootstrap import (
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
