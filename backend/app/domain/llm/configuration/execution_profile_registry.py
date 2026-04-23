from __future__ import annotations

import logging
import uuid
from threading import Lock
from typing import Any, Optional

from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select
from sqlalchemy.orm import Session, object_session

from app.domain.llm.governance.feature_taxonomy import (
    assert_nominal_feature_allowed,
    normalize_feature,
    normalize_subfeature,
)
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_prompt import PromptStatus
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel
from app.infra.db.utils import reconstruct_orm

logger = logging.getLogger(__name__)

# In-memory cache: map resolution key -> published profile id.
# Never store ORM instances here: they are bound to the Session that loaded them
# and will break subsequent requests (DetachedInstanceError / refresh on wrong session).
_profile_cache: dict[str, uuid.UUID] = {}
_cache_lock = Lock()


def _profile_reload_stmt(profile_id: uuid.UUID):
    return select(LlmExecutionProfileModel).where(
        LlmExecutionProfileModel.id == profile_id,
        LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
    )


def _load_cached_profile(db: Session, cache_key: str) -> Optional[LlmExecutionProfileModel]:
    with _cache_lock:
        profile_id = _profile_cache.get(cache_key)
    if profile_id is None:
        return None
    profile = db.execute(_profile_reload_stmt(profile_id)).scalar_one_or_none()
    if profile is None:
        with _cache_lock:
            _profile_cache.pop(cache_key, None)
    return profile


def _should_cache_profile_row(profile: LlmExecutionProfileModel, db: Session) -> bool:
    try:
        state = sa_inspect(profile)
        return bool(state.persistent and object_session(profile) is db)
    except Exception:
        return False


class ExecutionProfileRegistry:
    """
    Registry for LLM execution profiles with waterfall resolution (Story 66.11 D2).
    """

    @staticmethod
    def _get_active_release_snapshot(db: Session) -> Optional[LlmReleaseSnapshotModel]:
        """Fetch the currently active release snapshot."""
        from sqlalchemy import desc

        from app.infra.db.models.llm.llm_release import (
            LlmActiveReleaseModel,
            LlmReleaseSnapshotModel,
        )

        stmt = (
            select(LlmReleaseSnapshotModel)
            .join(LlmActiveReleaseModel)
            .order_by(desc(LlmActiveReleaseModel.activated_at))
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_active_profile(
        db: Session,
        feature: str,
        subfeature: Optional[str] = None,
        plan: Optional[str] = None,
        locale: str = "fr-FR",
    ) -> Optional[LlmExecutionProfileModel]:
        """
        Resolves the active execution profile using waterfall.
        AC10: Use the active snapshot manifest if available.
        """
        # Story 66.23: Hardened taxonomy resolution
        assert_nominal_feature_allowed(feature)

        feature = normalize_feature(feature)
        subfeature = normalize_subfeature(feature, subfeature)

        # Story 66.32 AC10, AC14: Resolve active snapshot first
        snapshot = ExecutionProfileRegistry._get_active_release_snapshot(db)
        snapshot_id = str(snapshot.id) if snapshot else "none"

        cache_key = f"{snapshot_id}:{feature}:{subfeature}:{plan}:{locale}"

        cached_profile = _load_cached_profile(db, cache_key)
        if cached_profile is not None:
            return cached_profile

        resolved_profile = None

        if snapshot:
            # AC10: Resolve from snapshot manifest
            manifest = snapshot.manifest
            targets = manifest.get("targets", {})

            # Waterfall resolution within snapshot
            # Note: Profiles in snapshot are bundled with assemblies.
            search_patterns = [
                f"{feature}:{subfeature}:{plan}:{locale}",
                f"{feature}:{subfeature}:None:{locale}",
                f"{feature}:None:None:{locale}",
            ]

            for key in search_patterns:
                bundle = targets.get(key)
                if bundle and "profile" in bundle:
                    data = bundle["profile"]
                    resolved_profile = reconstruct_orm(LlmExecutionProfileModel, data)
                    break
        else:
            # Legacy resolution from tables
            candidates = [
                (feature, subfeature, plan),
                (feature, subfeature, None) if subfeature else None,
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
                    resolved_profile = profile
                    break

        if resolved_profile and _should_cache_profile_row(resolved_profile, db):
            with _cache_lock:
                _profile_cache[cache_key] = resolved_profile.id

        return resolved_profile

    @staticmethod
    def get_profile_by_id(
        db: Session, profile_id: uuid.UUID, assembly: Optional[Any] = None
    ) -> Optional[LlmExecutionProfileModel]:
        """
        Direct resolution by ID.
        Story 66.32: Support transitive resolution from assembly bundle.
        """
        if assembly and hasattr(assembly, "_snapshot_bundle"):
            bundle = getattr(assembly, "_snapshot_bundle")
            if bundle and "profile" in bundle:
                data = bundle["profile"]
                if data.get("id") == str(profile_id):
                    return reconstruct_orm(LlmExecutionProfileModel, data)

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
