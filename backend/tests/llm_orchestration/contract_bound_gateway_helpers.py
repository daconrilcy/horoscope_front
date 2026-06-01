# Commentaire global: fixtures partagees pour les tests du gateway LLM contract-bound.
"""Construit des snapshots et providers factices pour les preuves CS-431."""

from __future__ import annotations

import json
from typing import Any

from app.domain.llm.runtime.contracts import (
    ContractOutputValidator,
    ContractRepairPolicy,
    GatewayMeta,
    GatewayResult,
    ResolvedGenerationContractSnapshot,
    UsageInfo,
)
from app.domain.theme_natal.generation_contracts import resolve_theme_natal_generation_contract
from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalOutputVariant,
)


class RecordingContractClient:
    """Client provider qui enregistre les appels sans sortir du processus de test."""

    def __init__(self, outputs: list[str]) -> None:
        self.outputs = list(outputs)
        self.calls: list[dict[str, Any]] = []

    async def execute(self, **kwargs: Any) -> GatewayResult:
        """Retourne la prochaine sortie brute et conserve les arguments provider."""
        self.calls.append(kwargs)
        raw_output = self.outputs.pop(0)
        return GatewayResult(
            use_case=str(kwargs["use_case"]),
            request_id=str(kwargs["request_id"]),
            trace_id=str(kwargs["trace_id"]),
            raw_output=raw_output,
            structured_output=None,
            usage=UsageInfo(input_tokens=12, output_tokens=34, total_tokens=46),
            meta=GatewayMeta(
                latency_ms=1,
                model=str(kwargs["model"]),
                provider="openai",
            ),
        )


def runtime_snapshot(
    variant: ThemeNatalOutputVariant,
    *,
    validators: tuple[ContractOutputValidator, ...] = (),
    form_repair_attempts: int = 1,
) -> ResolvedGenerationContractSnapshot:
    """Adapte un snapshot theme natal en snapshot runtime generique."""
    theme_snapshot = resolve_theme_natal_generation_contract(
        THEME_NATAL_READING_CONTRACT_KEYS[variant]
    )
    contract = theme_snapshot.contract
    return ResolvedGenerationContractSnapshot(
        generation_contract_key=theme_snapshot.generation_contract_key,
        generation_contract_version=theme_snapshot.generation_contract_version,
        generation_contract_snapshot_id=theme_snapshot.generation_contract_snapshot_id,
        generation_contract_hash=theme_snapshot.generation_contract_hash,
        prompt_contract_version=theme_snapshot.prompt_contract_version,
        output_schema_version=theme_snapshot.output_schema_version,
        data_contract_version=theme_snapshot.data_contract_version,
        engine_profile_version=theme_snapshot.engine_profile_version,
        engine_profile=contract.engine_profile.model_dump(mode="json"),
        prompt_contract=contract.prompt_contract.model_dump(mode="json"),
        output_schema=contract.output_contract.raw_provider_schema,
        data_contract=contract.data_contract.model_dump(mode="json"),
        validators=validators,
        repair_policy=ContractRepairPolicy(
            form_repair_attempts=form_repair_attempts,
            content_repair_allowed=False,
        ),
    )


def basic_prompt_data() -> dict[str, object]:
    """Retourne les donnees Basic visibles attendues par le contrat data."""
    return {
        "locale": "fr-FR",
        "basic_natal_reading_plan": {
            "sections": [
                {"key": "identity", "source_ids": ["sun-identity"]},
                {"key": "resources", "source_ids": ["moon-resources"]},
            ]
        },
        "public_birth_context": {"month": "juin"},
        "source_annex_labels": ("Soleil", "Lune"),
    }


def premium_prompt_data_with_basic_payload() -> dict[str, object]:
    """Ajoute un payload Basic parasite pour prouver le filtrage Premium."""
    return {
        "locale": "fr-FR",
        "expanded_reading_plan": {"chapters": ["identity", "timing"]},
        "public_birth_context": {"month": "juin"},
        "timing_windows": ("trimestre",),
        "source_annex_labels": ("Soleil",),
        "basic_natal_prompt_payload": {"sections": ["forbidden"]},
    }


def raw_json(payload: dict[str, object]) -> str:
    """Serialise un payload provider de facon stable."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def valid_basic_raw_payload() -> dict[str, object]:
    """Construit une reponse Basic brute conforme au schema strict."""
    return {
        "schema_version": "theme_natal_basic_full_raw_v1",
        "title": "Lecture Basic complete",
        "introduction": _long_text("Introduction claire et prudente pour la lecture Basic."),
        "sections": [
            _basic_section("identity"),
            _basic_section("resources"),
            _basic_section("relationships"),
            _basic_section("growth"),
        ],
        "conclusion": _long_text("Conclusion nuancee et exploitable pour la lecture Basic."),
        "safety_notes": ("Lecture symbolique sans conseil medical ou financier.",),
    }


def _basic_section(key: str) -> dict[str, object]:
    return {
        "key": key,
        "heading": f"Chapitre {key}",
        "narrative": _long_text(f"Narration publique du chapitre {key}."),
        "source_refs": (
            {
                "source_id": f"{key}-source",
                "source_kind": "reading_plan",
                "relevance": "Repere public du plan de lecture.",
            },
        ),
        "limitations": (),
    }


def _long_text(seed: str) -> str:
    repeated = " ".join([seed] * 18)
    return repeated[:900]
