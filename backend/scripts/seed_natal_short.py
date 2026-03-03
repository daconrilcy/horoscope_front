"""Migration: add natal_interpretation_short use case and prompt to DB.

This script adds the missing `natal_interpretation_short` use case config and
its active prompt version. It reuses the existing `AstroResponse_v1` schema.

Run:
    python backend/scripts/seed_natal_short.py
"""

from sqlalchemy import select

from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal

USE_CASE_KEY = "natal_interpretation_short"
SCHEMA_NAME = "AstroResponse_v1"

DEVELOPER_PROMPT = (
    "Langue : {{locale}}. use_case={{use_case}}.\n"
    "Tu es un astrologue expérimenté, style clair et synthétique.\n\n"
    "Tu interprètes uniquement à partir des données du thème fournies dans {{chart_json}}.\n"
    "Tu n'inventes aucun placement, aspect, maison ou signe.\n\n"
    "Règles de sortie :\n"
    "Tu dois produire un JSON strict conforme au schéma AstroResponse_v1.\n"
    "- title : 5–10 mots.\n"
    "- summary : 3–5 lignes, essentiel uniquement.\n"
    "- sections : inclure 'overall', 'career', 'relationships' (3 sections minimum).\n"
    "- highlights : 3–5 points clés.\n"
    "- advice : 3–5 conseils pratiques et concis.\n"
    "- evidence : liste d'identifiants UPPER_SNAKE_CASE des placements/aspects utilisés."
)


def seed():
    db = SessionLocal()
    try:
        # 1. Fetch AstroResponse_v1 schema (must already exist)
        schema = db.execute(
            select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == SCHEMA_NAME)
        ).scalar_one_or_none()
        if not schema:
            print(f"ERROR: Schema '{SCHEMA_NAME}' not found. Run seed_28_4.py first.")
            return

        # 2. Create or skip use case config
        existing_uc = db.execute(
            select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == USE_CASE_KEY)
        ).scalar_one_or_none()
        if existing_uc:
            print(f"Use case '{USE_CASE_KEY}' already exists — skipping.")
        else:
            print(f"Creating use case '{USE_CASE_KEY}'...")
            existing_uc = LlmUseCaseConfigModel(
                key=USE_CASE_KEY,
                display_name="Interprétation Natale (courte)",
                description="Analyse synthétique du thème de naissance.",
                output_schema_id=str(schema.id),
                safety_profile="astrology",
                interaction_mode="structured",
                user_question_policy="optional",
                required_prompt_placeholders=["chart_json"],
            )
            db.add(existing_uc)
            db.flush()
            print(f"  Created use case key={existing_uc.key}")

        # 3. Create or skip active prompt version
        existing_prompt = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == USE_CASE_KEY,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one_or_none()
        if existing_prompt:
            print(f"Active prompt for '{USE_CASE_KEY}' already exists — skipping.")
        else:
            print(f"Creating prompt for '{USE_CASE_KEY}'...")
            prompt = LlmPromptVersionModel(
                use_case_key=USE_CASE_KEY,
                status=PromptStatus.PUBLISHED,
                model="gpt-4o-mini",
                developer_prompt=DEVELOPER_PROMPT,
                created_by="system",
            )
            db.add(prompt)
            print("  Created prompt.")

        db.commit()
        print(f"\nMigration complete: '{USE_CASE_KEY}' is now available.")
    except Exception as e:
        db.rollback()
        import traceback

        traceback.print_exc()
        print(f"Migration failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
