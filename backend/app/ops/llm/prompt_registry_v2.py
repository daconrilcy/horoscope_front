from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime
from threading import Lock
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models import LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

# Cache for active prompts (use_case_key -> (serialized_data, expiry))
_prompt_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
_cache_lock = Lock()


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class PromptRegistryV2:
    """
    Admin/history registry for published prompt versions.

    Scope is intentionally limited to admin mutation flows, rollback/history, and
    related startup maintenance. Runtime execution paths must use direct read-only
    lookups instead of depending on this registry abstraction.
    """

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
                "reasoning_effort": result.reasoning_effort,
                "verbosity": result.verbosity,
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
        Automatically inactivates the previously published version for the same use case.
        """
        # 1. Get the version to publish
        version = db.get(LlmPromptVersionModel, version_id)

        if not version:
            raise ValueError(f"Prompt version {version_id} not found")

        if version.status == PromptStatus.PUBLISHED:
            return version

        use_case_key = version.use_case_key

        # Story 66.28: Block resurrection of forbidden nominal features (AC5)
        from app.domain.llm.governance.feature_taxonomy import assert_nominal_feature_allowed

        assert_nominal_feature_allowed(use_case_key)

        # 2. Inactivate currently published version while preserving its history.
        db.execute(
            update(LlmPromptVersionModel)
            .where(
                LlmPromptVersionModel.use_case_key == use_case_key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
            .values(status=PromptStatus.INACTIVE)
        )

        # 3. Publish the new version
        version.status = PromptStatus.PUBLISHED
        version.published_at = utc_now()

        # Story 66.9 AC4: Validate use case naming on publish
        try:
            from app.domain.llm.prompting.validators import (
                validate_template_content,
                validate_use_case_naming,
            )

            # Try to get output_schema from UseCaseConfig if possible (Medium 2 fix)
            stmt_uc = select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key)
            db_uc = db.execute(stmt_uc).scalar_one_or_none()

            output_schema = None
            if db_uc and db_uc.output_schema_id:
                # We need LlmOutputSchemaModel
                from app.infra.db.models import LlmOutputSchemaModel

                schema_model = db.get(LlmOutputSchemaModel, uuid.UUID(db_uc.output_schema_id))
                if schema_model:
                    output_schema = schema_model.json_schema

            warnings = validate_use_case_naming(use_case_key, output_schema=output_schema)
            for w in warnings:
                logger.warning("prompt_registry_v2_naming_warning: %s", w)

            # Story 66.17 AC2: Template content guard
            arch_violations = validate_template_content(version.developer_prompt)
            for v in arch_violations:
                logger.warning(
                    "template_content_violation: %s detected in prompt template. Excerpt: %s",
                    v.violation_type,
                    v.excerpt,
                )
        except Exception as e:
            logger.debug("prompt_registry_v2_validation_skipped: %s", e)

        db.commit()
        db.refresh(version)

        # 4. Invalidate cache
        PromptRegistryV2.invalidate_cache(use_case_key)

        return version

    @staticmethod
    def rollback_prompt(
        db: Session,
        use_case_key: str,
        target_version_id: uuid.UUID | None = None,
    ) -> LlmPromptVersionModel:
        """
        Rollback to a specific historical version or the most recent inactive legacy version.
        """
        # Story 66.28: Block resurrection of forbidden nominal features (AC5)
        from app.domain.llm.governance.feature_taxonomy import assert_nominal_feature_allowed

        assert_nominal_feature_allowed(use_case_key)

        current_published = PromptRegistryV2.get_active_prompt(db, use_case_key)

        if target_version_id is not None:
            target_version = db.get(LlmPromptVersionModel, target_version_id)
            if not target_version or target_version.use_case_key != use_case_key:
                raise ValueError(
                    f"Prompt version {target_version_id} not found for use case {use_case_key}"
                )
            if current_published and target_version.id == current_published.id:
                return target_version
        else:
            stmt = (
                select(LlmPromptVersionModel)
                .where(
                    LlmPromptVersionModel.use_case_key == use_case_key,
                    LlmPromptVersionModel.status.in_(PromptStatus.inactive_values()),
                )
                .order_by(LlmPromptVersionModel.published_at.desc())
                .limit(1)
            )
            result = db.execute(stmt)
            target_version = result.scalar_one_or_none()
            if not target_version:
                raise ValueError(f"No inactive version found for use case {use_case_key}")

        if current_published:
            db.execute(
                update(LlmPromptVersionModel)
                .where(LlmPromptVersionModel.id == current_published.id)
                .values(status=PromptStatus.INACTIVE)
            )

        target_version.status = PromptStatus.PUBLISHED
        target_version.published_at = utc_now()

        db.commit()
        db.refresh(target_version)

        PromptRegistryV2.invalidate_cache(use_case_key)

        return target_version
