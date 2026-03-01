"""
Seed des prompts nataux (Chapter 29) pour le LLMGateway.
Crée et publie les prompts pour natal_interpretation et natal_interpretation_short.
Idempotent : si un prompt PUBLISHED existe déjà, le script le signale et skip.
"""

import logging

from sqlalchemy import select

from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, utc_now

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NATAL_SHORT_PROMPT = """Langue cible : {{locale}}. Contexte : use_case={{use_case}}.

Tu es un astrologue expérimenté.
Tu interprètes le thème natal fourni de façon claire, moderne et non fataliste.

Tu travailles UNIQUEMENT à partir des données du thème natal suivantes :
{{chart_json}}

Règles absolues :
- N'invente aucun placement planétaire, aspect ou maison non présent dans les données
- Parle de tendances et de potentiels, jamais de certitudes
- Pas de diagnostic médical, légal ou financier ferme
- Si tu es incertain sur un point, reste général

Format de sortie (JSON strict AstroResponse_v1) :
- title : titre accrocheur, 5–10 mots
- summary : introduction du profil natal, 4–6 phrases
- sections : minimum 3 parmi [overall, career, relationships, inner_life, daily_life]
  - heading : titre de section percutant
  - content : 3–5 phrases par section, concret et actionnable
- highlights : 3–5 points forts ou traits marquants du thème
- advice : 3–5 conseils pratiques et positifs
- evidence : identifiants UPPER_SNAKE_CASE des placements réellement utilisés
  ex: SUN_TAURUS_H10, MOON_CANCER, ASPECT_SUN_MOON_TRINE, ASC_SCORPIO
- disclaimers : 1 note de prudence générale (astrologie = piste de réflexion)"""

NATAL_COMPLETE_PROMPT = """Langue cible : {{locale}}. Contexte : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert.
Adapte ton style et ton ton à cette persona tout en restant professionnel et bienveillant.

Tu réalises une interprétation approfondie et personnalisée du thème natal suivant :
{{chart_json}}

Règles absolues :
- Tu te bases UNIQUEMENT sur les données du thème natal fournies
- N'invente aucun placement, aspect ou maison non présent dans les données
- Parle de tendances, potentiels et dynamiques — jamais de prédictions certaines
- Pas de diagnostic médical, légal, financier ou psychologique ferme
- Si tu es incertain, reste nuancé et général

Niveau de détail : analyse complète et approfondie avec nuances

Format de sortie (JSON strict AstroResponse_v1) :
- title : titre personnalisé reflétant l'essentiel du thème, 5–12 mots
- summary : portrait astrologique complet, 6–10 phrases, ton de la persona
- sections : minimum 5 parmi [overall, career, relationships, inner_life, daily_life,
                              strengths, challenges]
  - heading : titre de section évocateur (max 80 chars)
  - content : analyse détaillée, 4–7 phrases, concret et personnalisé (max 2500 chars)
- highlights : 5–8 points forts, traits dominants ou configurations remarquables
- advice : 5–8 conseils actionnables, positifs et spécifiques au thème
- evidence : identifiants UPPER_SNAKE_CASE de TOUS les placements et aspects utilisés
  Exemples : SUN_TAURUS_H10, MOON_CANCER_H8, ASC_SCORPIO, MC_LEO,
             ASPECT_SUN_MOON_TRINE_ORB0, ASPECT_SATURN_ASC_SQUARE_ORB2,
             SUN_RETROGRADE (si applicable)
- disclaimers : 1–2 notes sur la nature indicative de l'astrologie"""

PROMPTS_TO_SEED = [
    {
        "use_case_key": "natal_interpretation_short",
        "display_name": "Interprétation Natale (Courte)",
        "description": "Analyse rapide du thème de naissance.",
        "persona_strategy": "optional",
        "required_prompt_placeholders": ["chart_json", "locale", "use_case"],
        "developer_prompt": NATAL_SHORT_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation_short",
        "eval_failure_threshold": 0.10, # Strict gate for free tier
    },
    {
        "use_case_key": "natal_interpretation",
        "display_name": "Interprétation Natale (Complète)",
        "description": "Analyse approfondie du thème de naissance avec persona.",
        "persona_strategy": "required",
        "required_prompt_placeholders": ["chart_json", "persona_name", "locale", "use_case"],
        "developer_prompt": NATAL_COMPLETE_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 3000,
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation",
        "eval_failure_threshold": 0.20, # More tolerant for complex long prompts
    },
]


def seed_prompts():
    """Seeds the database with natal interpretation prompts."""
    db = SessionLocal()
    keys_to_invalidate = set()
    try:
        # Get AstroResponse_v1 schema id
        stmt_schema = select(LlmOutputSchemaModel).where(
            LlmOutputSchemaModel.name == "AstroResponse_v1"
        )
        astro_schema = db.execute(stmt_schema).scalar_one_or_none()
        if not astro_schema:
            logger.error("AstroResponse_v1 schema not found. Run seed_28_4.py or check migrations.")
            return

        for config in PROMPTS_TO_SEED:
            key = config["use_case_key"]

            # 1. Ensure Use Case exists and is updated
            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
            uc = db.execute(stmt_uc).scalar_one_or_none()

            if not uc:
                logger.info(f"Creating use case config for {key}...")
                uc = LlmUseCaseConfigModel(
                    key=key,
                    display_name=config["display_name"],
                    description=config["description"],
                    output_schema_id=str(astro_schema.id),
                    persona_strategy=config["persona_strategy"],
                    required_prompt_placeholders=config["required_prompt_placeholders"],
                    safety_profile="astrology",
                    eval_fixtures_path=config["eval_fixtures_path"],
                    eval_failure_threshold=config["eval_failure_threshold"],
                )
                db.add(uc)
            else:
                logger.info(f"Updating use case config for {key}...")
                uc.display_name = config["display_name"]
                uc.description = config["description"]
                uc.output_schema_id = str(astro_schema.id)
                uc.persona_strategy = config["persona_strategy"]
                uc.required_prompt_placeholders = config["required_prompt_placeholders"]
                uc.eval_fixtures_path = config["eval_fixtures_path"]
                uc.eval_failure_threshold = config["eval_failure_threshold"]

            db.flush()

            # 2. Lint the prompt
            lint_res = PromptLint.lint_prompt(
                config["developer_prompt"],
                use_case_required_placeholders=config["required_prompt_placeholders"],
            )
            if not lint_res.passed:
                raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")

            # 3. Check if current published version is identical
            stmt_p = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            current_p = db.execute(stmt_p).scalar_one_or_none()

            if current_p and current_p.developer_prompt == config["developer_prompt"]:
                logger.info(f"Prompt for {key} already published and identical. Skipping.")
                continue

            # 4. Create and publish new version
            logger.info(f"Publishing new prompt version for {key}...")
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
            db.flush()

            # 5. Prepare invalidation
            keys_to_invalidate.add(key)
            logger.info(f"Prompt for {key} prepared for commit.")

        db.commit()

        # Invalidate after successful commit
        for key in keys_to_invalidate:
            PromptRegistryV2.invalidate_cache(key)

        logger.info("Seed process completed successfully.")

    except Exception as e:
        db.rollback()
        logger.exception(f"Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_prompts()
