from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus

logger = logging.getLogger(__name__)


def seed_66_20_taxonomy(db: Session) -> None:
    """Finalize canonical taxonomy for chat, guidance and natal (Story 66.20)."""

    # 1. Get default persona
    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.enabled)
    persona = db.execute(stmt_persona).scalars().first()
    if not persona:
        logger.warning("seed_66_20_taxonomy: no enabled persona found")
        return
    persona_id = persona.id

    # 2. Define target assemblies
    # (feature, subfeature, plan, template_key)
    target_assemblies = [
        # CHAT
        ("chat", "astrologer", "free", "chat_astrologer"),
        ("chat", "astrologer", "premium", "chat_astrologer"),
        # GUIDANCE
        ("guidance", "daily", "free", "guidance_daily"),
        ("guidance", "daily", "premium", "guidance_daily"),
        ("guidance", "weekly", "free", "guidance_weekly"),
        ("guidance", "weekly", "premium", "guidance_weekly"),
        ("guidance", "contextual", "free", "guidance_contextual"),
        ("guidance", "contextual", "premium", "guidance_contextual"),
        ("guidance", "event", "free", "event_guidance"),
        ("guidance", "event", "premium", "event_guidance"),
        # NATAL
        ("natal", "interpretation", "free", "natal_interpretation_short"),
        ("natal", "interpretation", "premium", "natal_interpretation"),
        ("natal", "psy_profile", "premium", "natal_psy_profile"),
        ("natal", "shadow_integration", "premium", "natal_shadow_integration"),
        ("natal", "leadership_workstyle", "premium", "natal_leadership_workstyle"),
        ("natal", "creativity_joy", "premium", "natal_creativity_joy"),
        ("natal", "relationship_style", "premium", "natal_relationship_style"),
        ("natal", "community_networks", "premium", "natal_community_networks"),
        ("natal", "values_security", "premium", "natal_values_security"),
        ("natal", "evolution_path", "premium", "natal_evolution_path"),
    ]

    for f, sf, p, t_key in target_assemblies:
        # A. Find template
        stmt_t = (
            select(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == t_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            .order_by(LlmPromptVersionModel.created_at.desc())
        )
        template = db.execute(stmt_t).scalars().first()

        if not template:
            logger.warning(f"seed_66_20_taxonomy: template {t_key} not found for {f}/{sf}")
            continue

        # B. Upsert Assembly
        stmt_exists = select(PromptAssemblyConfigModel).where(
            PromptAssemblyConfigModel.feature == f,
            PromptAssemblyConfigModel.subfeature == sf,
            PromptAssemblyConfigModel.plan == p,
            PromptAssemblyConfigModel.locale == "fr-FR",
        )
        existing = db.execute(stmt_exists).scalar_one_or_none()

        if not existing:
            new_asm = PromptAssemblyConfigModel(
                feature=f,
                subfeature=sf,
                plan=p,
                locale="fr-FR",
                feature_template_ref=template.id,
                persona_ref=persona_id,
                execution_config={
                    "model": template.model or "gpt-4o",
                    "temperature": template.temperature or 0.7,
                    "max_output_tokens": template.max_output_tokens or 2000,
                    "timeout_seconds": 60,
                },
                status=PromptStatus.PUBLISHED,
                created_by="system",
            )
            db.add(new_asm)
            logger.info(f"seed_66_20_taxonomy: created assembly {f}/{sf}/{p}")
        else:
            existing.feature_template_ref = template.id
            existing.status = PromptStatus.PUBLISHED
            logger.info(f"seed_66_20_taxonomy: updated assembly {f}/{sf}/{p}")

    # 3. Aligner ExecutionProfiles
    # (feature, subfeature, plan, model)
    target_profiles = [
        ("chat", "astrologer", None, "gpt-4o"),
        ("guidance", None, None, "gpt-4o"),
        ("natal", None, None, "gpt-4o"),
    ]

    for f, sf, p, model in target_profiles:
        stmt_p = select(LlmExecutionProfileModel).where(
            LlmExecutionProfileModel.feature == f,
            LlmExecutionProfileModel.subfeature == sf,
            LlmExecutionProfileModel.plan == p,
        )
        profile = db.execute(stmt_p).scalar_one_or_none()

        if not profile:
            new_profile = LlmExecutionProfileModel(
                name=f"Profile {f} {sf or ''} {p or ''}".strip(),
                feature=f,
                subfeature=sf,
                plan=p,
                model=model,
                provider="openai",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="structured_json" if f in ["guidance", "natal"] else "free_text",
                timeout_seconds=60,
                status=PromptStatus.PUBLISHED,
                created_by="system",
            )
            db.add(new_profile)
            logger.info(f"seed_66_20_taxonomy: created profile {f}/{sf or ''}/{p or ''}")
        else:
            profile.model = model
            profile.status = PromptStatus.PUBLISHED
            logger.info(f"seed_66_20_taxonomy: updated profile {f}/{sf or ''}/{p or ''}")

    db.commit()


if __name__ == "__main__":
    from app.infra.db.session import SessionLocal

    with SessionLocal() as session:
        seed_66_20_taxonomy(session)
