# Commentaire global: ces tests verrouillent le contrat DB de l'audit narratif v1.
"""Controle les champs et vocabulaires persistants `narrative_answer_audit_v1`."""

from __future__ import annotations

from sqlalchemy import inspect

from app.infra.db.models.user_natal_interpretation import (
    ALLOWED_NARRATIVE_ANSWER_TYPES,
    ALLOWED_NARRATIVE_GROUNDING_STATUSES,
    UserNatalInterpretationModel,
)


def test_narrative_answer_audit_required_columns_are_on_existing_owner() -> None:
    """Le proprietaire existant porte toutes les ancres CS-259 requises."""
    columns = {column.key: column for column in inspect(UserNatalInterpretationModel).columns}

    for column_name in {
        "answer_id",
        "answer_type",
        "chart_id",
        "user_id",
        "plan",
        "projection_version",
        "projection_hash",
        "llm_input_version",
        "llm_input_hash",
        "prompt_version",
        "provider",
        "model",
        "grounding_status",
        "evidence_refs",
        "created_at",
    }:
        assert column_name in columns
        assert not columns[column_name].nullable

    assert columns["prompt_ref"].nullable
    assert columns["prompt_snapshot_ref"].nullable


def test_narrative_answer_audit_closed_vocabularies_are_declared() -> None:
    """Les categories de reponse et statuts de grounding restent fermes."""
    assert ALLOWED_NARRATIVE_ANSWER_TYPES == (
        "basic",
        "premium",
        "long",
        "sensitive",
        "free_short",
    )
    assert ALLOWED_NARRATIVE_GROUNDING_STATUSES == (
        "grounded",
        "partial",
        "ungrounded",
        "rejected",
        "not_checked",
    )

    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in UserNatalInterpretationModel.__table__.constraints
        if hasattr(constraint, "sqltext")
    }
    assert "ck_user_natal_interpretations_answer_type" in constraints
    assert "ck_user_natal_interpretations_grounding_status" in constraints
    assert "free_short" in constraints["ck_user_natal_interpretations_answer_type"]
    assert "not_checked" in constraints["ck_user_natal_interpretations_grounding_status"]
