# Commentaire global: ces tests garantissent une purge replay limitee aux snapshots expires.
"""Tests de purge pour replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.domain.llm.runtime.observability_service import purge_expired_logs
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmReplaySnapshotModel,
)


class _FrozenClock:
    """Horloge de test deterministe pour la purge."""

    def __init__(self, value: datetime) -> None:
        self._value = value

    def utcnow(self) -> datetime:
        """Retourne toujours la date de reference du test."""
        return self._value


@pytest.fixture
def db() -> Session:
    """Ouvre une base SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _call_log(request_id: str, expires_at: datetime) -> LlmCallLogModel:
    """Cree un journal LLM minimal pour rattacher un snapshot."""
    return LlmCallLogModel(
        use_case="story-cs-295",
        model="gpt-test",
        latency_ms=1,
        tokens_in=1,
        tokens_out=1,
        cost_usd_estimated=0.0,
        validation_status="valid",
        request_id=request_id,
        trace_id=f"trace-{request_id}",
        input_hash="c" * 64,
        environment="test",
        expires_at=expires_at,
    )


@pytest.mark.asyncio
async def test_purge_deletes_expired_snapshot_without_deleting_active_log(db: Session) -> None:
    """Prouve que la purge retire le snapshot expire sans cascade hors scope."""
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    active_log = _call_log("active-log", now + timedelta(days=10))
    expired_snapshot_log = _call_log("expired-snapshot-log", now + timedelta(days=10))
    db.add_all([active_log, expired_snapshot_log])
    db.flush()
    db.add_all(
        [
            LlmReplaySnapshotModel(
                call_log_id=active_log.id,
                snapshot_type="replay_snapshot_v1",
                created_at=now,
                expires_at=now + timedelta(days=1),
                input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "c" * 64},
                input_hash="c" * 64,
                version_identity={},
                provenance={},
                redaction_state="encrypted_isolated_redacted_metadata_v1",
                input_enc=b"active",
            ),
            LlmReplaySnapshotModel(
                call_log_id=expired_snapshot_log.id,
                snapshot_type="replay_snapshot_v1",
                created_at=now - timedelta(days=31),
                expires_at=now - timedelta(days=1),
                input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "d" * 64},
                input_hash="d" * 64,
                version_identity={},
                provenance={},
                redaction_state="encrypted_isolated_redacted_metadata_v1",
                input_enc=b"expired",
            ),
        ]
    )
    db.commit()

    with patch("app.domain.llm.runtime.observability_service.datetime_provider", _FrozenClock(now)):
        deleted_count = await purge_expired_logs(db)

    remaining_logs = db.execute(select(LlmCallLogModel.request_id)).scalars().all()
    remaining_snapshots = db.execute(select(LlmReplaySnapshotModel.input_hash)).scalars().all()

    assert deleted_count == 1
    assert sorted(remaining_logs) == ["active-log", "expired-snapshot-log"]
    assert remaining_snapshots == ["c" * 64]
