from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.models.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
)
from app.infra.db.models.llm_sample_payload import LlmSamplePayloadModel


def get_active_prompt_version(db: Session, use_case_key: str) -> LlmPromptVersionModel | None:
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


def list_prompt_versions(db: Session, use_case_key: str) -> list[LlmPromptVersionModel]:
    stmt = (
        select(LlmPromptVersionModel)
        .where(LlmPromptVersionModel.use_case_key == use_case_key)
        .order_by(LlmPromptVersionModel.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_latest_prompt_version(db: Session, use_case_key: str) -> LlmPromptVersionModel | None:
    stmt = (
        select(LlmPromptVersionModel)
        .where(LlmPromptVersionModel.use_case_key == use_case_key)
        .order_by(LlmPromptVersionModel.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_use_case_configs(db: Session) -> list[LlmUseCaseConfigModel]:
    return list(db.execute(select(LlmUseCaseConfigModel)).scalars().all())


def get_latest_active_release_snapshot(db: Session) -> LlmReleaseSnapshotModel | None:
    latest_active = db.execute(
        select(LlmActiveReleaseModel).order_by(desc(LlmActiveReleaseModel.activated_at)).limit(1)
    ).scalar_one_or_none()
    if latest_active is None:
        return None
    return db.get(LlmReleaseSnapshotModel, latest_active.release_snapshot_id)


def list_release_snapshots_timeline(db: Session) -> list[LlmReleaseSnapshotModel]:
    stmt = select(LlmReleaseSnapshotModel).order_by(
        desc(LlmReleaseSnapshotModel.activated_at),
        desc(LlmReleaseSnapshotModel.created_at),
    )
    return list(db.execute(stmt).scalars().all())


def get_release_snapshot(db: Session, snapshot_id: str | object) -> LlmReleaseSnapshotModel | None:
    return db.get(LlmReleaseSnapshotModel, snapshot_id)


def get_use_case_config(db: Session, use_case_key: str) -> LlmUseCaseConfigModel | None:
    return db.get(LlmUseCaseConfigModel, use_case_key)


def get_sample_payload(
    db: Session, sample_payload_id: str | object
) -> LlmSamplePayloadModel | None:
    return db.get(LlmSamplePayloadModel, sample_payload_id)
