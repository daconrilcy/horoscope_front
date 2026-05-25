# Commentaire global: ces tests prouvent la creation et lecture persistantes des audits narratifs.
"""Couvre le repository `narrative_answer_audit_v1` adosse aux interpretations."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.infra.db.repositories.llm.narrative_answer_audit_repository import (
    NarrativeAnswerAuditCreate,
    NarrativeAnswerAuditRepository,
)


def test_repository_creates_and_reads_narrative_answer_audit(db: Session) -> None:
    """Une ligne auditée est réellement flushée puis relue par answer_id."""
    repository = NarrativeAnswerAuditRepository(db)
    created = repository.create(_audit_payload())
    db.commit()

    loaded = repository.get_by_answer_id("answer-288")
    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.answer_type == "premium"
    assert loaded.projection_hash == "a" * 64
    assert loaded.llm_input_hash == "b" * 64
    assert loaded.prompt_ref == "llm_prompt_versions:prompt-v1"
    assert loaded.provider == "openai"
    assert loaded.model == "gpt-test"
    assert loaded.grounding_status == "grounded"
    assert loaded.evidence_refs == [{"kind": "projection", "ref": "structured_facts_v1:hash"}]


def test_repository_rejects_values_outside_closed_vocabularies(db: Session) -> None:
    """Le repository bloque les categories inconnues avant le flush SQL."""
    repository = NarrativeAnswerAuditRepository(db)
    payload = _audit_payload(answer_type="vip")

    with pytest.raises(ValueError, match="answer_type"):
        repository.create(payload)  # type: ignore[arg-type]


def _audit_payload(
    *,
    answer_type: str = "premium",
    grounding_status: str = "grounded",
) -> NarrativeAnswerAuditCreate:
    """Construit un payload minimal conforme a CS-259 pour les tests."""
    return NarrativeAnswerAuditCreate(
        answer_id="answer-288",
        answer_type=answer_type,  # type: ignore[arg-type]
        chart_id="chart-288",
        user_id=288,
        plan="premium",
        projection_version="client_interpretation_projection_v1",
        projection_hash="a" * 64,
        llm_input_version="ai_narrative_input.v1",
        llm_input_hash="b" * 64,
        prompt_version="prompt-v1",
        prompt_ref="llm_prompt_versions:prompt-v1",
        prompt_snapshot_ref="llm_release_snapshots:snapshot-v1",
        provider="openai",
        model="gpt-test",
        grounding_status=grounding_status,  # type: ignore[arg-type]
        evidence_refs=[{"kind": "projection", "ref": "structured_facts_v1:hash"}],
        interpretation_payload={"summary": "Audit persiste."},
    )
