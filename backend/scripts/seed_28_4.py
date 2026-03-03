from sqlalchemy import select

from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal


def seed():
    db = SessionLocal()
    try:
        # 1. Schémas
        schemas_to_seed = {
            "ChatResponse_v1": {
                "type": "object",
                "additionalProperties": False,
                # strict=true requires ALL properties in required.
                # Nullable fields use {"type": ["string", "null"]} pattern.
                "required": [
                    "message",
                    "suggested_replies",
                    "intent",
                    "confidence",
                    "safety_notes",
                ],
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
                            "offer_tarot_reading",
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
            },
            "AstroResponse_v1": {
                "type": "object",
                "additionalProperties": False,
                # strict=true requires ALL properties to be listed in required.
                # Optional arrays must be required but can be empty (no minItems).
                "required": [
                    "title",
                    "summary",
                    "sections",
                    "highlights",
                    "advice",
                    "evidence",
                    "disclaimers",
                ],
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
                                "key": {
                                    "type": "string",
                                    "enum": [
                                        "overall",
                                        "career",
                                        "relationships",
                                        "inner_life",
                                        "daily_life",
                                        "strengths",
                                        "challenges",
                                        "tarot_spread",
                                        "event_context",
                                    ],
                                },
                                "heading": {"type": "string", "minLength": 1, "maxLength": 80},
                                "content": {"type": "string", "minLength": 1, "maxLength": 2500},
                            },
                        },
                    },
                    "highlights": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 10,
                        "items": {"type": "string", "minLength": 1, "maxLength": 360},
                    },
                    "advice": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 10,
                        "items": {"type": "string", "minLength": 1, "maxLength": 360},
                    },
                    "evidence": {
                        "type": "array",
                        "minItems": 0,
                        "maxItems": 40,
                        "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,80}$"},
                    },
                    "disclaimers": {
                        "type": "array",
                        "maxItems": 3,
                        "items": {"type": "string", "maxLength": 200},
                    },
                },
            },
        }

        schema_instances = {}
        for name, js in schemas_to_seed.items():
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == name)
            existing = db.execute(stmt).scalar_one_or_none()
            if not existing:
                print(f"Creating schema {name}...")
                existing = LlmOutputSchemaModel(name=name, json_schema=js)
                db.add(existing)
                db.flush()
            schema_instances[name] = existing

        # 2. Use Cases
        use_cases_to_seed = [
            {
                "key": "chat",
                "display_name": "Chat Astrologue",
                "description": "Conversation interactive avec l'astrologue virtuel.",
                "output_schema_id": str(schema_instances["ChatResponse_v1"].id),
            },
            {
                "key": "natal_interpretation",
                "display_name": "Interprétation Natale",
                "description": "Analyse approfondie du thème de naissance.",
                "output_schema_id": str(schema_instances["AstroResponse_v1"].id),
            },
        ]

        for uc_data in use_cases_to_seed:
            stmt = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == uc_data["key"])
            existing = db.execute(stmt).scalar_one_or_none()
            if not existing:
                print(f"Creating use case {uc_data['key']}...")
                existing = LlmUseCaseConfigModel(
                    key=uc_data["key"],
                    display_name=uc_data["display_name"],
                    description=uc_data["description"],
                    output_schema_id=uc_data["output_schema_id"],
                    safety_profile="astrology",
                )
                db.add(existing)
                db.flush()

        # 3. Prompts
        prompts_to_seed = [
            {
                "use_case_key": "chat",
                "developer_prompt": (
                    "Tu réponds en français si {{locale}} est 'fr', sinon dans la langue de {{locale}}.\n"
                    "Contexte : use_case={{use_case}}.\n"
                    "Tu es en conversation. Réponds au dernier message utilisateur uniquement.\n\n"
                    "Règles de sortie :\n"
                    "Tu dois produire un JSON strict conforme au schéma ChatResponse_v1.\n"
                    "- message : 1 à 6 phrases, ton conversationnel.\n"
                    "- suggested_replies : 3 à 5 propositions courtes, actionnables.\n"
                    "Si des données de naissance manquent et qu’elles sont nécessaires : intent='ask_birth_data'.\n"
                    "Sinon choisis l’intent le plus pertinent, ou omets-le."
                ),
            },
            {
                "use_case_key": "natal_interpretation",
                "developer_prompt": (
                    "Langue : {{locale}}. use_case={{use_case}}.\n"
                    "Tu es un astrologue expérimenté, style clair, moderne, non fataliste.\n\n"
                    "Tu interprètes uniquement à partir des données du thème fournies dans {{chart_json}}.\n"
                    "Tu n’inventes aucun placement, aspect, maison ou signe. Si tu es incertain, tu restes général.\n\n"
                    "Règles de sortie :\n"
                    "Tu dois produire un JSON strict conforme au schéma AstroResponse_v1.\n"
                    "- title : 5–10 mots.\n"
                    "- summary : 6–10 lignes max.\n"
                    "- sections : inclure au minimum 'overall', 'career', 'relationships', 'inner_life', 'daily_life'.\n"
                    "- highlights : 5–8 points.\n"
                    "- advice : 5–8 conseils pratiques.\n"
                    "- evidence : liste d’identifiants UPPER_SNAKE_CASE des placements/aspects réellement utilisés."
                ),
            },
        ]

        for p_data in prompts_to_seed:
            stmt = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == p_data["use_case_key"],
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            existing = db.execute(stmt).scalar_one_or_none()
            if not existing:
                print(f"Creating prompt for {p_data['use_case_key']}...")
                prompt = LlmPromptVersionModel(
                    use_case_key=p_data["use_case_key"],
                    status=PromptStatus.PUBLISHED,
                    model="gpt-4o-mini",
                    developer_prompt=p_data["developer_prompt"],
                    created_by="system",
                )
                db.add(prompt)

        db.commit()
        print("Seed 28.4 completed successfully.")
    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        print(f"Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
