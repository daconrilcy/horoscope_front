from __future__ import annotations

import logging
import uuid
from threading import Lock
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_prompt import PromptStatus

logger = logging.getLogger(__name__)

# Simple in-memory cache for published profiles
_profile_cache: dict[str, LlmExecutionProfileModel] = {}
_cache_lock = Lock()


class ExecutionProfileRegistry:
    """
    Registry for LLM execution profiles with waterfall resolution (Story 66.11 D2).
    """

    @staticmethod
    def get_active_profile(
        db: Session, feature: str, subfeature: Optional[str] = None, plan: Optional[str] = None
    ) -> Optional[LlmExecutionProfileModel]:
        """
        Resolves the active execution profile using waterfall:
        feature + subfeature + plan -> feature + subfeature -> feature
        """
        cache_key = f"{feature}:{subfeature}:{plan}"

        with _cache_lock:
            if cache_key in _profile_cache:
                return _profile_cache[cache_key]

        # Waterfall steps
        candidates = [
            # 1. Full match
            (feature, subfeature, plan),
            # 2. Feature + Subfeature
            (feature, subfeature, None) if subfeature else None,
            # 3. Feature only
            (feature, None, None),
        ]

        for candidate in candidates:
            if candidate is None:
                continue

            f, sf, p = candidate
            stmt = select(LlmExecutionProfileModel).where(
                LlmExecutionProfileModel.feature == f,
                LlmExecutionProfileModel.subfeature == sf,
                LlmExecutionProfileModel.plan == p,
                LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
            )
            profile = db.execute(stmt).scalar_one_or_none()
            if profile:
                with _cache_lock:
                    _profile_cache[cache_key] = profile
                return profile

        return None

    @staticmethod
    def get_profile_by_id(db: Session, profile_id: uuid.UUID) -> Optional[LlmExecutionProfileModel]:
        """Direct resolution by ID (used for assembly_ref)."""
        stmt = select(LlmExecutionProfileModel).where(
            LlmExecutionProfileModel.id == profile_id,
            LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def invalidate_cache() -> None:
        """Clear the registry cache."""
        with _cache_lock:
            _profile_cache.clear()
            logger.debug("execution_profile_registry_cache_invalidated")
