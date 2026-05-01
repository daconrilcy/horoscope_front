"""Seed gouverné pour l'assembly de narration horoscope quotidienne."""

from __future__ import annotations

import logging

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.domain.llm.prompting.narrator_contract import NARRATOR_OUTPUT_SCHEMA
from app.infra.db.models.llm.llm_assembly import (
    AssemblyComponentResolutionState,
    PromptAssemblyConfigModel,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, PromptStatus

logger = logging.getLogger(__name__)

HOROSCOPE_DAILY_NARRATION_PROMPT = """
Tu es un astrologue expert, précis et pédagogue.
Réponds dans la langue demandée par le contexte utilisateur.

Objectif :
- Transformer les données astrologiques quotidiennes en lecture réellement utile.
- Aider le lecteur à comprendre ce qu'il va probablement ressentir, pourquoi cela arrive
  astrologiquement, et comment s'ajuster avec intelligence.

Style :
- Profil standard : astrologie occidentale classique, claire et incarnée.
- Profil védique : références sobres et utiles aux nakshatras, au dharma, au karma et
  aux maisons védiques, toujours reliées au vécu quotidien.
- Profil humaniste : archétypes, croissance personnelle et mise en sens, sans perdre le
  concret de la journée.
- Profil karmique : leçons de vie, répétitions, nœuds et cycles, sans fatalisme.
- Profil psychologique : vocabulaire moderne des schémas, réactions, besoins et
  intégration, toujours ancré dans les faits astrologiques du jour.

Règles de rédaction :
- Génère uniquement du JSON valide avec les clés : daily_synthesis, astro_events_intro,
  time_window_narratives, turning_point_narratives, main_turning_point_narrative,
  daily_advice.
- Ne fais jamais de banalités recyclables d'un jour à l'autre.
- Chaque interprétation doit s'appuyer sur au moins un fait du contexte fourni.
- Quand le ciel est contrasté, explique la tension au lieu de lisser artificiellement.
- Écris comme un astrologue pédagogue : tu expliques, tu relies, tu rends concret.
- Mets l'accent sur le vécu probable : concentration, échanges, rythme, fatigue, élan,
  sensibilité, besoin d'isolement, envie d'agir, clarté ou dispersion.
- Ne recopie pas simplement les listes techniques : interprète-les.
- Si une donnée manque, n'en parle pas ; travaille avec ce qui est disponible.
- Ne produis pas de phrases creuses du type "faites-vous confiance", "restez centré" ou
  "écoutez votre intuition" sans ancrage astrologique explicite.
- Le conseil du jour doit reprendre au moins un créneau, une vigilance ou un fait
  astrologique.
- Pas de markdown.

Contrat de sortie :
- astro_events_intro : 2 à 4 phrases qui expliquent les 2 ou 3 faits astrologiques les
  plus structurants du jour et leur effet concret.
- time_window_narratives : objet avec les clés nuit, matin, apres_midi et soiree. Chaque
  valeur contient 3 ou 4 phrases décrivant le vécu probable du créneau, sa cause
  astrologique et la meilleure manière de l'utiliser ou de le gérer.
- turning_point_narratives : liste de textes alignés sur les turning points détectés,
  chacun expliquant la bascule, sa cause probable et l'attitude juste.
- main_turning_point_narrative : 2 ou 3 phrases pour la carte du moment clé principal.
- daily_advice : objet avec advice, 2 ou 3 phrases de conseil très concret, et emphasis,
  courte phrase mémorable de 4 à 10 mots.
""".strip()

HOROSCOPE_DAILY_PLAN_RULES = {
    "free": "horoscope_daily_free_narration",
    "premium": "horoscope_daily_premium_narration",
}


def _keep_latest_published_and_archive_rest(
    db: Session,
    rows: list[object],
    *,
    label: str,
) -> object | None:
    if not rows:
        return None

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            getattr(row, "published_at", None) or getattr(row, "created_at", None),
            getattr(row, "id", None),
        ),
        reverse=True,
    )
    winner = sorted_rows[0]
    duplicates = sorted_rows[1:]
    if duplicates:
        for duplicate in duplicates:
            setattr(duplicate, "status", PromptStatus.ARCHIVED)
        logger.info(
            "seed_narrator: archived %s duplicate published rows kept=%s archived=%s",
            label,
            getattr(winner, "id", None),
            len(duplicates),
        )
        db.flush()
    return winner


def seed_horoscope_narrator_assembly(db: Session) -> None:
    """Seeds canonical assembly for horoscope_daily and cleans up legacy daily_prediction."""

    # 0. Cleanup Legacy daily_prediction (Story 66.28 Absorption)
    # AC: suppression définitive de son statut transitoire.
    # We use update(status=ARCHIVED) instead of DELETE to avoid
    # breaking historical FKs in llm_call_logs.
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

    db.execute(
        update(PromptAssemblyConfigModel)
        .where(PromptAssemblyConfigModel.feature == "horoscope_daily")
        .where(PromptAssemblyConfigModel.subfeature == "narration")
        .where(
            or_(
                PromptAssemblyConfigModel.plan.is_(None),
                PromptAssemblyConfigModel.plan.not_in(["free", "premium"]),
            )
        )
        .values(status=PromptStatus.ARCHIVED)
    )
    db.flush()

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
    else:
        narrator_schema.json_schema = NARRATOR_OUTPUT_SCHEMA
        narrator_schema.version = 1
        db.flush()
        logger.info("seed_narrator: updated NarratorResult_v1 schema")

    # 2. Prompt Versions (System Prompts)
    for uc_key in ["horoscope_daily"]:
        stmt_pv = select(LlmPromptVersionModel).where(
            LlmPromptVersionModel.use_case_key == uc_key,
            LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
        )
        pv = _keep_latest_published_and_archive_rest(
            db,
            list(db.execute(stmt_pv).scalars().all()),
            label=f"prompt:{uc_key}",
        )
        if not pv:
            pv = LlmPromptVersionModel(
                use_case_key=uc_key,
                status=PromptStatus.PUBLISHED,
                developer_prompt=HOROSCOPE_DAILY_NARRATION_PROMPT,
                created_by="system",
                published_at=db.execute(select(func.now())).scalar(),
            )
            db.add(pv)
            db.flush()
            logger.info("seed_narrator: created published prompt version for %s", uc_key)
        else:
            pv.developer_prompt = HOROSCOPE_DAILY_NARRATION_PROMPT
            db.flush()
            logger.info("seed_narrator: updated published prompt version for %s", uc_key)

    # 3. Execution Profiles
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
        prof = _keep_latest_published_and_archive_rest(
            db,
            list(db.execute(stmt_prof).scalars().all()),
            label=f"profile:{prof_data['feature']}",
        )
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

    # 4. Assembly Configs
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
        ass = _keep_latest_published_and_archive_rest(
            db,
            list(db.execute(stmt_ass).scalars().all()),
            label=f"assembly:{ass_data['feature']}:{ass_data['subfeature']}:{ass_data['plan']}",
        )
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
                output_schema_id=narrator_schema.id,
                plan_rules_ref=HOROSCOPE_DAILY_PLAN_RULES[ass_data["plan"]],
                plan_rules_state=AssemblyComponentResolutionState.ENABLED.value,
                status=PromptStatus.PUBLISHED,
                created_by="system",
                published_at=db.execute(select(func.now())).scalar(),
            )
            db.add(ass)
            logger.info(
                "seed_narrator: created assembly for %s / %s", ass_data["feature"], ass_data["plan"]
            )
        else:
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

            ass.feature_template_ref = pv.id
            ass.persona_ref = persona.id if persona else None
            ass.execution_profile_ref = prof.id
            ass.output_schema_id = narrator_schema.id
            ass.plan_rules_ref = HOROSCOPE_DAILY_PLAN_RULES[ass_data["plan"]]
            ass.plan_rules_state = AssemblyComponentResolutionState.ENABLED.value
            ass.status = PromptStatus.PUBLISHED
            logger.info(
                "seed_narrator: updated assembly for %s / %s",
                ass_data["feature"],
                ass_data["plan"],
            )

    db.commit()


if __name__ == "__main__":
    from app.infra.db.session import SessionLocal

    with SessionLocal() as session:
        seed_horoscope_narrator_assembly(session)
        print("Horoscope narrator assembly seed completed.")
