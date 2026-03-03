from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import LlmOutputSchemaModel, LlmPersonaModel, LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal
from app.llm_orchestration.models import EVIDENCE_ID_REGEX
from app.llm_orchestration.schemas import _SECTION_KEY_VALUES


class SeedValidationError(Exception):
    """Raised when seed configuration is invalid."""

    pass


CHAT_RESPONSE_V1 = {
    "type": "object",
    "required": ["message"],
    "additionalProperties": False,
    "properties": {
        "message": {"type": "string", "minLength": 1},
        "suggested_replies": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 5,
            "default": [],
        },
        "intent": {
            "type": "string",
            "enum": [
                "ask_birthdata",
                "explain_aspect",
                "offer_tarot",
                "offer_guidance",
                "general",
                None,
            ],  # noqa: E501
        },
        "safety_notes": {"type": "array", "items": {"type": "string"}, "default": []},
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

# The 7 canonical use cases
USE_CASES_CONTRACTS = [
    {
        "key": "natal_interpretation",
        "display_name": "Interprétation Natale",
        "description": "Analyse approfondie du thème de naissance.",
        "output_schema_name": "AstroResponse_v3",  # Story 30-8 T7.2: migrated from v1
        "persona_strategy": "required",
        "safety_profile": "astrology",
        "fallback_use_case_key": "natal_interpretation_short",
        "required_prompt_placeholders": ["chart_json", "persona_name"],
        "interaction_mode": "structured",
        "user_question_policy": "none",
        "input_schema": {
            "type": "object",
            "required": ["chart_json"],
            "properties": {
                "chart_json": {"type": "object"},
                "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
            },
        },
    },
    {
        "key": "natal_interpretation_short",
        "display_name": "Interprétation Natale Courte",
        "description": "Version concise de l'analyse natale.",
        "output_schema_name": "AstroResponse_v1",
        "persona_strategy": "optional",
        "safety_profile": "astrology",
        "fallback_use_case_key": None,
        "required_prompt_placeholders": ["chart_json"],
        "interaction_mode": "structured",
        "user_question_policy": "optional",
        "input_schema": {
            "type": "object",
            "required": ["chart_json"],
            "properties": {
                "chart_json": {"type": "object"},
                "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
            },
        },
    },
    {
        "key": "chat_astrologer",
        "display_name": "Chat Astrologue",
        "description": "Conversation interactive avec l'astrologue virtuel.",
        "output_schema_name": "ChatResponse_v1",
        "persona_strategy": "required",
        "safety_profile": "astrology",
        "fallback_use_case_key": None,
        "required_prompt_placeholders": ["persona_name"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
        "input_schema": {
            "type": "object",
            "required": ["message"],
            "properties": {
                "message": {"type": "string", "maxLength": 1000},
                "conversation_id": {"type": "string"},
                "persona_id": {"type": "string"},
            },
        },
    },
    {
        "key": "tarot_reading",
        "display_name": "Tirage de Tarot",
        "description": "Interprétation d'un tirage de cartes.",
        "output_schema_name": "AstroResponse_v1",
        "persona_strategy": "optional",
        "safety_profile": "astrology",
        "fallback_use_case_key": "natal_interpretation_short",
        "required_prompt_placeholders": ["cards_json"],
        "interaction_mode": "structured",
        "user_question_policy": "optional",
        "input_schema": {
            "type": "object",
            "required": ["cards_json"],
            "properties": {
                "cards_json": {"type": "object"},
                "question": {"type": "string", "maxLength": 200},
            },
        },
    },
    {
        "key": "event_guidance",
        "display_name": "Guidance Événementielle",
        "description": "Analyse d'un événement spécifique via l'astrologie.",
        "output_schema_name": "AstroResponse_v1",
        "persona_strategy": "optional",
        "safety_profile": "astrology",
        "fallback_use_case_key": "natal_interpretation_short",
        "required_prompt_placeholders": ["chart_json", "event_description"],
        "interaction_mode": "chat",
        "user_question_policy": "required",
        "input_schema": {
            "type": "object",
            "required": ["chart_json", "event_description"],
            "properties": {
                "chart_json": {"type": "object"},
                "event_description": {"type": "string", "maxLength": 500},
            },
        },
    },
    {
        "key": "astrologer_selection_help",
        "display_name": "Aide au Choix d'Astrologue",
        "description": "Assistant pour aider l'utilisateur à choisir un expert.",
        "output_schema_name": "ChatResponse_v1",
        "persona_strategy": "forbidden",
        "safety_profile": "support",
        "fallback_use_case_key": None,
        "required_prompt_placeholders": [],
        "interaction_mode": "chat",
        "user_question_policy": "required",
        "input_schema": None,
    },
    {
        "key": "account_support",
        "display_name": "Support Compte",
        "description": "Aide technique pour la gestion du compte utilisateur.",
        "output_schema_name": None,
        "persona_strategy": "forbidden",
        "safety_profile": "support",
        "fallback_use_case_key": None,
        "required_prompt_placeholders": [],
        "interaction_mode": "chat",
        "user_question_policy": "required",
        "input_schema": None,
    },
]


def seed_use_cases(db: Session) -> None:
    # 0. Ensure a default persona exists for 'required' use cases
    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.name == "Astrologue Standard")
    default_persona = db.execute(stmt_persona).scalars().first()

    if not default_persona:
        default_persona = LlmPersonaModel(
            name="Astrologue Standard",
            description="Persona par défaut pour les services d'astrologie.",
            tone="Bienveillant et professionnel",
            verbosity="medium",
            style_markers=["précis", "empathique"],
            boundaries="Ne donne pas de conseils médicaux ou financiers fermes.",
            enabled=True,
        )
        db.add(default_persona)
        db.flush()  # Generate ID

    default_persona_id = str(default_persona.id)

    # 1. Upsert Output Schemas
    # Check if ChatResponse_v1 exists
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "ChatResponse_v1")
    chat_schema = db.execute(stmt).scalar_one_or_none()
    if not chat_schema:
        chat_schema = LlmOutputSchemaModel(
            name="ChatResponse_v1", json_schema=CHAT_RESPONSE_V1, version=1
        )
        db.add(chat_schema)
        db.flush()
    else:
        chat_schema.json_schema = CHAT_RESPONSE_V1

    # Upsert AstroResponse_v1
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "AstroResponse_v1")
    astro_schema = db.execute(stmt).scalar_one_or_none()
    if not astro_schema:
        astro_schema = LlmOutputSchemaModel(
            name="AstroResponse_v1", json_schema=ASTRO_RESPONSE_V1_JSON_SCHEMA, version=1
        )
        db.add(astro_schema)
        db.flush()
    else:
        astro_schema.json_schema = ASTRO_RESPONSE_V1_JSON_SCHEMA

    # Upsert AstroResponse_v3 (Story 30-8 T7.1)
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "AstroResponse_v3")
    astro_v3_schema = db.execute(stmt).scalar_one_or_none()
    if not astro_v3_schema:
        astro_v3_schema = LlmOutputSchemaModel(
            name="AstroResponse_v3", json_schema=ASTRO_RESPONSE_V3_JSON_SCHEMA, version=3
        )
        db.add(astro_v3_schema)
        db.flush()
    else:
        astro_v3_schema.json_schema = ASTRO_RESPONSE_V3_JSON_SCHEMA

    # 2. Upsert Use Cases
    schema_map = {
        "ChatResponse_v1": chat_schema,
        "AstroResponse_v1": astro_schema,
        "AstroResponse_v3": astro_v3_schema,
    }

    for contract in USE_CASES_CONTRACTS:
        stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == contract["key"])
        uc = db.execute(stmt).scalar_one_or_none()

        schema_name = contract["output_schema_name"]
        schema_id = (
            str(schema_map[schema_name].id)
            if schema_name and schema_name in schema_map and schema_map[schema_name]
            else None
        )  # noqa: E501

        if not uc:
            uc = LlmUseCaseConfigModel(
                key=contract["key"],
                display_name=contract["display_name"],
                description=contract["description"],
                input_schema=contract["input_schema"],
                output_schema_id=schema_id,
                persona_strategy=contract["persona_strategy"],
                safety_profile=contract["safety_profile"],
                required_prompt_placeholders=contract["required_prompt_placeholders"],
                fallback_use_case_key=contract["fallback_use_case_key"],
                interaction_mode=contract.get("interaction_mode", "structured"),
                user_question_policy=contract.get("user_question_policy", "none"),
                allowed_persona_ids=[],
            )
            db.add(uc)
        else:
            uc.display_name = contract["display_name"]
            uc.description = contract["description"]
            uc.input_schema = contract["input_schema"]
            uc.output_schema_id = schema_id
            uc.persona_strategy = contract["persona_strategy"]
            uc.safety_profile = contract["safety_profile"]
            uc.required_prompt_placeholders = contract["required_prompt_placeholders"]
            uc.fallback_use_case_key = contract["fallback_use_case_key"]
            uc.interaction_mode = contract.get("interaction_mode", "structured")
            uc.user_question_policy = contract.get("user_question_policy", "none")

        # AC 5 / Issue B: Ensure at least one persona if strategy is required
        if uc.persona_strategy == "required" and not uc.allowed_persona_ids:
            uc.allowed_persona_ids = [default_persona_id]

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_use_cases(session)
        print("Use cases seed completed.")
