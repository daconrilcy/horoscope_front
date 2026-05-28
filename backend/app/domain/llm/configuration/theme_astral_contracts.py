# Contrats versionnes et profils provider du theme astral.
"""Contrats versionnes du prompt theme astral persistes via la registry LLM."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_prompt import PromptStatus

THEME_ASTRAL_USE_CASE_KEY = "theme_astral"
THEME_ASTRAL_FEATURE = "theme_astral"
THEME_ASTRAL_SUBFEATURE = "prompt_contract"
THEME_ASTRAL_PROMPT_CONTRACT_ID = "theme_astral_prompt_v1"
THEME_ASTRAL_INPUT_CONTRACT_ID = "theme_astral_llm_input_v1"
THEME_ASTRAL_RESPONSE_CONTRACT_ID = "theme_astral_response_contract_v1"
THEME_ASTRAL_OUTPUT_SCHEMA_NAME = THEME_ASTRAL_RESPONSE_CONTRACT_ID
THEME_ASTRAL_PERSONA_CODE = "theme_astral_astrologer_voice_v1"
THEME_ASTRAL_EXECUTION_PROFILE_NAME = "Theme Astral Contract GPT-5"

ThemeAstralCommercialPlan = Literal["free", "basic", "premium"]

THEME_ASTRAL_DELIVERY_PROFILES: dict[str, dict[str, Any]] = {
    "essential": {
        "delivery_profile_id": "theme_astral_delivery_profile_v1",
        "delivery_profile_version": "v1",
        "depth": "essential",
        "selection_policy": "core_chart_factors",
        "material_budget": {"max_source_items": 16, "max_sections": 4},
        "output_length_policy": {"target": "concise", "max_output_tokens": 1400},
    },
    "deep": {
        "delivery_profile_id": "theme_astral_delivery_profile_v1",
        "delivery_profile_version": "v1",
        "depth": "deep",
        "selection_policy": "expanded_chart_factors",
        "material_budget": {"max_source_items": 40, "max_sections": 8},
        "output_length_policy": {"target": "detailed", "max_output_tokens": 3200},
    },
}

THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES: dict[ThemeAstralCommercialPlan, dict[str, Any]] = {
    "free": {
        "delivery_profile_id": "theme_astral_delivery_profile_v1",
        "delivery_profile_version": "v1",
        "depth": "essential",
        "material_budget": {"max_source_items": 8, "max_sections": 4},
        "astrological_facts_budget": {
            "max_objects": 3,
            "max_aspects": 1,
            "max_dominants": 1,
        },
        "section_budget": {"max_sections": 4},
        "output_length_policy": {"target": "concise", "max_output_tokens": 1400},
    },
    "basic": {
        "delivery_profile_id": "theme_astral_delivery_profile_v1",
        "delivery_profile_version": "v1",
        "depth": "expanded",
        "material_budget": {"max_source_items": 24, "max_sections": 6},
        "astrological_facts_budget": {
            "max_objects": 6,
            "max_aspects": 3,
            "max_dominants": 2,
        },
        "section_budget": {"max_sections": 6},
        "output_length_policy": {"target": "balanced", "max_output_tokens": 2400},
    },
    "premium": {
        "delivery_profile_id": "theme_astral_delivery_profile_v1",
        "delivery_profile_version": "v1",
        "depth": "complete",
        "material_budget": {"max_source_items": 48, "max_sections": 8},
        "astrological_facts_budget": {
            "max_objects": 12,
            "max_aspects": 6,
            "max_dominants": 3,
        },
        "section_budget": {"max_sections": 8},
        "output_length_policy": {"target": "detailed", "max_output_tokens": 3600},
    },
}

THEME_ASTRAL_INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [THEME_ASTRAL_INPUT_CONTRACT_ID, "locale"],
    "properties": {
        THEME_ASTRAL_INPUT_CONTRACT_ID: {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "runtime_contract",
                "safety_contract",
                "astrologer_voice",
                "feature_context",
                "delivery_profile",
                "input_data",
                "output_contract",
            ],
            "properties": {
                "runtime_contract": {"type": "object"},
                "safety_contract": {"type": "object"},
                "astrologer_voice": {"type": "object"},
                "feature_context": {"type": "object"},
                "delivery_profile": {"type": "object"},
                "input_data": {"type": "object"},
                "output_contract": {"type": "object"},
            },
        },
        "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
    },
}

THEME_ASTRAL_RESPONSE_SCHEMA: dict[str, Any] = {
    "$id": THEME_ASTRAL_RESPONSE_CONTRACT_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "evidence", "contract_trace"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 1, "maxLength": 1800},
        "sections": {
            "type": "array",
            "minItems": 1,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {"type": "string", "minLength": 1, "maxLength": 80},
                    "heading": {"type": "string", "minLength": 1, "maxLength": 120},
                    "content": {"type": "string", "minLength": 1, "maxLength": 5000},
                },
            },
        },
        "evidence": {
            "type": "array",
            "maxItems": 80,
            "items": {"type": "string", "minLength": 1, "maxLength": 120},
        },
        "contract_trace": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "prompt_contract_id",
                "input_contract_id",
                "response_contract_id",
                "delivery_profile_id",
            ],
            "properties": {
                "prompt_contract_id": {"const": THEME_ASTRAL_PROMPT_CONTRACT_ID},
                "input_contract_id": {"const": THEME_ASTRAL_INPUT_CONTRACT_ID},
                "response_contract_id": {"const": THEME_ASTRAL_RESPONSE_CONTRACT_ID},
                "delivery_profile_id": {"type": "string"},
            },
        },
    },
}


class ThemeAstralContractRef(BaseModel):
    """Reference une ligne publiee de registry LLM sans exposer de libelle commercial."""

    id: str
    version: str | int


class ThemeAstralActiveContractFamily(BaseModel):
    """Read model stable du contrat prompt theme astral actif."""

    prompt_contract_id: Literal["theme_astral_prompt_v1"]
    input_contract_id: Literal["theme_astral_llm_input_v1"]
    response_contract_id: Literal["theme_astral_response_contract_v1"]
    delivery_profile: dict[str, Any]
    astrologer_voice: dict[str, Any]
    prompt_template_ref: ThemeAstralContractRef
    assembly_ref: ThemeAstralContractRef
    output_schema_ref: ThemeAstralContractRef
    execution_profile_ref: ThemeAstralContractRef
    status: Literal["published"]

    @model_validator(mode="after")
    def validate_contract_family(self) -> "ThemeAstralActiveContractFamily":
        """Bloque les assemblages actifs qui mélangent des versions incompatibles."""
        if self.delivery_profile.get("depth") not in THEME_ASTRAL_DELIVERY_PROFILES:
            raise ValueError("delivery_profile depth is not supported for theme_astral.")
        if self.output_schema_ref.id != THEME_ASTRAL_RESPONSE_CONTRACT_ID:
            raise ValueError("output schema must reference theme_astral_response_contract_v1.")
        if not self.astrologer_voice:
            raise ValueError("astrologer_voice must be resolved from a persona.")
        return self


def resolve_active_theme_astral_prompt_contract(
    db: Session, *, depth: str
) -> ThemeAstralActiveContractFamily:
    """Lit l'assembly publie theme_astral et retourne la famille de contrats active."""

    if depth not in THEME_ASTRAL_DELIVERY_PROFILES:
        raise ValueError(f"Unknown theme_astral delivery depth: {depth}.")

    assembly = db.execute(
        select(PromptAssemblyConfigModel).where(
            PromptAssemblyConfigModel.feature == THEME_ASTRAL_FEATURE,
            PromptAssemblyConfigModel.subfeature == THEME_ASTRAL_SUBFEATURE,
            PromptAssemblyConfigModel.plan == depth,
            PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
        )
    ).scalar_one_or_none()
    if assembly is None:
        raise ValueError(f"No published theme_astral assembly for depth: {depth}.")
    if assembly.feature_template is None:
        raise ValueError("theme_astral assembly must reference a prompt version.")
    if assembly.output_schema is None:
        raise ValueError("theme_astral assembly must reference an output schema.")
    if assembly.output_schema.name != THEME_ASTRAL_RESPONSE_CONTRACT_ID:
        raise ValueError("theme_astral assembly references an incompatible output schema.")
    if assembly.persona is None:
        raise ValueError("theme_astral assembly must reference an astrologer persona.")
    if assembly.execution_profile is None:
        raise ValueError("theme_astral assembly must reference an execution profile.")

    persona = assembly.persona
    return ThemeAstralActiveContractFamily(
        prompt_contract_id=THEME_ASTRAL_PROMPT_CONTRACT_ID,
        input_contract_id=THEME_ASTRAL_INPUT_CONTRACT_ID,
        response_contract_id=THEME_ASTRAL_RESPONSE_CONTRACT_ID,
        delivery_profile=THEME_ASTRAL_DELIVERY_PROFILES[depth],
        astrologer_voice={
            "persona_ref": str(persona.id),
            "code": persona.code,
            "tone": str(persona.tone),
            "verbosity": str(persona.verbosity),
            "style_markers": list(persona.style_markers or []),
            "boundaries": list(persona.boundaries or []),
        },
        prompt_template_ref=ThemeAstralContractRef(
            id=str(assembly.feature_template_ref), version=THEME_ASTRAL_PROMPT_CONTRACT_ID
        ),
        assembly_ref=ThemeAstralContractRef(id=str(assembly.id), version="published"),
        output_schema_ref=ThemeAstralContractRef(
            id=assembly.output_schema.name, version=assembly.output_schema.version
        ),
        execution_profile_ref=ThemeAstralContractRef(
            id=str(assembly.execution_profile_ref), version=assembly.execution_profile.name
        ),
        status="published",
    )


def resolve_theme_astral_provider_delivery_profile(
    commercial_plan: ThemeAstralCommercialPlan,
) -> dict[str, Any]:
    """Convertit un plan commercial backend en profil provider non commercial."""
    try:
        return dict(THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES[commercial_plan])
    except KeyError as exc:
        raise ValueError("unsupported theme_astral commercial plan") from exc


__all__ = [
    "THEME_ASTRAL_DELIVERY_PROFILES",
    "THEME_ASTRAL_EXECUTION_PROFILE_NAME",
    "THEME_ASTRAL_FEATURE",
    "THEME_ASTRAL_INPUT_CONTRACT_ID",
    "THEME_ASTRAL_INPUT_SCHEMA",
    "THEME_ASTRAL_OUTPUT_SCHEMA_NAME",
    "THEME_ASTRAL_PERSONA_CODE",
    "THEME_ASTRAL_PROMPT_CONTRACT_ID",
    "THEME_ASTRAL_RESPONSE_CONTRACT_ID",
    "THEME_ASTRAL_RESPONSE_SCHEMA",
    "THEME_ASTRAL_SUBFEATURE",
    "THEME_ASTRAL_USE_CASE_KEY",
    "ThemeAstralCommercialPlan",
    "ThemeAstralActiveContractFamily",
    "resolve_active_theme_astral_prompt_contract",
    "resolve_theme_astral_provider_delivery_profile",
]
