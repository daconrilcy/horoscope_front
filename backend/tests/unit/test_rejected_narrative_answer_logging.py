# Commentaire global: ces tests garantissent le log interne du rejet narratif.
"""Controle les champs de log emis par le workflow CS-290."""

from __future__ import annotations

import logging

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    validate_evidence_refs_by_section,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    REJECTED_NARRATIVE_LOG_EVENT,
    build_rejected_narrative_answer_outcome,
    emit_rejected_narrative_answer_log,
)


def test_rejected_answer_log_has_operational_fields_without_raw_payload(caplog) -> None:
    """Le log expose les diagnostics utiles sans le texte narratif brut."""
    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=(),
        authorized_sources=(),
    )
    outcome = build_rejected_narrative_answer_outcome(
        answer_id="answer-log",
        answer_type="premium",
        validation_result=validation_result,
        raw_answer={"summary": "RAW_SECRET_ANSWER"},
    )
    assert outcome is not None

    logger = logging.getLogger("tests.rejected_narrative_answer")
    with caplog.at_level(logging.INFO, logger=logger.name):
        emit_rejected_narrative_answer_log(
            logger,
            outcome=outcome,
            request_id="request-290",
            trace_id="trace-290",
            use_case="natal_interpretation",
        )

    record = caplog.records[0]
    assert record.event == REJECTED_NARRATIVE_LOG_EVENT
    assert record.request_id == "request-290"
    assert record.answer_id == "answer-log"
    assert record.use_case == "natal_interpretation"
    assert record.rejection_reason["code"] == "ungrounded_evidence_refs"
    assert "RAW_SECRET_ANSWER" not in record.getMessage()
