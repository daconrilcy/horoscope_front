from __future__ import annotations

import logging

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.llm_orchestration.narrator_contract import NARRATOR_OUTPUT_SCHEMA

logger = logging.getLogger(__name__)


def seed_horoscope_narrator_assembly(db: Session) -> None:
    """Seeds canonical assembly for horoscope_daily and cleans up legacy daily_prediction."""

    # 0. Cleanup Legacy daily_prediction (Story 66.28 Absorption)
    # AC: suppression définitive de son statut transitoire.
    # We use update(status=ARCHIVED) instead of DELETE to avoid breaking historical FKs in llm_call_logs.
    legacy_key = "daily_prediction"

    # 1. Assemblies
    db.execute(
        update(PromptAssemblyConfigModel)
        .where(PromptAssemblyConfigModel.feature == legacy_key)
        .values(status=PromptStatus.ARCHIVED)
    )
    # 2. Prompt Versions
    db.execute(
        update(LlmPromptVersionModel)
        .where(LlmPromptVersionModel.use_case_key == legacy_key)
        .values(status=PromptStatus.ARCHIVED)
    )
    # 3. Execution Profiles
    db.execute(
        update(LlmExecutionProfileModel)
        .where(LlmExecutionProfileModel.feature == legacy_key)
        .values(status=PromptStatus.ARCHIVED)
    )
    # 4. Use Case Configs
    # Note: UseCaseConfigModel doesn't have a status, but archiving its versions and assemblies
    # effectively disables it for the gateway.

    db.flush()
    logger.info("seed_narrator: archived legacy %s artifacts", legacy_key)

    # 1. Output Schema
    stmt_schema = select(LlmOutputSchemaModel).where(
        LlmOutputSchemaModel.name == "NarratorResult_v1"
    )
    narrator_schema = db.execute(stmt_schema).scalar_one_or_none()
    if not narrator_schema:
        narrator_schema = LlmOutputSchemaModel(
            name="NarratorResult_v1", json_schema=NARRATOR_OUTPUT_SCHEMA, version=1
        )
        db.add(narrator_schema)
        db.flush()
        logger.info("seed_narrator: created NarratorResult_v1 schema")

    # 2. Use Cases
    use_cases = [
        {
            "key": "horoscope_daily",
            "display_name": "Horoscope Quotidien Canonique",
            "description": "Narration de l'horoscope quotidien (free/premium).",
        },
    ]

    for uc_data in use_cases:
        stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == uc_data["key"])
        uc = db.execute(stmt_uc).scalar_one_or_none()
        if not uc:
            uc = LlmUseCaseConfigModel(
                key=uc_data["key"],
                display_name=uc_data["display_name"],
                description=uc_data["description"],
                output_schema_id=str(narrator_schema.id),
                persona_strategy="required",
                interaction_mode="structured",
                user_question_policy="none",
                safety_profile="astrology",
                required_prompt_placeholders=["question"],  # standard placeholder
            )
            db.add(uc)
            db.flush()
            logger.info("seed_narrator: created use case %s", uc_data["key"])

    # 3. Prompt Versions (System Prompts)
    system_prompt_fr = (
        "Tu es un astrologue expert, précis et pédagogue. "
        "Réponds en français. "
        "Génère uniquement du JSON valide avec les clés : "
        "daily_synthesis (string), astro_events_intro (string), "
        "time_window_narratives (objet avec clés nuit/matin/apres_midi/soiree), "
        "turning_point_narratives (liste de strings), "
        "main_turning_point_narrative (string), "
        "daily_advice (objet avec advice et emphasis). "
        "Apporte de la valeur : explique ce qui se joue, pourquoi astrologiquement, "
        "et quelle attitude adopter. Évite les banalités et le remplissage. "
        "Pas de markdown."
    )

    for uc_key in ["horoscope_daily"]:
        stmt_pv = select(LlmPromptVersionModel).where(
            LlmPromptVersionModel.use_case_key == uc_key,
            LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
        )
        pv = db.execute(stmt_pv).scalar_one_or_none()
        if not pv:
            pv = LlmPromptVersionModel(
                use_case_key=uc_key,
                status=PromptStatus.PUBLISHED,
                developer_prompt=system_prompt_fr,
                model="gpt-4o",
                temperature=0.7,
                max_output_tokens=3000,
                created_by="system",
                published_at=db.execute(select(func.now())).scalar(),
            )
            db.add(pv)
            db.flush()
            logger.info("seed_narrator: created published prompt version for %s", uc_key)

    # 4. Execution Profiles
    profiles = [
        {
            "name": "Horoscope Narration Standard",
            "feature": "horoscope_daily",
            "max_output_tokens": 3000,
        },
    ]

    for prof_data in profiles:
        stmt_prof = select(LlmExecutionProfileModel).where(
            LlmExecutionProfileModel.feature == prof_data["feature"],
            LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
        )
        prof = db.execute(stmt_prof).scalar_one_or_none()
        if not prof:
            prof = LlmExecutionProfileModel(
                name=prof_data["name"],
                feature=prof_data["feature"],
                provider="openai",
                model="gpt-4o",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="structured_json",
                max_output_tokens=prof_data["max_output_tokens"],
                status=PromptStatus.PUBLISHED,
                created_by="system",
                published_at=db.execute(select(func.now())).scalar(),
            )
            db.add(prof)
            db.flush()
            logger.info("seed_narrator: created execution profile for %s", prof_data["feature"])

    # 5. Assembly Configs
    # We need a persona
    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.enabled)
    persona = db.execute(stmt_persona).scalars().first()

    if not persona:
        logger.error("seed_narrator: No active persona found. Cannot seed assemblies.")
        return

    assemblies = [
        {
            "feature": "horoscope_daily",
            "subfeature": "narration",
            "plan": "free",
            "max_tokens": 1300,
        },
        {
            "feature": "horoscope_daily",
            "subfeature": "narration",
            "plan": "premium",
            "max_tokens": 3000,
        },
    ]

    for ass_data in assemblies:
        stmt_ass = select(PromptAssemblyConfigModel).where(
            PromptAssemblyConfigModel.feature == ass_data["feature"],
            PromptAssemblyConfigModel.subfeature == ass_data["subfeature"],
            PromptAssemblyConfigModel.plan == ass_data["plan"],
            PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
        )
        ass = db.execute(stmt_ass).scalar_one_or_none()
        if not ass:
            # Find template and profile
            pv = db.execute(
                select(LlmPromptVersionModel).where(
                    LlmPromptVersionModel.use_case_key == ass_data["feature"],
                    LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
                )
            ).scalar_one()

            prof = db.execute(
                select(LlmExecutionProfileModel).where(
                    LlmExecutionProfileModel.feature == ass_data["feature"],
                    LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
                )
            ).scalar_one()

            ass = PromptAssemblyConfigModel(
                feature=ass_data["feature"],
                subfeature=ass_data["subfeature"],
                plan=ass_data["plan"],
                locale="fr-FR",
                feature_template_ref=pv.id,
                persona_ref=persona.id if persona else None,
                execution_profile_ref=prof.id,
                execution_config={
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_output_tokens": ass_data["max_tokens"],
                    "timeout_seconds": 60,
                },
                status=PromptStatus.PUBLISHED,
                created_by="system",
                published_at=db.execute(select(func.now())).scalar(),
            )
            db.add(ass)
            logger.info(
                "seed_narrator: created assembly for %s / %s", ass_data["feature"], ass_data["plan"]
            )

    db.commit()


if __name__ == "__main__":
    from app.infra.db.session import SessionLocal

    with SessionLocal() as session:
        seed_horoscope_narrator_assembly(session)
        print("Horoscope narrator assembly seed completed.")
