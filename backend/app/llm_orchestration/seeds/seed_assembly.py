from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus

logger = logging.getLogger(__name__)


def seed_assembly(db: Session) -> None:
    """Seeds a first active assembly for natal_interpretation."""

    # 1. Find feature template (natal interpretation published)
    stmt = select(LlmPromptVersionModel).where(
        LlmPromptVersionModel.use_case_key == "natal_interpretation",
        LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
    )
    feature_template = db.execute(stmt).scalar_one_or_none()

    if not feature_template:
        logger.warning("seed_assembly_skipped: no published natal_interpretation template found")
        return

    # 2. Find a default persona
    stmt_persona = select(LlmPersonaModel).where(LlmPersonaModel.enabled)
    persona = db.execute(stmt_persona).scalars().first()

    # 3. Check if assembly already exists
    stmt_exists = select(PromptAssemblyConfigModel).where(
        PromptAssemblyConfigModel.feature == "natal",
        PromptAssemblyConfigModel.subfeature == "interpretation",
        PromptAssemblyConfigModel.plan.is_(None),
        PromptAssemblyConfigModel.locale == "fr-FR",
    )
    existing = db.execute(stmt_exists).scalar_one_or_none()

    if existing:
        logger.info("seed_assembly_skipped: assembly already exists")
        return

    # 4. Create first assembly
    new_assembly = PromptAssemblyConfigModel(
        feature="natal",
        subfeature="interpretation",
        plan=None,
        locale="fr-FR",
        feature_template_ref=feature_template.id,
        persona_ref=persona.id if persona else None,
        execution_config={
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_output_tokens": 4000,
            "timeout_seconds": 60,
        },
        status=PromptStatus.PUBLISHED,
        created_by="system",
    )
    db.add(new_assembly)
    db.commit()
    logger.info("seed_assembly_success: created natal:interpretation default assembly")
