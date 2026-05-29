# Commentaire global: ces tests prouvent l'alignement audit du runtime natal avec le contrat LLM.
"""Verifie les hashes et preuves stockes dans `narrative_answer_audit_v1`."""

from __future__ import annotations

from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.infra.db.models.user_natal_interpretation import UserNatalInterpretationModel
from app.services.llm_generation.natal.interpretation_service import (
    _apply_narrative_answer_audit,
)
from tests.unit.domain.astrology.test_llm_astrology_input_v1 import _build_payload


def test_natal_audit_uses_llm_astrology_input_hashes_and_evidence_refs() -> None:
    """L'audit persistant reprend les hashes et preuves du contrat prompt-visible."""
    llm_input = _build_payload()
    model = UserNatalInterpretationModel()

    _apply_narrative_answer_audit(
        model,
        level="complete",
        variant_code=None,
        schema_version="v1",
        request_id="runtime-1",
        gateway_result=_gateway_result(),
        persist_payload={"summary": "texte"},
        llm_astrology_input_v1=llm_input,
    )

    assert model.projection_hash == llm_input["provenance"]["projection_hash"]
    assert model.projection_version == llm_input["evidence"]["evidence_refs"][0]["source_version"]
    assert model.llm_input_hash == llm_input["provenance"]["llm_input_hash"]
    assert model.llm_input_version == llm_input["contract_version"]
    assert model.grounding_status == "grounded"
    assert model.evidence_refs == llm_input["evidence"]["evidence_refs"]


def test_runtime_only_request_id_does_not_change_audit_llm_input_hash() -> None:
    """Un changement de request_id audit-only ne modifie pas `llm_input_hash`."""
    llm_input = _build_payload()
    first = UserNatalInterpretationModel()
    second = UserNatalInterpretationModel()

    _apply_narrative_answer_audit(
        first,
        level="complete",
        variant_code=None,
        schema_version="v1",
        request_id="runtime-1",
        gateway_result=_gateway_result(),
        persist_payload={"summary": "texte"},
        llm_astrology_input_v1=llm_input,
    )
    _apply_narrative_answer_audit(
        second,
        level="complete",
        variant_code=None,
        schema_version="v1",
        request_id="runtime-2",
        gateway_result=_gateway_result(),
        persist_payload={"summary": "texte"},
        llm_astrology_input_v1=llm_input,
    )

    assert first.answer_id != second.answer_id
    assert first.llm_input_hash == second.llm_input_hash


def _gateway_result() -> GatewayResult:
    """Construit un resultat gateway minimal sans appel provider."""
    return GatewayResult(
        use_case="natal_interpretation",
        request_id="gateway-request",
        trace_id="trace",
        raw_output="{}",
        structured_output={"summary": "texte"},
        usage=UsageInfo(input_tokens=1, output_tokens=1),
        meta=GatewayMeta(
            latency_ms=1,
            model="test-model",
            provider="test-provider",
            plan="premium",
            prompt_version_id="prompt-v1",
        ),
    )
