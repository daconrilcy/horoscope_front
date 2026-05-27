# Commentaire global: ces tests verrouillent l'identite hashable du contrat LLM astrologique.
"""Prouve la stabilite et les invalidations de `llm_input_hash`."""

from __future__ import annotations

from dataclasses import replace

from app.domain.astrology.interpretation.ai_narrative_input_contracts import (
    AINarrativeInterpretiveSignals,
)
from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLMAstrologyInputV1Builder,
)
from tests.unit.domain.astrology.test_llm_astrology_input_v1 import (
    _build_payload,
    _build_sources,
)


def test_llm_input_hash_is_stable_for_same_prompt_visible_material() -> None:
    """Deux constructions equivalentes produisent le meme hash canonique."""
    first = _build_payload()
    second = _build_payload()

    assert first["provenance"]["llm_input_hash"] == second["provenance"]["llm_input_hash"]
    assert len(first["provenance"]["llm_input_hash"]) == 64


def test_prompt_visible_signal_change_alters_llm_input_hash() -> None:
    """Un signal visible par le prompt invalide l'identite LLM."""
    structured_facts, ai_input, client_projection = _build_sources()
    updated_signals = replace(
        ai_input.interpretive_signals,
        dignity_codes=ai_input.interpretive_signals.dignity_codes + ("venus",),
    )
    changed_ai_input = replace(ai_input, interpretive_signals=updated_signals)

    original = LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=ai_input,
        client_interpretation_projection_v1=client_projection,
    )
    changed = LLMAstrologyInputV1Builder().build(
        structured_facts_v1=structured_facts,
        ai_narrative_input=changed_ai_input,
        client_interpretation_projection_v1=client_projection,
    )

    assert isinstance(updated_signals, AINarrativeInterpretiveSignals)
    assert original["provenance"]["llm_input_hash"] != changed["provenance"]["llm_input_hash"]


def test_runtime_only_request_identity_preserves_llm_input_hash() -> None:
    """Les identifiants runtime restent hors materiau prompt-visible."""
    first = _build_payload()
    second = _build_payload()

    assert first["provenance"]["prompt_ref"] == "natal.astrology.compact.v1"
    assert first["data_roles"]["runtime_only"] == [
        "request_id",
        "trace_id",
        "chart_json",
        "natal_data",
    ]
    assert first["provenance"]["llm_input_hash"] == second["provenance"]["llm_input_hash"]
