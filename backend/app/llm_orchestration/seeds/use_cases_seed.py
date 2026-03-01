from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models import LlmOutputSchemaModel, LlmPersonaModel, LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal


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

# The 7 canonical use cases
USE_CASES_CONTRACTS = [
    {
        "key": "natal_interpretation",
        "display_name": "Interprétation Natale",
        "description": "Analyse approfondie du thème de naissance.",
        "output_schema_name": "AstroResponse_v1",
        "persona_strategy": "required",
        "safety_profile": "astrology",
        "fallback_use_case_key": "natal_interpretation_short",
        "required_prompt_placeholders": ["chart_json", "persona_name"],
        "input_schema": {
            "type": "object",
            "required": ["question", "chart_json"],
            "properties": {
                "question": {"type": "string", "maxLength": 500},
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
        "input_schema": None,
    },
]


# Personas definition
PERSONAS = [
    {
        "name": "Astrologue Standard",
        "description": "Persona par défaut pour les services d'astrologie.",
        "tone": "warm",
        "verbosity": "medium",
        "style_markers": ["précis", "empathique"],
        "boundaries": ["Ne donne pas de conseils médicaux ou financiers fermes."],
    },
    {
        "name": "Luna Céleste",
        "description": "Astrologue depuis 15 ans, spécialisée en astrologie relationnelle.",
        "tone": "warm",
        "verbosity": "medium",
        "style_markers": ["bienveillant", "direct"],
        "boundaries": ["Se concentre sur les relations et le développement personnel."],
    },
    {
        "name": "Orion Mystique",
        "description": "Expert en astrologie prévisionnelle et choix de carrière.",
        "tone": "mystical",
        "verbosity": "high",
        "style_markers": ["analytique", "précis"],
        "boundaries": ["Évite les prédictions fatidiques, privilégie le conseil de carrière."],
    },
    {
        "name": "Stella Nova",
        "description": "Guide spirituel utilisant l'astrologie comme outil d'éveil.",
        "tone": "warm",
        "verbosity": "medium",
        "style_markers": ["doux", "intuitif"],
        "boundaries": ["Ne remplace pas un suivi psychologique."],
    },
    {
        "name": "Atlas Cosmos",
        "description": "Spécialiste de l'astrologie financière et des cycles planétaires.",
        "tone": "rational",
        "verbosity": "medium",
        "style_markers": ["pragmatique", "factuel"],
        "boundaries": ["Conseils basés sur les cycles, pas de garantie de profit."],
    },
]


def seed_use_cases(db: Session) -> None:
    # 0. Ensure personas exist
    persona_ids = []
    for p_data in PERSONAS:
        stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.name == p_data["name"])
        persona = db.execute(stmt_persona).scalar_one_or_none()

        if not persona:
            persona = LlmPersonaModel(
                name=p_data["name"],
                description=p_data["description"],
                tone=p_data["tone"],
                verbosity=p_data["verbosity"],
                style_markers=p_data["style_markers"],
                boundaries=p_data["boundaries"],
                enabled=True,
            )
            db.add(persona)
            db.flush()  # Generate ID
        
        persona_ids.append(str(persona.id))

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

    # Get AstroResponse_v1
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "AstroResponse_v1")
    astro_schema = db.execute(stmt).scalar_one_or_none()

    # 2. Upsert Use Cases
    schema_map = {"ChatResponse_v1": chat_schema, "AstroResponse_v1": astro_schema}

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

        # AC 5 / Issue B: Ensure all seeded personas are allowed if strategy is required
        if uc.persona_strategy == "required":
            # In development, we allow all seeded personas
            # We use a set to avoid duplicates and ensure all current persona_ids are present
            current_allowed = set(uc.allowed_persona_ids or [])
            for pid in persona_ids:
                current_allowed.add(pid)
            uc.allowed_persona_ids = list(current_allowed)

    db.commit()


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_use_cases(session)
        print("Use cases seed completed.")
