# Garde d'architecture verifiant l'alignement entre SQLite, les modeles et Base.metadata.
"""Verifie que le registre SQLAlchemy couvre les tables applicatives connues."""

from __future__ import annotations

import ast
import sqlite3
from pathlib import Path

from app.infra.db.base import Base

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
MODELS_ROOT = BACKEND_ROOT / "app" / "infra" / "db" / "models"
SQLITE_DB_PATH = BACKEND_ROOT / "horoscope.db"
EXCEPTION_REGISTER_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "CS-180-aligner-registre-modeles-db-infra"
    / "db-table-exception-register.md"
)

EXACT_TABLE_EXCEPTIONS = frozenset(
    {
        "_alembic_tmp_astrologer_profiles",
        "alembic_version",
        "apscheduler_jobs",
        "llm_prompt_version_fallback_archives",
    }
)
FORBIDDEN_EXCEPTION_PATTERNS = frozenset({"llm_*", "_alembic_*", "*_archives"})


def _sqlite_table_names() -> set[str]:
    """Retourne les tables DB auditees sans dependre d'un fichier local ignore."""

    if not SQLITE_DB_PATH.exists():
        return set(_declared_model_tables()) | _registered_exception_tables()

    with sqlite3.connect(SQLITE_DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()
    return {row[0] for row in rows}


def _declared_model_tables() -> dict[str, str]:
    """Parse les fichiers de modeles et retourne chaque table avec son proprietaire."""

    model_tables: dict[str, str] = {}
    for path in sorted(MODELS_ROOT.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for statement in node.body:
                if not isinstance(statement, ast.Assign):
                    continue
                if not any(
                    isinstance(target, ast.Name) and target.id == "__tablename__"
                    for target in statement.targets
                ):
                    continue
                if isinstance(statement.value, ast.Constant) and isinstance(
                    statement.value.value, str
                ):
                    table_name = statement.value.value
                    owner = f"{path.relative_to(BACKEND_ROOT).as_posix()}::{node.name}"
                    assert table_name not in model_tables, (
                        f"Duplicate SQLAlchemy table owner for {table_name}: "
                        f"{model_tables[table_name]} and {owner}"
                    )
                    model_tables[table_name] = owner
    return model_tables


def _registered_exception_tables() -> set[str]:
    """Lit le registre d'exceptions persistant et refuse les motifs generiques."""

    assert EXCEPTION_REGISTER_PATH.exists(), (
        f"DB table exception register not found: {EXCEPTION_REGISTER_PATH}"
    )
    content = EXCEPTION_REGISTER_PATH.read_text(encoding="utf-8")
    for forbidden_pattern in FORBIDDEN_EXCEPTION_PATTERNS:
        assert forbidden_pattern not in content

    registered_tables: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith("| `") or line.startswith("| `Table`"):
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        if not columns:
            continue
        table_cell = columns[0]
        if table_cell.startswith("`") and table_cell.endswith("`"):
            registered_tables.add(table_cell.strip("`"))
    return registered_tables


def test_flagged_content_model_is_loaded_by_base_metadata() -> None:
    """Verrouille le chargement metadata du modele `flagged_contents`."""

    assert "flagged_contents" in _declared_model_tables()
    assert "flagged_contents" in Base.metadata.tables


def test_sqlite_tables_without_model_are_exactly_classified() -> None:
    """Garantit que seules les exceptions documentees restent sans modele."""

    sqlite_tables = _sqlite_table_names()
    model_tables = set(_declared_model_tables())
    missing_model_tables = sqlite_tables - model_tables

    assert _registered_exception_tables() == EXACT_TABLE_EXCEPTIONS
    assert missing_model_tables == EXACT_TABLE_EXCEPTIONS


def test_declared_model_tables_are_loaded_in_base_metadata() -> None:
    """Echoue si un fichier de modele applicatif reste absent de `Base.metadata`."""

    model_tables = set(_declared_model_tables())
    metadata_tables = set(Base.metadata.tables)

    assert model_tables - metadata_tables == set()


def test_sqlite_model_tables_are_loaded_in_base_metadata() -> None:
    """Echoue si une table SQLite applicative modelee reste hors metadata."""

    sqlite_tables = _sqlite_table_names()
    model_tables = set(_declared_model_tables())
    metadata_tables = set(Base.metadata.tables)

    assert (sqlite_tables & model_tables) - metadata_tables == set()
