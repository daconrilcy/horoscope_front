import logging
import uuid
from sqlalchemy import select
from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def utc_now():
    return datetime.now(timezone.utc)

EVENT_GUIDANCE_PROMPT = """Langue de réponse : français ({{locale}}). Contexte : use_case={{use_case}}.

Tu es un astrologue expert. Ton rôle est d'analyser un événement spécifique décrit par l'utilisateur à la lumière de son thème natal.
Événement : {{event_description}}

Règles :
- Analyse comment les transits ou le thème natal influencent cet événement.
- Sois constructif et donne des pistes d'action.
- Utilise AstroResponse_v2.

Format de sortie : JSON strict AstroResponse_v2
- key "event_context" OBLIGATOIRE dans les sections.
"""

TAROT_READING_PROMPT = """Langue de réponse : français ({{locale}}). Contexte : use_case={{use_case}}.

Tu es un tarologue et astrologue. Interprète le tirage de tarot suivant en lien avec le thème natal si possible.
Cartes : {{cards_json}}

Format de sortie : JSON strict AstroResponse_v2
- key "tarot_spread" OBLIGATOIRE dans les sections.
"""

CHAT_ASTROLOGER_PROMPT = """Tu es {{persona_name}}, un astrologue professionnel et bienveillant. 
Réponds aux messages de l'utilisateur en restant fidèle à ta personnalité.
Si l'utilisateur pose une question technique, utilise tes connaissances en astrologie.

Format de sortie : JSON strict ChatResponse_v1
"""

PROMPTS_TO_SEED = [
    {
        "use_case_key": "event_guidance",
        "display_name": "Guidance Événementielle",
        "description": "Analyse d'un événement spécifique via l'astrologie.",
        "interaction_mode": "structured",
        "user_question_policy": "required",
        "persona_strategy": "optional",
        "output_schema_name": "AstroResponse_v2",
        "required_prompt_placeholders": ["event_description"],
        "developer_prompt": EVENT_GUIDANCE_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 4000,
    },
    {
        "use_case_key": "tarot_reading",
        "display_name": "Tirage de Tarot",
        "description": "Interprétation d'un tirage de cartes.",
        "interaction_mode": "structured",
        "user_question_policy": "optional",
        "persona_strategy": "optional",
        "output_schema_name": "AstroResponse_v2",
        "required_prompt_placeholders": ["cards_json"],
        "developer_prompt": TAROT_READING_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 4000,
    },
    {
        "use_case_key": "chat_astrologer",
        "display_name": "Chat Astrologue",
        "description": "Conversation interactive avec l'astrologue virtuel.",
        "interaction_mode": "chat",
        "user_question_policy": "optional",
        "persona_strategy": "required",
        "output_schema_name": "ChatResponse_v1",
        "required_prompt_placeholders": ["persona_name"],
        "developer_prompt": CHAT_ASTROLOGER_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.8,
        "max_output_tokens": 2000,
    },
]

# Schema names that are mandatory for these use cases to function correctly
_REQUIRED_SCHEMAS = {"AstroResponse_v2", "ChatResponse_v1"}

def seed():
    db = SessionLocal()
    try:
        # Resolve and validate required schemas upfront
        schema_map: dict = {}
        for schema_name in _REQUIRED_SCHEMAS:
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == schema_name)
            schema_obj = db.execute(stmt).scalar_one_or_none()
            if schema_obj is None:
                raise RuntimeError(
                    f"Required schema '{schema_name}' not found in DB. "
                    "Run seed_schemas or fix_schemas_strict.py first."
                )
            schema_map[schema_name] = schema_obj

        for config in PROMPTS_TO_SEED:
            key = config["use_case_key"]
            schema = schema_map[config["output_schema_name"]]

            # 1. Ensure Use Case exists
            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
            uc = db.execute(stmt_uc).scalar_one_or_none()

            if not uc:
                logger.info(f"Creating use case config for {key}...")
                uc = LlmUseCaseConfigModel(
                    key=key,
                    display_name=config["display_name"],
                    description=config["description"],
                    interaction_mode=config["interaction_mode"],
                    user_question_policy=config["user_question_policy"],
                    output_schema_id=str(schema.id),
                    persona_strategy=config["persona_strategy"],
                    required_prompt_placeholders=config["required_prompt_placeholders"],
                    safety_profile="astrology",
                )
                db.add(uc)
            else:
                logger.info(f"Updating use case config for {key}...")
                uc.interaction_mode = config["interaction_mode"]
                uc.user_question_policy = config["user_question_policy"]
                uc.persona_strategy = config["persona_strategy"]
                uc.output_schema_id = str(schema.id)

            db.flush()

            # 2. Publish Prompt Version
            stmt_p = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            current_p = db.execute(stmt_p).scalar_one_or_none()

            if current_p:
                current_p.status = PromptStatus.ARCHIVED

            new_v = LlmPromptVersionModel(
                use_case_key=key,
                status=PromptStatus.PUBLISHED,
                developer_prompt=config["developer_prompt"],
                model=config["model"],
                temperature=config["temperature"],
                max_output_tokens=config["max_output_tokens"],
                created_by="system",
                published_at=utc_now(),
            )
            db.add(new_v)
            
        db.commit()
        logger.info("New use cases seed completed successfully.")
    except Exception as e:
        db.rollback()
        logger.exception(f"Seed failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
