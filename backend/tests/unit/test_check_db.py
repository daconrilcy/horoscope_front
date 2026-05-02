# Tests du script de diagnostic de la base SQLite locale du backend.

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import check_db


def test_table_exists_detects_existing_table() -> None:
    """Verifie que la detection de table lit le catalogue SQLite."""
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE llm_assembly_configs (id INTEGER PRIMARY KEY)")

        assert check_db.table_exists(connection, "llm_assembly_configs") is True
        assert check_db.table_exists(connection, "missing_table") is False
    finally:
        connection.close()


def test_print_table_columns_rejects_invalid_table_name() -> None:
    """Evite qu'un nom de table invalide soit injecte dans une instruction PRAGMA."""
    connection = sqlite3.connect(":memory:")
    try:
        with pytest.raises(ValueError):
            check_db.print_table_columns(connection, "llm_assembly_configs; DROP TABLE users")
    finally:
        connection.close()


def test_main_uses_backend_database_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Garantit que le diagnostic depend du chemin configure, pas du repertoire courant."""
    database_path = tmp_path / "horoscope.db"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("CREATE TABLE llm_assembly_configs (id INTEGER PRIMARY KEY)")
    finally:
        connection.close()

    monkeypatch.setattr(check_db, "BACKEND_DB_PATH", database_path)

    assert check_db.main() == 0
    assert "Table llm_assembly_configs exists: True" in capsys.readouterr().out
