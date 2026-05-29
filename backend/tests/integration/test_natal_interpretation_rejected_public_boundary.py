# Commentaire global: tests d'integration sur la frontiere publique rejected/accepted.
"""Verifie que les rejets LLM n'apparaissent pas comme interpretations utilisateur."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    validate_evidence_refs_by_section,
)
from app.domain.llm.prompting.schemas import AstroResponseV1
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    build_rejected_narrative_answer_outcome,
)
from app.services.llm_generation.natal.stored_interpretation_payload import (
    NARRATIVE_ANSWER_AUDIT_USE_CASE,
)

_REJECTED_PAYLOAD = {
    "status": "rejected",
    "rejection_reason": {"code": "natal_output_policy_violation"},
    "validation_context": [],
    "raw_answer_storage": {"structured_output": {"summary": "interne"}},
    "client_message": "Message controle.",
    "retry_policy": "out_of_scope",
    "title": "",
    "summary": "Message controle.",
    "sections": [],
    "highlights": [],
    "advice": [],
    "evidence": [],
}


def _accepted_payload() -> dict[str, object]:
    return {
        "title": "Theme",
        "summary": "Resume valide avec contenu suffisant.",
        "sections": [
            {"key": "overall", "heading": "Vue", "content": "Contenu principal."},
            {"key": "career", "heading": "Carriere", "content": "Contenu complementaire."},
        ],
        "highlights": ["A", "B", "C"],
        "advice": ["A", "B", "C"],
        "evidence": [],
    }


def test_list_interpretations_excludes_rejected_and_audit_rows(db: Session) -> None:
    """La liste publique ignore les rejets legacy et les lignes audit-only."""
    accepted = UserNatalInterpretationModel(
        user_id=384,
        chart_id="chart-384",
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload=_accepted_payload(),
        grounding_status="grounded",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    rejected = UserNatalInterpretationModel(
        user_id=384,
        chart_id="chart-384",
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload=_REJECTED_PAYLOAD,
        grounding_status="rejected",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    audit_row = UserNatalInterpretationModel(
        user_id=384,
        chart_id="chart-384",
        level=InterpretationLevel.COMPLETE,
        use_case=NARRATIVE_ANSWER_AUDIT_USE_CASE,
        interpretation_payload={"status": "rejected", "client_message": "audit"},
        grounding_status="rejected",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    db.add_all([accepted, rejected, audit_row])
    db.commit()

    rows, total = NatalInterpretationService.list_interpretations(
        db,
        user_id=384,
        chart_id="chart-384",
    )

    assert total == 1
    assert len(rows) == 1
    assert rows[0].id == accepted.id
    assert db.get(UserNatalInterpretationModel, rejected.id) is None


def test_get_interpretation_by_id_returns_none_for_rejected_legacy_row(db: Session) -> None:
    """Le detail public retourne None sur un rejet legacy (purge + 404 API)."""
    rejected = UserNatalInterpretationModel(
        user_id=385,
        chart_id="chart-385",
        level=InterpretationLevel.COMPLETE,
        use_case="natal_interpretation",
        interpretation_payload=_REJECTED_PAYLOAD,
        grounding_status="rejected",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    db.add(rejected)
    db.commit()
    rejected_id = rejected.id

    item = NatalInterpretationService.get_interpretation_by_id(
        db,
        user_id=385,
        interpretation_id=rejected_id,
    )

    assert item is None
    assert db.get(UserNatalInterpretationModel, rejected_id) is None


def test_get_interpretation_by_id_hides_audit_only_row_without_delete(db: Session) -> None:
    """Une ligne audit-only reste en base mais n'est pas exposee publiquement."""
    audit_row = UserNatalInterpretationModel(
        user_id=386,
        chart_id="chart-386",
        level=InterpretationLevel.COMPLETE,
        use_case=NARRATIVE_ANSWER_AUDIT_USE_CASE,
        interpretation_payload={"status": "rejected", "client_message": "audit"},
        grounding_status="rejected",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    db.add(audit_row)
    db.commit()
    audit_id = audit_row.id

    item = NatalInterpretationService.get_interpretation_by_id(
        db,
        user_id=386,
        interpretation_id=audit_id,
    )

    assert item is None
    assert db.get(UserNatalInterpretationModel, audit_id) is not None


def test_rejected_payload_cannot_be_validated_as_astro_response_v1() -> None:
    """Preuve RG-150: le contrat Astro strict refuse un payload rejected."""
    with pytest.raises(ValidationError):
        AstroResponseV1(**_REJECTED_PAYLOAD, disclaimers=[])


def test_deserialize_rejected_raises_service_error_not_pydantic() -> None:
    """La deserialization service remonte une erreur metier explicite."""
    model = UserNatalInterpretationModel(
        user_id=387,
        chart_id="chart-387",
        level=InterpretationLevel.SHORT,
        use_case="natal_interpretation_short",
        interpretation_payload=_REJECTED_PAYLOAD,
        grounding_status="rejected",
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    with pytest.raises(NatalInterpretationServiceError, match="rejected"):
        NatalInterpretationService._deserialize_persisted_interpretation(
            model,
            level="short",
            locale="fr-FR",
        )


def test_persist_rejected_audit_uses_audit_use_case(db: Session) -> None:
    """Un rejet persiste avec use_case audit, pas comme interpretation utilisateur."""
    from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
    from app.infra.db.repositories.llm.narrative_answer_audit_repository import (
        NarrativeAnswerAuditRepository,
    )
    from app.services.llm_generation.natal.interpretation_service import (
        _persist_rejected_narrative_answer_audit,
    )

    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=(),
        authorized_sources=(),
    )
    outcome = build_rejected_narrative_answer_outcome(
        answer_id="natal_interpretation:req-384",
        answer_type="premium",
        validation_result=validation_result,
        raw_answer={"summary": "RAW_INTERNAL"},
    )
    assert outcome is not None

    gateway_result = GatewayResult(
        use_case="natal_interpretation",
        request_id="req-384",
        trace_id="trace-384",
        raw_output="{}",
        structured_output={"summary": "RAW_INTERNAL"},
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=10,
            model="gpt-test",
            prompt_version_id="11111111-1111-1111-1111-111111111111",
            plan="premium",
            provider="openai",
        ),
    )
    llm_input = {
        "contract_version": "llm_astrology_input.v1",
        "provenance": {
            "llm_input_hash": "a" * 64,
            "projection_hash": "b" * 64,
        },
        "evidence": {
            "grounding_status": "grounded",
            "evidence_refs": [],
        },
    }

    _persist_rejected_narrative_answer_audit(
        db,
        user_id=388,
        chart_id="chart-388",
        level="complete",
        variant_code=None,
        gateway_result=gateway_result,
        llm_astrology_input_v1=llm_input,
        rejected_outcome=outcome,
    )

    rows, total = NatalInterpretationService.list_interpretations(
        db,
        user_id=388,
        chart_id="chart-388",
    )
    assert total == 0
    assert rows == []

    repository = NarrativeAnswerAuditRepository(db)
    persisted = repository.get_by_answer_id(outcome.answer_id)
    assert persisted is not None
    assert persisted.use_case == NARRATIVE_ANSWER_AUDIT_USE_CASE
