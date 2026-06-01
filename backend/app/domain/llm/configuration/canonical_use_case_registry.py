# Registre interne des cas d'usage LLM canoniques.
"""Declare les contrats runtime internes consommes par le gateway LLM."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_INPUT_SCHEMA,
    THEME_ASTRAL_RESPONSE_CONTRACT_ID,
    THEME_ASTRAL_RESPONSE_SCHEMA,
    THEME_ASTRAL_USE_CASE_KEY,
)
from app.domain.llm.prompting.narrator_contract import NARRATOR_OUTPUT_SCHEMA
from app.domain.llm.prompting.schemas import _SECTION_KEY_VALUES
from app.domain.llm.runtime.contracts import EVIDENCE_ID_REGEX
from app.domain.theme_natal.generation_contracts import THEME_NATAL_GENERATION_CONTRACTS
from app.domain.theme_natal.generation_schemas import THEME_NATAL_PUBLIC_SCHEMA_REGISTRY


class CanonicalOutputSchemaDefinition(BaseModel):
    name: str
    version: int
    json_schema: dict[str, Any]


class CanonicalUseCaseContract(BaseModel):
    key: str
    display_name: str
    description: str
    output_schema_name: str | None = None
    persona_strategy: str = "optional"
    safety_profile: str = "astrology"
    fallback_target_key: str | None = None
    required_prompt_placeholders: list[str] = Field(default_factory=list)
    interaction_mode: str = "structured"
    user_question_policy: str = "none"
    input_schema: dict[str, Any] | None = None
    eval_fixtures_path: str | None = None
    eval_failure_threshold: float | None = None
    golden_set_path: str | None = None


CHAT_RESPONSE_V1 = {
    "type": "object",
    "required": ["message", "suggested_replies", "intent", "confidence", "safety_notes"],
    "additionalProperties": False,
    "properties": {
        "message": {"type": "string", "minLength": 1, "maxLength": 2500},
        "suggested_replies": {
            "type": "array",
            "maxItems": 5,
            "items": {"type": "string", "minLength": 1, "maxLength": 80},
        },
        "intent": {
            "type": ["string", "null"],
            "enum": [
                "clarify_question",
                "ask_birth_data",
                "explain_natal_basics",
                "offer_natal_interpretation",
                "offer_event_guidance",
                "handoff_to_support",
                "close_conversation",
                None,
            ],
        },
        "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "safety_notes": {
            "type": "array",
            "maxItems": 3,
            "items": {"type": "string", "maxLength": 200},
        },
    },
}

ASTRO_RESPONSE_V1_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence", "disclaimers"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 120},
        "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
        "sections": {
            "type": "array",
            "minItems": 2,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {"type": "string", "enum": list(_SECTION_KEY_VALUES)},
                    "heading": {"type": "string", "minLength": 1, "maxLength": 80},
                    "content": {"type": "string", "minLength": 1, "maxLength": 2500},
                },
            },
        },
        "highlights": {
            "type": "array",
            "minItems": 3,
            "maxItems": 10,
            "items": {"type": "string", "maxLength": 360},
        },
        "advice": {
            "type": "array",
            "minItems": 3,
            "maxItems": 10,
            "items": {"type": "string", "maxLength": 360},
        },
        "evidence": {
            "type": "array",
            "maxItems": 40,
            "items": {"type": "string", "pattern": EVIDENCE_ID_REGEX},
        },
        "disclaimers": {
            "type": "array",
            "maxItems": 3,
            "items": {"type": "string", "maxLength": 200},
        },
    },
}

ASTRO_RESPONSE_V3_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 900, "maxLength": 2800},
        "sections": {
            "type": "array",
            "minItems": 5,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {"type": "string", "enum": list(_SECTION_KEY_VALUES)},
                    "heading": {"type": "string", "minLength": 1, "maxLength": 100},
                    "content": {"type": "string", "minLength": 280, "maxLength": 6500},
                },
            },
        },
        "highlights": {
            "type": "array",
            "minItems": 5,
            "maxItems": 12,
            "items": {"type": "string", "maxLength": 360},
        },
        "advice": {
            "type": "array",
            "minItems": 5,
            "maxItems": 12,
            "items": {"type": "string", "maxLength": 360},
        },
        "evidence": {
            "type": "array",
            "maxItems": 80,
            "items": {"type": "string", "pattern": EVIDENCE_ID_REGEX},
        },
    },
}

CANONICAL_OUTPUT_SCHEMAS: tuple[CanonicalOutputSchemaDefinition, ...] = (
    CanonicalOutputSchemaDefinition(
        name="ChatResponse_v1",
        json_schema=CHAT_RESPONSE_V1,
        version=1,
    ),
    CanonicalOutputSchemaDefinition(
        name="AstroResponse_v1",
        json_schema=ASTRO_RESPONSE_V1_JSON_SCHEMA,
        version=1,
    ),
    CanonicalOutputSchemaDefinition(
        name="AstroResponse_v3",
        json_schema=ASTRO_RESPONSE_V3_JSON_SCHEMA,
        version=3,
    ),
    CanonicalOutputSchemaDefinition(
        name="NarratorResult_v1",
        json_schema=NARRATOR_OUTPUT_SCHEMA,
        version=1,
    ),
    CanonicalOutputSchemaDefinition(
        name=THEME_ASTRAL_RESPONSE_CONTRACT_ID,
        json_schema=THEME_ASTRAL_RESPONSE_SCHEMA,
        version=1,
    ),
    *(
        CanonicalOutputSchemaDefinition(name=name, version=version, json_schema=json_schema)
        for name, version, json_schema in THEME_NATAL_PUBLIC_SCHEMA_REGISTRY
    ),
)

NATAL_LLM_ASTROLOGY_INPUT_SCHEMA = {
    "type": "object",
    "required": ["llm_astrology_input_v1"],
    "properties": {
        "llm_astrology_input_v1": {"type": "object"},
        "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
    },
}

CANONICAL_USE_CASE_CONTRACTS: tuple[CanonicalUseCaseContract, ...] = (
    CanonicalUseCaseContract(
        key="natal_interpretation",
        display_name="Interprétation Natale",
        description="Analyse approfondie du thème de naissance.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="chat_astrologer",
        display_name="Chat Astrologue",
        description="Conversation interactive avec l'astrologue virtuel.",
        output_schema_name="ChatResponse_v1",
        persona_strategy="required",
        required_prompt_placeholders=["persona_name", "current_datetime"],
        interaction_mode="chat",
        user_question_policy="required",
        input_schema={
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string", "maxLength": 1000},
                "conversation_id": {"type": ["integer", "string", "null"]},
                "persona_id": {"type": ["string", "null"]},
            },
        },
    ),
    CanonicalUseCaseContract(
        key="astrologer_selection_help",
        display_name="Aide au Choix d'Astrologue",
        description="Assistant pour aider l'utilisateur à choisir un expert.",
        output_schema_name="ChatResponse_v1",
        persona_strategy="forbidden",
        safety_profile="support",
        interaction_mode="chat",
        user_question_policy="required",
    ),
    CanonicalUseCaseContract(
        key="account_support",
        display_name="Support Compte",
        description="Aide technique pour la gestion du compte utilisateur.",
        persona_strategy="forbidden",
        safety_profile="support",
        interaction_mode="chat",
        user_question_policy="required",
    ),
    CanonicalUseCaseContract(
        key="natal_psy_profile",
        display_name="Profil Psycho Natal",
        description="Portrait psychologique astrologique (dynamique, non clinique).",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_shadow_integration",
        display_name="Shadow Integration Natal",
        description="Schémas répétitifs, déclencheurs et leviers d'intégration.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_leadership_workstyle",
        display_name="Leadership et Workstyle Natal",
        description="Style de leadership, motivation et environnement idéal.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_creativity_joy",
        display_name="Créativité et Joie Natales",
        description="Inspiration, blocages créatifs et pratiques de ressourcement.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_relationship_style",
        display_name="Style Relationnel Natal",
        description="Besoins affectifs, gestion du conflit et style d'engagement.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_community_networks",
        display_name="Communauté et Réseaux Natals",
        description="Place dans le collectif, collaboration et énergie sociale.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_values_security",
        display_name="Valeurs et Sécurité Natales",
        description="Rapport aux valeurs, à la sécurité et aux limites personnelles.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="natal_evolution_path",
        display_name="Axe d'Évolution Natal",
        description="Zone de confort, croissance et étapes d'intégration.",
        output_schema_name="AstroResponse_v3",
        persona_strategy="required",
        required_prompt_placeholders=["llm_astrology_input_v1", "persona_name"],
        input_schema=NATAL_LLM_ASTROLOGY_INPUT_SCHEMA,
    ),
    CanonicalUseCaseContract(
        key="guidance_daily",
        display_name="Guidance Quotidienne",
        description="Conseils astrologiques pour la journée.",
        output_schema_name="AstroResponse_v1",
        required_prompt_placeholders=["natal_chart_summary"],
        interaction_mode="chat",
        user_question_policy="optional",
    ),
    CanonicalUseCaseContract(
        key="guidance_weekly",
        display_name="Guidance Hebdomadaire",
        description="Conseils astrologiques pour la semaine.",
        output_schema_name="AstroResponse_v1",
        required_prompt_placeholders=["natal_chart_summary"],
        interaction_mode="chat",
    ),
    CanonicalUseCaseContract(
        key="guidance_contextual",
        display_name="Guidance Contextuelle",
        description="Lecture astrologique prudente pour une situation ou consultation thématique.",
        output_schema_name="AstroResponse_v1",
        required_prompt_placeholders=["situation", "objective", "natal_chart_summary"],
        interaction_mode="chat",
        user_question_policy="required",
    ),
    CanonicalUseCaseContract(
        key="horoscope_daily",
        display_name="Horoscope Quotidien Canonique",
        description="Narration de l'horoscope quotidien (free/premium).",
        output_schema_name="NarratorResult_v1",
        persona_strategy="required",
        required_prompt_placeholders=["question"],
    ),
    CanonicalUseCaseContract(
        key=THEME_ASTRAL_USE_CASE_KEY,
        display_name="Contrat Prompt Theme Astral",
        description="Contrat versionne de construction du prompt theme astral.",
        output_schema_name=THEME_ASTRAL_RESPONSE_CONTRACT_ID,
        persona_strategy="required",
        required_prompt_placeholders=[THEME_ASTRAL_INPUT_CONTRACT_ID, "persona_name"],
        input_schema=THEME_ASTRAL_INPUT_SCHEMA,
    ),
    *(
        CanonicalUseCaseContract(
            key=contract.generation_contract_key,
            display_name=f"Theme Natal {contract.output_variant.value}",
            description="Contrat versionne de generation theme natal.",
            output_schema_name=contract.output_contract.public_schema_name,
            persona_strategy="required",
            required_prompt_placeholders=["theme_natal_generation_input_v1"],
            input_schema={
                "type": "object",
                "required": ["theme_natal_generation_input_v1", "locale"],
                "additionalProperties": False,
                "properties": {
                    "theme_natal_generation_input_v1": {"type": "object"},
                    "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
                },
            },
        )
        for contract in THEME_NATAL_GENERATION_CONTRACTS
    ),
)

_CONTRACTS_BY_KEY = {contract.key: contract for contract in CANONICAL_USE_CASE_CONTRACTS}
_SCHEMAS_BY_NAME = {schema.name: schema for schema in CANONICAL_OUTPUT_SCHEMAS}


def list_canonical_use_case_contracts() -> list[CanonicalUseCaseContract]:
    return list(CANONICAL_USE_CASE_CONTRACTS)


def list_modern_natal_use_case_contracts() -> list[CanonicalUseCaseContract]:
    """Retourne les cas natals modernes proprietaires de l'entree astrologique riche."""

    return [
        contract
        for contract in CANONICAL_USE_CASE_CONTRACTS
        if contract.key.startswith("natal_")
        and contract.input_schema is not None
        and "llm_astrology_input_v1" in contract.input_schema.get("required", [])
    ]


def get_canonical_use_case_contract(key: str) -> CanonicalUseCaseContract | None:
    return _CONTRACTS_BY_KEY.get(key)


def get_canonical_output_schema_definition(
    schema_name: str | None,
) -> CanonicalOutputSchemaDefinition | None:
    if not schema_name:
        return None
    return _SCHEMAS_BY_NAME.get(schema_name)


__all__ = [
    "ASTRO_RESPONSE_V1_JSON_SCHEMA",
    "ASTRO_RESPONSE_V3_JSON_SCHEMA",
    "CANONICAL_OUTPUT_SCHEMAS",
    "CANONICAL_USE_CASE_CONTRACTS",
    "CHAT_RESPONSE_V1",
    "CanonicalOutputSchemaDefinition",
    "CanonicalUseCaseContract",
    "THEME_ASTRAL_RESPONSE_SCHEMA",
    "get_canonical_output_schema_definition",
    "get_canonical_use_case_contract",
    "list_canonical_use_case_contracts",
    "list_modern_natal_use_case_contracts",
]
