# Script de diagnostic ciblant toujours la base SQLite locale du backend.

import re
import sqlite3
from pathlib import Path

BACKEND_DB_PATH = Path(__file__).resolve().parent / "horoscope.db"
LLM_ASSEMBLY_CONFIGS_TABLE = "llm_assembly_configs"
SQLITE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    """Indique si une table existe dans la base SQLite inspectee."""
    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def print_table_columns(connection: sqlite3.Connection, table_name: str) -> None:
    """Affiche les colonnes de la table demandee pour un diagnostic manuel."""
    if SQLITE_IDENTIFIER_PATTERN.fullmatch(table_name) is None:
        raise ValueError(f"Invalid SQLite table name: {table_name}")

    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    for column in cursor.fetchall():
        print(column)


def main() -> int:
    """Execute le diagnostic sur la base SQLite locale du backend."""
    if not BACKEND_DB_PATH.exists():
        print(f"File {BACKEND_DB_PATH} not found.")
        return 1

    with sqlite3.connect(BACKEND_DB_PATH) as connection:
        exists = table_exists(connection, LLM_ASSEMBLY_CONFIGS_TABLE)
        print(f"Table {LLM_ASSEMBLY_CONFIGS_TABLE} exists: {exists}")
        if exists:
            print_table_columns(connection, LLM_ASSEMBLY_CONFIGS_TABLE)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
