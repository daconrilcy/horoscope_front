# Commentaire global: definit les contrats de generation immuables du theme natal.
"""Contrats de generation theme natal, resolution snapshot et hash deterministe."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field

from app.domain.theme_natal.generation_schemas import (
    PUBLIC_PROJECTED_SCHEMA_NAMES,
    RAW_PROVIDER_SCHEMA_NAMES,
    THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS,
    THEME_NATAL_RAW_PROVIDER_SCHEMAS,
)
from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_CONTRACT_KEYS,
    ThemeNatalOutputVariant,
)

THEME_NATAL_GENERATION_CONTRACT_VERSION = "1.0.0"
THEME_NATAL_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "generation_contract_key",
    "generation_contract_version",
    "generation_contract_snapshot_id",
    "generation_contract_hash",
    "prompt_contract_version",
    "output_schema_version",
    "data_contract_version",
    "engine_profile_version",
)


class _StrictContractModel(BaseModel):
    """Base stricte des sections contractuelles persistables."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ThemeNatalRuntimeParameters(_StrictContractModel):
    """Parametres runtime versionnes sans appel provider."""

    temperature: float = Field(ge=0, le=2)
    top_p: float = Field(gt=0, le=1)
    max_output_tokens: int = Field(gt=0)


class ThemeNatalEngineProfile(_StrictContractModel):
    """Profil moteur requis par un contrat de generation."""

    version: str
    provider: str
    model_family: str
    runtime_parameters: ThemeNatalRuntimeParameters
    safety_profile: str


class ThemeNatalDataContract(_StrictContractModel):
    """Classification des donnees visibles, validees ou auditees."""

    version: str
    prompt_visible: tuple[str, ...]
    validation_only: tuple[str, ...]
    audit_only: tuple[str, ...]


class ThemeNatalPromptContract(_StrictContractModel):
    """Contrat prompt epingle pour une variante de lecture."""

    version: str
    prompt_policy_id: str
    assembly_key: str
    style_profile: str
    safety_policy: str
    forbidden_content_profile: tuple[str, ...]


class ThemeNatalOutputContract(_StrictContractModel):
    """Contrat de sortie separant brut provider et projection publique."""

    version: str
    raw_schema_name: str
    raw_schema_version: str
    raw_provider_schema: dict[str, Any]
    public_schema_name: str
    public_schema_version: str
    public_projected_schema: dict[str, Any]
    projection_policy: str


class ThemeNatalPersistenceContract(_StrictContractModel):
    """Champs auditables requis pour stocker un snapshot de contrat."""

    version: str
    snapshot_fields: tuple[str, ...]
    audit_fields: tuple[str, ...]
    mutable_registry_reference_allowed: bool = False


class ThemeNatalGenerationContract(_StrictContractModel):
    """Contrat complet de generation pour une variante theme natal."""

    generation_contract_key: str
    generation_contract_version: str
    output_variant: ThemeNatalOutputVariant
    engine_profile: ThemeNatalEngineProfile
    data_contract: ThemeNatalDataContract
    prompt_contract: ThemeNatalPromptContract
    output_contract: ThemeNatalOutputContract
    persistence_contract: ThemeNatalPersistenceContract


class ThemeNatalResolvedGenerationContractSnapshot(_StrictContractModel):
    """Snapshot resolu et hashable a persister avec une generation."""

    generation_contract_key: str
    generation_contract_version: str
    generation_contract_snapshot_id: str
    generation_contract_hash: str
    prompt_contract_version: str
    output_schema_version: str
    data_contract_version: str
    engine_profile_version: str
    contract: ThemeNatalGenerationContract


def calculate_theme_natal_generation_contract_hash(
    contract: ThemeNatalGenerationContract,
) -> str:
    """Calcule le hash stable du contenu contractuel resolu."""

    serialized = json.dumps(
        contract.model_dump(mode="json"),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def resolve_theme_natal_generation_contract(
    generation_contract_key: str,
    *,
    registry: Mapping[str, ThemeNatalGenerationContract] | None = None,
) -> ThemeNatalResolvedGenerationContractSnapshot:
    """Retourne un snapshot independant du registre mutable fourni."""

    contracts = registry or THEME_NATAL_GENERATION_CONTRACTS_BY_KEY
    contract = contracts[generation_contract_key]
    contract_copy = ThemeNatalGenerationContract.model_validate(contract.model_dump(mode="python"))
    contract_hash = calculate_theme_natal_generation_contract_hash(contract_copy)
    return ThemeNatalResolvedGenerationContractSnapshot(
        generation_contract_key=contract_copy.generation_contract_key,
        generation_contract_version=contract_copy.generation_contract_version,
        generation_contract_snapshot_id=f"{contract_copy.generation_contract_key}@{contract_hash[:16]}",
        generation_contract_hash=contract_hash,
        prompt_contract_version=contract_copy.prompt_contract.version,
        output_schema_version=contract_copy.output_contract.version,
        data_contract_version=contract_copy.data_contract.version,
        engine_profile_version=contract_copy.engine_profile.version,
        contract=contract_copy,
    )


def _contract(
    *,
    variant: ThemeNatalOutputVariant,
    engine_profile: ThemeNatalEngineProfile,
    data_contract: ThemeNatalDataContract,
    prompt_contract: ThemeNatalPromptContract,
    projection_policy: str,
) -> ThemeNatalGenerationContract:
    """Assemble une variante contractuelle avec ses schemas stricts."""

    return ThemeNatalGenerationContract(
        generation_contract_key=THEME_NATAL_READING_CONTRACT_KEYS[variant],
        generation_contract_version=THEME_NATAL_GENERATION_CONTRACT_VERSION,
        output_variant=variant,
        engine_profile=engine_profile,
        data_contract=data_contract,
        prompt_contract=prompt_contract,
        output_contract=ThemeNatalOutputContract(
            version="theme_natal.output_contract.v1",
            raw_schema_name=RAW_PROVIDER_SCHEMA_NAMES[variant],
            raw_schema_version="1",
            raw_provider_schema=THEME_NATAL_RAW_PROVIDER_SCHEMAS[variant],
            public_schema_name=PUBLIC_PROJECTED_SCHEMA_NAMES[variant],
            public_schema_version="1",
            public_projected_schema=THEME_NATAL_PUBLIC_PROJECTED_SCHEMAS[variant],
            projection_policy=projection_policy,
        ),
        persistence_contract=ThemeNatalPersistenceContract(
            version="theme_natal.persistence_contract.v1",
            snapshot_fields=THEME_NATAL_SNAPSHOT_FIELDS,
            audit_fields=(
                "request_id",
                "run_id",
                "answer_id",
                "validation_status",
                "provider_response_ref",
            ),
            mutable_registry_reference_allowed=False,
        ),
    )


THEME_NATAL_GENERATION_CONTRACTS: tuple[ThemeNatalGenerationContract, ...] = (
    _contract(
        variant=ThemeNatalOutputVariant.FREE_PREVIEW,
        engine_profile=ThemeNatalEngineProfile(
            version="theme_natal.engine.free_preview.v1",
            provider="openai",
            model_family="gpt-5-mini",
            runtime_parameters=ThemeNatalRuntimeParameters(
                temperature=0.4,
                top_p=0.9,
                max_output_tokens=900,
            ),
            safety_profile="astrology_public_preview",
        ),
        data_contract=ThemeNatalDataContract(
            version="theme_natal.data.free_preview.v1",
            prompt_visible=(
                "locale",
                "birth_context_without_direct_identifiers",
                "selected_public_chart_factors",
            ),
            validation_only=("entitlement_tier", "output_variant", "schema_version"),
            audit_only=("user_id", "chart_id", "request_id", "generation_contract_snapshot_id"),
        ),
        prompt_contract=ThemeNatalPromptContract(
            version="theme_natal.prompt.free_preview.v1",
            prompt_policy_id="theme_natal_free_preview_prompt_policy_v1",
            assembly_key="theme_natal_free_preview_assembly_v1",
            style_profile="concise_preview",
            safety_policy="public_astrology_non_deterministic_advice",
            forbidden_content_profile=("diagnostic", "certainty_claim", "private_identifier"),
        ),
        projection_policy="project_free_preview_card_without_provider_trace",
    ),
    _contract(
        variant=ThemeNatalOutputVariant.BASIC_FULL_READING,
        engine_profile=ThemeNatalEngineProfile(
            version="theme_natal.engine.basic_full_reading.v1",
            provider="openai",
            model_family="gpt-5",
            runtime_parameters=ThemeNatalRuntimeParameters(
                temperature=0.35,
                top_p=0.9,
                max_output_tokens=2400,
            ),
            safety_profile="astrology_basic_report",
        ),
        data_contract=ThemeNatalDataContract(
            version="theme_natal.data.basic_full_reading.v1",
            prompt_visible=(
                "locale",
                "basic_natal_reading_plan",
                "public_birth_context",
                "source_annex_labels",
            ),
            validation_only=("entitlement_tier", "section_keys", "public_schema_version"),
            audit_only=(
                "user_id",
                "chart_id",
                "request_id",
                "answer_id",
                "generation_contract_snapshot_id",
            ),
        ),
        prompt_contract=ThemeNatalPromptContract(
            version="theme_natal.prompt.basic_full_reading.v1",
            prompt_policy_id="theme_natal_basic_full_prompt_policy_v1",
            assembly_key="theme_natal_basic_full_assembly_v1",
            style_profile="human_basic_report",
            safety_policy="public_astrology_with_source_annex",
            forbidden_content_profile=("premium_positioning", "raw_score", "private_identifier"),
        ),
        projection_policy="project_basic_public_chapters_without_provider_trace",
    ),
    _contract(
        variant=ThemeNatalOutputVariant.PREMIUM_FULL_READING,
        engine_profile=ThemeNatalEngineProfile(
            version="theme_natal.engine.premium_full_reading.v1",
            provider="openai",
            model_family="gpt-5",
            runtime_parameters=ThemeNatalRuntimeParameters(
                temperature=0.32,
                top_p=0.9,
                max_output_tokens=3800,
            ),
            safety_profile="astrology_premium_report",
        ),
        data_contract=ThemeNatalDataContract(
            version="theme_natal.data.premium_full_reading.v1",
            prompt_visible=(
                "locale",
                "expanded_reading_plan",
                "public_birth_context",
                "timing_windows",
                "source_annex_labels",
            ),
            validation_only=("entitlement_tier", "chapter_keys", "public_schema_version"),
            audit_only=(
                "user_id",
                "chart_id",
                "request_id",
                "answer_id",
                "generation_contract_snapshot_id",
            ),
        ),
        prompt_contract=ThemeNatalPromptContract(
            version="theme_natal.prompt.premium_full_reading.v1",
            prompt_policy_id="theme_natal_premium_full_prompt_policy_v1",
            assembly_key="theme_natal_premium_full_assembly_v1",
            style_profile="deep_premium_report",
            safety_policy="public_astrology_with_timing_context",
            forbidden_content_profile=("clinical_claim", "certainty_claim", "private_identifier"),
        ),
        projection_policy="project_premium_public_chapters_without_provider_trace",
    ),
)

THEME_NATAL_GENERATION_CONTRACTS_BY_KEY: dict[str, ThemeNatalGenerationContract] = {
    contract.generation_contract_key: contract for contract in THEME_NATAL_GENERATION_CONTRACTS
}

__all__ = [
    "THEME_NATAL_GENERATION_CONTRACTS",
    "THEME_NATAL_GENERATION_CONTRACTS_BY_KEY",
    "THEME_NATAL_GENERATION_CONTRACT_VERSION",
    "THEME_NATAL_SNAPSHOT_FIELDS",
    "ThemeNatalDataContract",
    "ThemeNatalEngineProfile",
    "ThemeNatalGenerationContract",
    "ThemeNatalOutputContract",
    "ThemeNatalPersistenceContract",
    "ThemeNatalPromptContract",
    "ThemeNatalResolvedGenerationContractSnapshot",
    "calculate_theme_natal_generation_contract_hash",
    "resolve_theme_natal_generation_contract",
]
