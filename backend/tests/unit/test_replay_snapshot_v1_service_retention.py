# Commentaire global: ces tests verrouillent la retention portee par le service replay_snapshot_v1.
"""Tests unitaires de retention du service replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _call_log(db: Session, now: datetime) -> LlmCallLogModel:
    """Cree un journal LLM minimal pour rattacher un snapshot."""
    log = LlmCallLogModel(
        use_case="story-cs-296",
        model="gpt-test",
        latency_ms=1,
        tokens_in=1,
        tokens_out=1,
        cost_usd_estimated=0.0,
        validation_status="valid",
        request_id="request-retention-service",
        trace_id="trace-retention-service",
        input_hash="a" * 64,
        environment="test",
        expires_at=now + timedelta(days=90),
    )
    db.add(log)
    db.flush()
    return log


def test_create_snapshot_applies_exact_thirty_day_retention() -> None:
    """Prouve que le service derive `expires_at` depuis `created_at + 30 jours`."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        log = _call_log(db, now)

        result = ReplaySnapshotV1Service.create_snapshot(
            db,
            call_log_id=log.id,
            user_input={"message": "bonjour"},
            request_id=log.request_id,
            trace_id=log.trace_id,
            use_case=log.use_case,
            result=None,
            created_at=now,
        )

        snapshot = db.execute(select(LlmReplaySnapshotModel)).scalar_one()
        assert result.status == "success"
        assert result.metadata is not None
        assert snapshot.created_at.replace(tzinfo=UTC) == now
        assert snapshot.expires_at.replace(tzinfo=UTC) == now + timedelta(days=30)
        assert result.metadata.expires_at.replace(tzinfo=UTC) == now + timedelta(days=30)
    finally:
        db.close()
