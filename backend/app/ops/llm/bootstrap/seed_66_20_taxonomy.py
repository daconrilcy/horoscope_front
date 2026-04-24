from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_use_case_contract,
)
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, PromptStatus

logger = logging.getLogger(__name__)

def _resolve_output_schema_id(db: Session, schema_name: str | None) -> str | None:
    if not schema_name:
        return None
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == schema_name)
    schema = db.execute(stmt).scalar_one_or_none()
    return str(schema.id) if schema else None


def seed_66_20_taxonomy(db: Session) -> None:
    """Finalize canonical taxonomy for chat, guidance and natal (Story 66.20)."""

    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.enabled)
    persona = db.execute(stmt_persona).scalars().first()
    if not persona:
        logger.warning("seed_66_20_taxonomy: no enabled persona found")
        return
    persona_id = persona.id

    target_assemblies = [
        ("chat", "astrologer", "free", "chat_astrologer"),
        ("chat", "astrologer", "premium", "chat_astrologer"),
        ("guidance", "daily", "free", "guidance_daily"),
        ("guidance", "daily", "premium", "guidance_daily"),
        ("guidance", "weekly", "free", "guidance_weekly"),
        ("guidance", "weekly", "premium", "guidance_weekly"),
        ("guidance", "contextual", "free", "guidance_contextual"),
        ("guidance", "contextual", "premium", "guidance_contextual"),
        ("guidance", "event", "free", "event_guidance"),
        ("guidance", "event", "premium", "event_guidance"),
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

    for feature, subfeature, plan, template_key in target_assemblies:
        stmt_template = (
            select(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == template_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            .order_by(LlmPromptVersionModel.created_at.desc())
        )
        template = db.execute(stmt_template).scalars().first()
        if not template:
            logger.warning(
                "seed_66_20_taxonomy: template %s not found for %s/%s",
                template_key,
                feature,
                subfeature,
            )
            continue

        contract = get_canonical_use_case_contract(template_key)
        stmt_existing = select(PromptAssemblyConfigModel).where(
            PromptAssemblyConfigModel.feature == feature,
            PromptAssemblyConfigModel.subfeature == subfeature,
            PromptAssemblyConfigModel.plan == plan,
            PromptAssemblyConfigModel.locale == "fr-FR",
        )
        existing = db.execute(stmt_existing).scalar_one_or_none()

        if not existing:
            profile_stmt = (
                select(LlmExecutionProfileModel)
                .where(
                    LlmExecutionProfileModel.feature == feature,
                    LlmExecutionProfileModel.subfeature == subfeature,
                    LlmExecutionProfileModel.plan == plan,
                    LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
                )
                .order_by(LlmExecutionProfileModel.created_at.desc())
            )
            profile = db.execute(profile_stmt).scalars().first()
            existing = PromptAssemblyConfigModel(
                feature=feature,
                subfeature=subfeature,
                plan=plan,
                locale="fr-FR",
                feature_template_ref=template.id,
                persona_ref=persona_id,
                execution_profile_ref=profile.id if profile else None,
                output_schema_id=_resolve_output_schema_id(
                    db,
                    contract.output_schema_name if contract else None,
                ),
                status=PromptStatus.PUBLISHED,
                created_by="system",
            )
            db.add(existing)
            logger.info("seed_66_20_taxonomy: created assembly %s/%s/%s", feature, subfeature, plan)
        else:
            existing.feature_template_ref = template.id
            existing.output_schema_id = _resolve_output_schema_id(
                db,
                contract.output_schema_name if contract else None,
            )
            existing.status = PromptStatus.PUBLISHED
            logger.info("seed_66_20_taxonomy: updated assembly %s/%s/%s", feature, subfeature, plan)

    target_profiles = [
        ("chat", "astrologer", None, "gpt-4o"),
        ("guidance", None, None, "gpt-4o"),
        ("natal", None, None, "gpt-4o"),
    ]

    for feature, subfeature, plan, model in target_profiles:
        stmt_profile = select(LlmExecutionProfileModel).where(
            LlmExecutionProfileModel.feature == feature,
            LlmExecutionProfileModel.subfeature == subfeature,
            LlmExecutionProfileModel.plan == plan,
        )
        profile = db.execute(stmt_profile).scalar_one_or_none()

        if not profile:
            profile = LlmExecutionProfileModel(
                name=f"Profile {feature} {subfeature or ''} {plan or ''}".strip(),
                feature=feature,
                subfeature=subfeature,
                plan=plan,
                model=model,
                provider="openai",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="structured_json" if feature in ["guidance", "natal"] else "free_text",
                timeout_seconds=60,
                status=PromptStatus.PUBLISHED,
                created_by="system",
            )
            db.add(profile)
            logger.info(
                "seed_66_20_taxonomy: created profile %s/%s/%s",
                feature,
                subfeature or "",
                plan or "",
            )
        else:
            profile.model = model
            profile.status = PromptStatus.PUBLISHED
            logger.info(
                "seed_66_20_taxonomy: updated profile %s/%s/%s",
                feature,
                subfeature or "",
                plan or "",
            )

    for feature, subfeature, plan, _template_key in target_assemblies:
        profile_stmt = (
            select(LlmExecutionProfileModel)
            .where(
                LlmExecutionProfileModel.feature == feature,
                LlmExecutionProfileModel.subfeature == subfeature,
                LlmExecutionProfileModel.plan == plan,
            )
            .order_by(LlmExecutionProfileModel.created_at.desc())
        )
        profile = db.execute(profile_stmt).scalars().first()
        if profile is None:
            continue

        assembly_stmt = select(PromptAssemblyConfigModel).where(
            PromptAssemblyConfigModel.feature == feature,
            PromptAssemblyConfigModel.subfeature == subfeature,
            PromptAssemblyConfigModel.plan == plan,
            PromptAssemblyConfigModel.locale == "fr-FR",
        )
        assembly = db.execute(assembly_stmt).scalar_one_or_none()
        if assembly is not None:
            assembly.execution_profile_ref = profile.id

    db.commit()


if __name__ == "__main__":
    from app.infra.db.session import SessionLocal

    with SessionLocal() as session:
        seed_66_20_taxonomy(session)
