from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import LlmPromptVersionModel
from app.infra.db.repositories.llm.prompting_repository import (
    get_active_prompt_version as repo_get_active_prompt_version,
)


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

    return repo_get_active_prompt_version(db, use_case_key)
