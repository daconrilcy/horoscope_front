# Commentaire global: ces tests verrouillent les etats de lecture metadata replay_snapshot_v1.
"""Tests unitaires des metadonnees controlees replay_snapshot_v1."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.services.replay_snapshot_v1_service import (
    REPLAY_SNAPSHOT_V1_PURGED_STATE,
    ReplaySnapshotV1Service,
)


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _snapshot(db: Session, *, expires_at: datetime, purged: bool = False) -> LlmReplaySnapshotModel:
    """Cree un snapshot replay minimal."""
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    log = LlmCallLogModel(
        use_case="story-cs-296",
        model="gpt-test",
        latency_ms=1,
        tokens_in=1,
        tokens_out=1,
        cost_usd_estimated=0.0,
        validation_status="valid",
        request_id=f"request-{uuid.uuid4().hex}",
        trace_id="trace-metadata-service",
        input_hash="b" * 64,
        environment="test",
        expires_at=now + timedelta(days=90),
    )
    db.add(log)
    db.flush()
    snapshot = LlmReplaySnapshotModel(
        call_log_id=log.id,
        snapshot_type="replay_snapshot_v1",
        created_at=now,
        expires_at=expires_at,
        input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "b" * 64},
        input_hash="b" * 64,
        version_identity={"model": "gpt-test"},
        provenance={"request_ref": log.request_id},
        redaction_state=(
            REPLAY_SNAPSHOT_V1_PURGED_STATE if purged else "encrypted_isolated_redacted_metadata_v1"
        ),
        input_enc=b"" if purged else b"encrypted",
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def test_get_snapshot_metadata_returns_success_for_active_snapshot() -> None:
    """Prouve que les metadonnees actives reviennent sans payload chiffre."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))

        result = ReplaySnapshotV1Service.get_snapshot_metadata(db, snapshot_id=snapshot.id, now=now)

        assert result.status == "success"
        assert result.metadata is not None
        assert result.metadata.snapshot_id == snapshot.id
        assert not hasattr(result.metadata, "input_enc")
    finally:
        db.close()


def test_get_snapshot_metadata_refuses_expired_and_purged_snapshots() -> None:
    """Prouve les etats `expired`, `already_purged` et `not_found`."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        expired = _snapshot(db, expires_at=now - timedelta(seconds=1))
        purged = _snapshot(db, expires_at=now + timedelta(days=1), purged=True)

        assert (
            ReplaySnapshotV1Service.get_snapshot_metadata(
                db, snapshot_id=expired.id, now=now
            ).status
            == "expired"
        )
        assert (
            ReplaySnapshotV1Service.get_snapshot_metadata(db, snapshot_id=purged.id, now=now).status
            == "already_purged"
        )
        assert (
            ReplaySnapshotV1Service.get_snapshot_metadata(
                db, snapshot_id=uuid.uuid4(), now=now
            ).status
            == "not_found"
        )
    finally:
        db.close()


def test_get_snapshot_metadata_ignores_non_v1_snapshot_rows() -> None:
    """Prouve que le service ne lit pas les lignes hors contrat replay_snapshot_v1."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))
        snapshot.snapshot_type = "other_snapshot_type"
        db.flush()

        result = ReplaySnapshotV1Service.get_snapshot_metadata(db, snapshot_id=snapshot.id, now=now)

        assert result.status == "not_found"
        assert result.metadata is None
    finally:
        db.close()


def test_get_replay_payload_snapshot_ignores_non_v1_snapshot_rows() -> None:
    """Prouve que la lecture par call_log ne reutilise pas un autre type de snapshot."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))
        snapshot.snapshot_type = "other_snapshot_type"
        db.flush()

        result = ReplaySnapshotV1Service.get_replay_payload_snapshot(
            db, call_log_id=snapshot.call_log_id, now=now
        )

        assert result.status == "not_found"
    finally:
        db.close()
