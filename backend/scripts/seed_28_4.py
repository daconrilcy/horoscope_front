from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal


def seed():
    db = SessionLocal()
    try:
        # 1. Schémas
        chat_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["message", "suggested_replies"],
            "properties": {
                "message": {"type": "string", "minLength": 1, "maxLength": 2500},
                "suggested_replies": {
                    "type": "array",
                    "maxItems": 5,
                    "items": {"type": "string", "minLength": 1, "maxLength": 80},
                },
                "intent": {
                    "type": "string",
                    "enum": [
                        "clarify_question",
                        "ask_birth_data",
                        "explain_natal_basics",
                        "offer_natal_interpretation",
                        "offer_tarot_reading",
                        "offer_event_guidance",
                        "handoff_to_support",
                        "close_conversation",
                    ],
                },
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "safety_notes": {
                    "type": "array",
                    "maxItems": 3,
                    "items": {"type": "string", "maxLength": 200},
                },
            },
        }

        astro_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["title", "summary", "sections", "highlights", "advice", "evidence"],
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
                                ],  # noqa: E501
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
                    "items": {"type": "string", "minLength": 1, "maxLength": 160},
                },  # noqa: E501
                "advice": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 10,
                    "items": {"type": "string", "minLength": 1, "maxLength": 160},
                },  # noqa: E501
                "evidence": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 40,
                    "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,60}$"},
                },
                "disclaimers": {
                    "type": "array",
                    "maxItems": 3,
                    "items": {"type": "string", "maxLength": 200},
                },  # noqa: E501
            },
        }

        s_chat = LlmOutputSchemaModel(name="ChatResponse_v1", json_schema=chat_schema)
        s_astro = LlmOutputSchemaModel(name="AstroResponse_v1", json_schema=astro_schema)
        db.add_all([s_chat, s_astro])
        db.flush()

        # 2. Use Cases
        use_cases = [
            LlmUseCaseConfigModel(
                key="chat",
                display_name="Chat Astrologue",
                description="Conversation interactive avec l'astrologue virtuel.",
                output_schema_id=str(s_chat.id),
                safety_profile="astrology",
            ),
            LlmUseCaseConfigModel(
                key="natal_interpretation",
                display_name="Interprétation Natale",
                description="Analyse approfondie du thème de naissance.",
                output_schema_id=str(s_astro.id),
                safety_profile="astrology",
            ),
        ]
        db.add_all(use_cases)
        db.flush()

        # 3. Prompts
        p_chat = LlmPromptVersionModel(
            use_case_key="chat",
            status=PromptStatus.PUBLISHED,
            model="gpt-4o-mini",
            developer_prompt=(
                "Tu réponds en français si {{locale}} est 'fr', sinon dans la langue de {{locale}}.\n"  # noqa: E501
                "Contexte : use_case={{use_case}}.\n"
                "Tu es en conversation. Réponds au dernier message utilisateur uniquement.\n\n"
                "Règles de sortie :\n"
                "Tu dois produire un JSON strict conforme au schéma ChatResponse_v1.\n"
                "- message : 1 à 6 phrases, ton conversationnel.\n"
                "- suggested_replies : 3 à 5 propositions courtes, actionnables.\n"
                "Si des données de naissance manquent et qu’elles sont nécessaires : intent='ask_birth_data'.\n"  # noqa: E501
                "Sinon choisis l’intent le plus pertinent, ou omets-le."
            ),
            created_by="system",
        )
        p_natal = LlmPromptVersionModel(
            use_case_key="natal_interpretation",
            status=PromptStatus.PUBLISHED,
            model="gpt-4o-mini",
            developer_prompt=(
                "Langue : {{locale}}. use_case={{use_case}}.\n"
                "Tu es un astrologue expérimenté, style clair, moderne, non fataliste.\n\n"
                "Tu interprètes uniquement à partir des données du thème fournies dans {{chart_json}}.\n"  # noqa: E501
                "Tu n’inventes aucun placement, aspect, maison ou signe. Si tu es incertain, tu restes général.\n\n"  # noqa: E501
                "Règles de sortie :\n"
                "Tu dois produire un JSON strict conforme au schéma AstroResponse_v1.\n"
                "- title : 5–10 mots.\n"
                "- summary : 6–10 lignes max.\n"
                "- sections : inclure au minimum 'overall', 'career', 'relationships', 'inner_life', 'daily_life'.\n"  # noqa: E501
                "- highlights : 5–8 points.\n"
                "- advice : 5–8 conseils pratiques.\n"
                "- evidence : liste d’identifiants UPPER_SNAKE_CASE des placements/aspects réellement utilisés."  # noqa: E501
            ),
            created_by="system",
        )
        db.add_all([p_chat, p_natal])

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
