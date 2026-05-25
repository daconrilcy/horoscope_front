# Commentaire global: ces tests verifient la politique de donnees sensibles de l'audit narratif.
"""Valide le traitement des champs sensibles de `narrative_answer_audit_v1`."""

from __future__ import annotations

from app.core.sensitive_data import DataCategory, Sink, classify_field, get_policy_action


def test_prompt_payload_fields_remain_forbidden_in_audit_trail() -> None:
    """Un prompt complet reste interdit dans les traces d'audit."""
    category = classify_field("prompt")

    assert category == DataCategory.USER_AUTHORED_CONTENT
    assert get_policy_action(Sink.AUDIT_TRAIL, category).value == "forbidden"


def test_audit_prompt_and_model_refs_are_operational_metadata() -> None:
    """Les references techniques stockees ne contiennent pas le prompt brut."""
    for field_name in {
        "prompt_version",
        "prompt_ref",
        "prompt_snapshot_ref",
        "provider",
        "model",
        "llm_input_hash",
        "projection_hash",
        "evidence_refs",
    }:
        assert classify_field(field_name) == DataCategory.OPERATIONAL_METADATA
