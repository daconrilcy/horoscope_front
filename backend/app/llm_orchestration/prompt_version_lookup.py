from __future__ import annotations

import uuid

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus


def get_active_prompt_version(
    db: Session, use_case_key: str, *, override_prompt_version_id: str | None = None
) -> LlmPromptVersionModel | None:
    """
    Runtime-safe lookup for a published prompt version.

    This helper is intentionally read-only and avoids PromptRegistryV2 so nominal
    runtime paths do not depend on the admin/history registry abstraction.
    """
    if override_prompt_version_id:
        try:
            return db.get(LlmPromptVersionModel, uuid.UUID(override_prompt_version_id))
        except (ValueError, TypeError):
            return None

    stmt = (
        select(LlmPromptVersionModel)
        .where(
            LlmPromptVersionModel.use_case_key == use_case_key,
            LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
        )
        .order_by(
            desc(LlmPromptVersionModel.published_at),
            desc(LlmPromptVersionModel.created_at),
        )
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()
