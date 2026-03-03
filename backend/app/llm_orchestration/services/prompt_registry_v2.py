from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

# Cache for active prompts (use_case_key -> (serialized_data, expiry))
_prompt_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_cache_lock = Lock()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromptRegistryV2:
    @staticmethod
    def get_active_prompt(db: Session, use_case_key: str) -> Optional[LlmPromptVersionModel]:
        """
        Get the currently published prompt for a use case.
        Includes an in-memory TTL cache (60s).
        """
        now = time.time()
        with _cache_lock:
            if use_case_key in _prompt_cache:
                data, expiry = _prompt_cache[use_case_key]
                if now < expiry:
                    increment_counter("prompt_registry_cache_hits_total", labels={"status": "hit"})
                    # Return a detached model instance for gateway usage
                    # Note: this instance is not attached to the DB session
                    return LlmPromptVersionModel(**data)

        increment_counter("prompt_registry_cache_hits_total", labels={"status": "miss"})
        stmt = (
            select(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == use_case_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            .limit(1)
        )
        result = db.execute(stmt).scalar_one_or_none()

        if result:
            # Serialise key fields to avoid session issues in cache
            data = {
                "id": result.id,
                "use_case_key": result.use_case_key,
                "model": result.model,
                "temperature": result.temperature,
                "max_output_tokens": result.max_output_tokens,
                "developer_prompt": result.developer_prompt,
                "fallback_use_case_key": result.fallback_use_case_key,
                "status": result.status,
                "created_by": result.created_by,
                "created_at": result.created_at,
                "published_at": result.published_at,
            }
            with _cache_lock:
                _prompt_cache[use_case_key] = (data, now + 60)

        return result

    @staticmethod
    def invalidate_cache(use_case_key: str) -> None:
        """Invalidate the cache for a specific use case."""
        with _cache_lock:
            _prompt_cache.pop(use_case_key, None)

    @staticmethod
    def publish_prompt(db: Session, version_id: uuid.UUID) -> LlmPromptVersionModel:
        """
        Publish a prompt version.
        Automatically archives the previously published version for the same use case.
        """
        # 1. Get the version to publish
        version = db.get(LlmPromptVersionModel, version_id)

        if not version:
            raise ValueError(f"Prompt version {version_id} not found")

        if version.status == PromptStatus.PUBLISHED:
            return version

        use_case_key = version.use_case_key

        # 2. Archive currently published version
        db.execute(
            update(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == use_case_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            .values(status=PromptStatus.ARCHIVED)
        )

        # 3. Publish the new version
        version.status = PromptStatus.PUBLISHED
        version.published_at = utc_now()

        db.commit()
        db.refresh(version)

        # 4. Invalidate cache
        PromptRegistryV2.invalidate_cache(use_case_key)

        return version

    @staticmethod
    def rollback_prompt(db: Session, use_case_key: str) -> LlmPromptVersionModel:
        """
        Rollback to the most recent archived version.
        """
        # 1. Find the current published version
        current_published = PromptRegistryV2.get_active_prompt(db, use_case_key)

        # 2. Find the most recent archived version
        stmt = (
            select(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == use_case_key,
                LlmPromptVersionModel.status == PromptStatus.ARCHIVED,
            )
            .order_by(LlmPromptVersionModel.published_at.desc())
            .limit(1)
        )
        result = db.execute(stmt)
        last_archived = result.scalar_one_or_none()

        if not last_archived:
            raise ValueError(f"No archived version found for use case {use_case_key}")

        # 3. Archive current
        if current_published:
            # If it was from cache, we might need to get it from DB to update it
            # But here we just want to change status.
            # If it's a detached instance, we should merge it or just use an update stmt.
            db.execute(
                update(LlmPromptVersionModel)
                .where(LlmPromptVersionModel.id == current_published.id)
                .values(status=PromptStatus.ARCHIVED)
            )

        # 4. Re-publish last archived
        last_archived.status = PromptStatus.PUBLISHED
        last_archived.published_at = utc_now()

        db.commit()
        db.refresh(last_archived)

        # 5. Invalidate cache
        PromptRegistryV2.invalidate_cache(use_case_key)

        return last_archived
