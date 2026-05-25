# Commentaire global: ces tests comparent le schema runtime et la migration de l'audit narratif.
"""Controle les colonnes et contraintes DB de `narrative_answer_audit_v1`."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import CheckConstraint

from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel

MIGRATION_PATH = Path(
    "migrations/versions/20260525_0139_extend_user_natal_interpretations_audit_v1.py"
)


def test_user_natal_interpretation_schema_exposes_audit_columns() -> None:
    """Le schema SQLAlchemy charge les colonnes d'audit sur la table existante."""
    table = UserNatalInterpretationModel.__table__
    columns = set(table.columns.keys())
    checks = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert {
        "answer_id",
        "answer_type",
        "plan",
        "projection_version",
        "projection_hash",
        "llm_input_version",
        "llm_input_hash",
        "prompt_version",
        "prompt_ref",
        "prompt_snapshot_ref",
        "provider",
        "model",
        "grounding_status",
        "evidence_refs",
    } <= columns
    assert "ck_user_natal_interpretations_answer_type" in checks
    assert "ck_user_natal_interpretations_grounding_status" in checks


def test_migration_extends_existing_table_without_new_audit_table() -> None:
    """La migration cible la table existante et ne cree pas de table doublon."""
    content = MIGRATION_PATH.read_text(encoding="utf-8")

    assert 'down_revision: Union[str, Sequence[str], None] = "20260524_0138"' in content
    assert "op.create_table" not in content
    assert 'TABLE_NAME = "user_natal_interpretations"' in content
    assert "answer_type IN" in content
    assert "grounding_status IN" in content
