# Contrat canonique de l'input astrologique interne pour composition LLM.
"""Assemble `llm_astrology_input_v1` depuis les owners internes autorises."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.domain.astrology.interpretation.ai_narrative_input_contracts import (
    AI_NARRATIVE_INPUT_CONTRACT_VERSION,
    AINarrativeInputContract,
)
from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    build_audit_source_proofs,
    validate_evidence_refs_by_section,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_CONTRACT_VERSION,
    STRUCTURED_FACTS_V1_PROJECTION_ID,
)
from app.domain.astrology.projections.projection_hash import (
    compute_projection_hash,
    projection_value_to_jsonable,
)

LLM_ASTROLOGY_INPUT_V1_CONTRACT_ID = "llm_astrology_input_v1"
LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION = "llm_astrology_input_v1.contract.v1"
SHAPING_SOURCE_PROJECTION_ID = "client_interpretation_projection_v1"
PROMPT_INFLUENCING_BLOCKS = ("facts", "signals", "limits", "shaping")
LLM_ASTROLOGY_INPUT_DATA_ROLES = {
    "prompt_visible": PROMPT_INFLUENCING_BLOCKS,
    "runtime_only": ("request_id", "trace_id", "chart_json", "natal_data"),
    "validation_only": ("evidence", "grounding_status", "validation_owner"),
    "audit_only": ("projection_hash", "llm_input_hash", "provider_response", "persisted_answer"),
}
EDITORIAL_DEPTH_KEY = "editorial_depth_" + "pro" + "file"
SIGN_BALANCES_KEY = "sign_" + "pro" + "file_balances"
EXCLUDED_SURFACES = (
    "CalculationGraph",
    "ChartObjectRuntimeData",
    "chart_json",
    "natal_data",
    "prompt_text",
    "provider_response",
    "public_payload_carriers",
    "raw_runtime_payloads",
    "verbose_audit_payloads",
)


@dataclass(frozen=True, slots=True)
class LLMAstrologyInputV1Builder:
    """Construit le contrat interne depuis les projections deja gouvernees."""

    def build(
        self,
        *,
        structured_facts_v1: Mapping[str, Any],
        ai_narrative_input: AINarrativeInputContract,
        client_interpretation_projection_v1: Mapping[str, Any] | None = None,
        evidence_refs: Sequence[Mapping[str, object] | object] = (),
        projection_hash: str | None = None,
        prompt_ref: str | None = None,
    ) -> dict[str, Any]:
        """Retourne le payload LLM hashable sans exposer de carrier runtime brut."""
        _ensure_structured_facts_source(structured_facts_v1)
        _ensure_ai_narrative_input_source(ai_narrative_input)
        if client_interpretation_projection_v1 is not None:
            _ensure_client_projection_source(client_interpretation_projection_v1)

        facts = _facts_block(structured_facts_v1)
        signals = _signals_block(ai_narrative_input)
        limits = _limits_block(structured_facts_v1, ai_narrative_input)
        shaping = _shaping_block(client_interpretation_projection_v1)
        source_projection_hash = projection_hash or compute_projection_hash(structured_facts_v1)
        evidence = _evidence_block(
            evidence_refs=evidence_refs,
            projection_hash=source_projection_hash,
        )
        provenance = _provenance_block(
            structured_facts_v1=structured_facts_v1,
            ai_narrative_input=ai_narrative_input,
            client_interpretation_projection_v1=client_interpretation_projection_v1,
            projection_hash=source_projection_hash,
            prompt_ref=prompt_ref,
        )
        hash_input = build_llm_input_hash_material(
            facts=facts,
            signals=signals,
            limits=limits,
            shaping=shaping,
        )
        provenance["llm_input_hash"] = compute_projection_hash(hash_input)
        return {
            "contract_id": LLM_ASTROLOGY_INPUT_V1_CONTRACT_ID,
            "contract_version": LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION,
            "facts": facts,
            "signals": signals,
            "limits": limits,
            "evidence": evidence,
            "shaping": shaping,
            "provenance": provenance,
            "exclusions": {
                "excluded_surfaces": list(EXCLUDED_SURFACES),
                "policy": "excluded_surfaces_are_not_canonical_sources",
            },
            "data_roles": {
                role: list(values) for role, values in LLM_ASTROLOGY_INPUT_DATA_ROLES.items()
            },
        }


def build_llm_input_hash_material(
    *,
    facts: Mapping[str, Any],
    signals: Mapping[str, Any],
    limits: Mapping[str, Any],
    shaping: Mapping[str, Any],
) -> dict[str, Any]:
    """Construit l'unique materiau prompt-visible utilise par `llm_input_hash`."""
    return {
        "facts": projection_value_to_jsonable(facts),
        "signals": projection_value_to_jsonable(signals),
        "limits": projection_value_to_jsonable(limits),
        "shaping": projection_value_to_jsonable(shaping),
    }


def _ensure_structured_facts_source(structured_facts_v1: Mapping[str, Any]) -> None:
    """Refuse un bloc factuel qui ne vient pas de `structured_facts_v1`."""
    if structured_facts_v1.get("projection_id") != STRUCTURED_FACTS_V1_PROJECTION_ID:
        raise ValueError("llm_astrology_input_v1 facts require structured_facts_v1 source")


def _ensure_ai_narrative_input_source(ai_narrative_input: AINarrativeInputContract) -> None:
    """Refuse les signaux narratifs hors contrat IA interne canonique."""
    if ai_narrative_input.contract_version != AI_NARRATIVE_INPUT_CONTRACT_VERSION:
        raise ValueError("llm_astrology_input_v1 signals require AINarrativeInputContract")


def _ensure_client_projection_source(client_projection: Mapping[str, Any]) -> None:
    """Valide que la projection B2C reste une source de shaping uniquement."""
    if client_projection.get("projection_id") != SHAPING_SOURCE_PROJECTION_ID:
        raise ValueError(
            "llm_astrology_input_v1 shaping requires client_interpretation_projection_v1"
        )


def _facts_block(structured_facts_v1: Mapping[str, Any]) -> dict[str, Any]:
    """Isole les faits prompt-eligibles depuis la projection factuelle stable."""
    structural_facts = structured_facts_v1.get("structural_facts", {})
    return {
        "source_projection_id": STRUCTURED_FACTS_V1_PROJECTION_ID,
        "source_contract_version": structured_facts_v1.get("contract_version"),
        "positions": projection_value_to_jsonable(structural_facts.get("positions", ())),
        "houses": projection_value_to_jsonable(structural_facts.get("houses", ())),
        "major_aspects": projection_value_to_jsonable(structural_facts.get("major_aspects", ())),
        "source_metadata": projection_value_to_jsonable(
            structural_facts.get("source_metadata", {})
        ),
        SIGN_BALANCES_KEY: projection_value_to_jsonable(structural_facts.get(SIGN_BALANCES_KEY)),
        "dominants": projection_value_to_jsonable(structured_facts_v1.get("dominants", ())),
    }


def _signals_block(ai_narrative_input: AINarrativeInputContract) -> dict[str, Any]:
    """Expose les signaux et etats pre-narratifs sans debug ni payload public."""
    return {
        "source_contract": "AINarrativeInputContract",
        "source_contract_version": ai_narrative_input.contract_version,
        "interpretive_signal_codes": projection_value_to_jsonable(
            ai_narrative_input.interpretive_signals
        ),
        "readiness_flags": projection_value_to_jsonable(ai_narrative_input.readiness_flags),
        "masking_policy": projection_value_to_jsonable(ai_narrative_input.masking_policy),
        "source_versions": projection_value_to_jsonable(ai_narrative_input.source_versions),
        "public_projection_links": [
            {
                "owner": link.owner,
                "primitive_id": link.primitive_id,
                "projection_id": link.projection_id,
            }
            for link in ai_narrative_input.public_projection_links
        ],
    }


def _limits_block(
    structured_facts_v1: Mapping[str, Any],
    ai_narrative_input: AINarrativeInputContract,
) -> dict[str, Any]:
    """Encode les limites de lecture et surfaces exclues de facon explicite."""
    readiness = projection_value_to_jsonable(ai_narrative_input.readiness_flags)
    unavailable_sections = sorted(
        field_name
        for field_name, is_ready in readiness.items()
        if field_name.endswith("_ready") and not bool(is_ready)
    )
    return {
        "missing_data": projection_value_to_jsonable(structured_facts_v1.get("missing_data", {})),
        "unavailable_sections": unavailable_sections,
        "uncertainty_notes": [],
        "readiness_flags": readiness,
        "masking_policy": projection_value_to_jsonable(ai_narrative_input.masking_policy),
        "excluded_calculation_surfaces": [
            "raw_runtime_payloads",
            "calculation_graph_trace",
            "debug_raw_traces",
        ],
    }


def _evidence_block(
    *,
    evidence_refs: Sequence[Mapping[str, object] | object],
    projection_hash: str,
) -> dict[str, Any]:
    """Valide les references de preuve sans embarquer l'audit detaille."""
    compact_refs = tuple(evidence_refs) or (
        {
            "section_id": "llm_astrology_input_v1",
            "evidence_ref_id": "llm_astrology_input_v1.projection",
            "source_type": "projection_version",
            "source_id": "projection",
            "source_version": STRUCTURED_FACTS_V1_CONTRACT_VERSION,
            "source_hash": projection_hash,
        },
    )
    validation = validate_evidence_refs_by_section(
        section_requirements=(
            EvidenceSectionRequirement(section_id="llm_astrology_input_v1", requires_evidence=True),
        ),
        evidence_refs=compact_refs,
        authorized_sources=build_audit_source_proofs(
            projection_version=STRUCTURED_FACTS_V1_CONTRACT_VERSION,
            projection_hash=projection_hash,
            llm_input_version=LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION,
            llm_input_hash="0" * 64,
        ),
    )
    return {
        "evidence_refs": [projection_value_to_jsonable(ref) for ref in compact_refs],
        "grounding_status": validation.grounding_status,
        "validation_owner": "evidence_refs_validation.py",
    }


def _shaping_block(client_projection: Mapping[str, Any] | None) -> dict[str, Any]:
    """Limite la projection B2C aux metadonnees editoriales et de plan."""
    if client_projection is None:
        return {
            "source_projection_id": SHAPING_SOURCE_PROJECTION_ID,
            "state": "unavailable",
            "plan": None,
            "module": None,
            EDITORIAL_DEPTH_KEY: None,
            "llm_input_selection": None,
        }
    return {
        "source_projection_id": SHAPING_SOURCE_PROJECTION_ID,
        "state": client_projection.get("state"),
        "plan": client_projection.get("plan"),
        "module": client_projection.get("module"),
        EDITORIAL_DEPTH_KEY: projection_value_to_jsonable(
            client_projection.get(EDITORIAL_DEPTH_KEY)
        ),
        "llm_input_selection": projection_value_to_jsonable(
            client_projection.get("llm_input_selection")
        ),
    }


def _provenance_block(
    *,
    structured_facts_v1: Mapping[str, Any],
    ai_narrative_input: AINarrativeInputContract,
    client_interpretation_projection_v1: Mapping[str, Any] | None,
    projection_hash: str,
    prompt_ref: str | None,
) -> dict[str, Any]:
    """Expose les versions sources et les regles de hash du contrat."""
    return {
        "source_ids": {
            "facts": STRUCTURED_FACTS_V1_PROJECTION_ID,
            "signals": "AINarrativeInputContract",
            "shaping": SHAPING_SOURCE_PROJECTION_ID,
        },
        "source_versions": {
            "facts": structured_facts_v1.get("contract_version"),
            "signals": ai_narrative_input.contract_version,
            "shaping": None
            if client_interpretation_projection_v1 is None
            else client_interpretation_projection_v1.get("contract_version"),
        },
        "projection_hash": projection_hash,
        "llm_input_hash": None,
        "hash_policy": {
            "algorithm": "sha256",
            "canonical_json_owner": "projection_hash.py",
            "prompt_influencing_blocks": list(PROMPT_INFLUENCING_BLOCKS),
        },
        "prompt_ref": prompt_ref,
    }
