# Commentaire global: ces tests prouvent la purge automatique persistante replay_snapshot_v1.
"""Tests d'integration de purge automatique replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.domain.audit.safe_details import ReplaySnapshotBulkPurgeAuditDetails
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _call_log(db: Session, request_id: str, now: datetime) -> LlmCallLogModel:
    """Cree un journal LLM minimal."""
    log = LlmCallLogModel(
        use_case="story-cs-296",
        model="gpt-test",
        latency_ms=1,
        tokens_in=1,
        tokens_out=1,
        cost_usd_estimated=0.0,
        validation_status="valid",
        request_id=request_id,
        trace_id=f"trace-{request_id}",
        input_hash=request_id[0] * 64,
        environment="test",
        expires_at=now + timedelta(days=90),
    )
    db.add(log)
    db.flush()
    return log


def _snapshot(
    db: Session,
    log: LlmCallLogModel,
    *,
    expires_at: datetime,
    snapshot_type: str = "replay_snapshot_v1",
) -> None:
    """Ajoute un snapshot replay rattache a un journal."""
    db.add(
        LlmReplaySnapshotModel(
            call_log_id=log.id,
            snapshot_type=snapshot_type,
            created_at=expires_at - timedelta(days=30),
            expires_at=expires_at,
            input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": log.input_hash},
            input_hash=log.input_hash,
            version_identity={},
            provenance={},
            redaction_state="encrypted_isolated_redacted_metadata_v1",
            input_enc=b"encrypted",
        )
    )


def test_purge_expired_deletes_only_expired_replay_snapshots() -> None:
    """Prouve le comptage, l'audit borne et la conservation hors replay_snapshot_v1."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        active_log = _call_log(db, "active", now)
        expired_log = _call_log(db, "expired", now)
        other_type_log = _call_log(db, "other-type", now)
        _snapshot(db, active_log, expires_at=now + timedelta(days=1))
        _snapshot(db, expired_log, expires_at=now - timedelta(seconds=1))
        _snapshot(
            db,
            other_type_log,
            expires_at=now - timedelta(seconds=1),
            snapshot_type="other_snapshot_type",
        )
        db.commit()

        result = ReplaySnapshotV1Service.purge_expired(
            db,
            now=now,
            request_id="automatic-purge-request",
            actor_role="system",
        )

        remaining_snapshots = db.execute(
            select(LlmReplaySnapshotModel.input_hash, LlmReplaySnapshotModel.snapshot_type)
        ).all()
        remaining_request_ids = db.execute(select(LlmCallLogModel.request_id)).scalars().all()
        event = db.execute(select(AuditEventModel)).scalar_one()
        assert result.status == "success"
        assert result.purged_count == 1
        assert isinstance(result.audit_details, ReplaySnapshotBulkPurgeAuditDetails)
        assert result.audit_details.purged_count == 1
        assert sorted(remaining_snapshots) == [
            (active_log.input_hash, "replay_snapshot_v1"),
            (other_type_log.input_hash, "other_snapshot_type"),
        ]
        assert sorted(remaining_request_ids) == ["active", "expired", "other-type"]
        assert event.action == "llm_replay_snapshots_expired_purged"
        assert event.details["snapshot_type"] == "replay_snapshot_v1"
        assert event.details["purged_count"] == 1
    finally:
        db.close()
