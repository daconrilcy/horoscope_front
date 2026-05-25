# Test d'integration du schema de persistence des projections.
"""Controle les colonnes exposees par le modele et la migration Alembic."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, inspect

from app.infra.db.base import Base

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def test_persisted_projection_schema_exposes_required_columns() -> None:
    """Le schema runtime contient toutes les colonnes requises par CS-264."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    columns = {column["name"] for column in inspect(engine).get_columns("persisted_projections")}

    assert {
        "chart_id",
        "user_id",
        "projection_type",
        "projection_version",
        "projection_hash",
        "payload",
        "source_versions",
        "source",
        "generated_at",
    } <= columns


def test_migration_declares_persisted_projection_table_and_hash() -> None:
    """La migration Alembic porte la table canonique et projection_hash."""
    migration = (
        BACKEND_ROOT / "migrations" / "versions" / ("20260524_0138_create_persisted_projections.py")
    )
    content = migration.read_text(encoding="utf-8")

    assert "persisted_projections" in content
    assert "projection_hash" in content
    assert 'down_revision: Union[str, Sequence[str], None] = "20260523_0137"' in content
