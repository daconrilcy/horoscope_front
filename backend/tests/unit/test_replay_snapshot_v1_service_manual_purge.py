# Commentaire global: ces tests verrouillent les resultats metier de purge manuelle replay.
"""Tests unitaires de purge manuelle replay_snapshot_v1."""

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


def _snapshot(db: Session, *, expires_at: datetime) -> LlmReplaySnapshotModel:
    """Cree un snapshot replay minimal pour la purge."""
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
        trace_id="trace-manual-purge",
        input_hash="c" * 64,
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
        input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "c" * 64},
        input_hash="c" * 64,
        version_identity={},
        provenance={},
        redaction_state="encrypted_isolated_redacted_metadata_v1",
        input_enc=b"encrypted",
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def test_purge_snapshot_returns_success_then_already_purged() -> None:
    """Prouve la purge par tombstone et l'etat stable `already_purged`."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))

        first = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=snapshot.id,
            request_id="manual-purge-success",
            now=now,
            audit=False,
        )
        second = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=snapshot.id,
            request_id="manual-purge-repeat",
            now=now,
            audit=False,
        )

        assert first.status == "success"
        assert first.purged_count == 1
        assert second.status == "already_purged"
        assert second.purged_count == 0
        assert snapshot.redaction_state == REPLAY_SNAPSHOT_V1_PURGED_STATE
        assert snapshot.input_enc == b""
        assert snapshot.input_ref["kind"] == "replay_snapshot_payload_tombstone"
    finally:
        db.close()


def test_purge_snapshot_returns_expired_and_not_found_states() -> None:
    """Prouve les resultats `expired` et `not_found` sans logique de route."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        expired = _snapshot(db, expires_at=now - timedelta(seconds=1))

        expired_result = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=expired.id,
            request_id="manual-purge-expired",
            now=now,
            audit=False,
        )
        missing_result = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=uuid.uuid4(),
            request_id="manual-purge-missing",
            now=now,
            audit=False,
        )

        assert expired_result.status == "expired"
        assert expired_result.purged_count == 1
        assert missing_result.status == "not_found"
    finally:
        db.close()


def test_purge_snapshot_ignores_non_v1_snapshot_rows() -> None:
    """Prouve que la purge manuelle ne tombstone pas les lignes hors replay_snapshot_v1."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))
        snapshot.snapshot_type = "other_snapshot_type"
        db.flush()

        result = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=snapshot.id,
            request_id="manual-purge-other-type",
            now=now,
            audit=False,
        )

        assert result.status == "not_found"
        assert snapshot.redaction_state == "encrypted_isolated_redacted_metadata_v1"
        assert snapshot.input_enc == b"encrypted"
    finally:
        db.close()
