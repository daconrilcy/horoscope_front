# Commentaire global: ces tests relient les preuves hashées aux sources du contrat LLM.
"""Controle la coherence des `evidence_refs` de `llm_astrology_input_v1`."""

from __future__ import annotations

from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLMAstrologyInputV1Builder,
)
from tests.unit.domain.astrology.test_llm_astrology_input_v1 import _build_sources


def test_evidence_refs_match_authorized_projection_source() -> None:
    """Une preuve hashée autorisee garde le contrat LLM grounded."""
    structured_facts, ai_input, client_projection = _build_sources()
    payload = LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_input,
        client_interpretation_projection_v1=client_projection,
    )

    assert payload["evidence"]["grounding_status"] == "grounded"
    assert (
        payload["evidence"]["evidence_refs"][0]["source_hash"]
        == (payload["provenance"]["projection_hash"])
    )


def test_invalid_evidence_ref_hash_is_rejected() -> None:
    """Une preuve decorative ou mal hashee ne peut pas rester grounded."""
    structured_facts, ai_input, client_projection = _build_sources()

    payload = LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_input,
        client_interpretation_projection_v1=client_projection,
        evidence_refs=(
            {
                "section_id": "llm_astrology_input_v1",
                "evidence_ref_id": "llm_astrology_input_v1.invalid",
                "source_type": "projection_version",
                "source_id": "projection",
                "source_version": "structured_facts_v1.contract.v1",
                "source_hash": "f" * 64,
            },
        ),
    )

    assert payload["evidence"]["grounding_status"] == "ungrounded"
    assert payload["evidence"]["evidence_refs"][0]["source_hash"] == "f" * 64
