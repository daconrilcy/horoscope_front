# Commentaire global: ces tests prouvent que les audits replay_snapshot_v1 restent bornes.
"""Tests unitaires des details d'audit de purge replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.domain.audit.safe_details import ReplaySnapshotActivityAuditDetails, to_safe_details
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_replay_snapshot_purge_audit_details_are_bounded() -> None:
    """Prouve la forme safe_details dediee et l'ecriture AuditService."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        log = LlmCallLogModel(
            use_case="story-cs-296",
            model="gpt-test",
            latency_ms=1,
            tokens_in=1,
            tokens_out=1,
            cost_usd_estimated=0.0,
            validation_status="valid",
            request_id="request-audit-service",
            trace_id="trace-audit-service",
            input_hash="d" * 64,
            environment="test",
            expires_at=now + timedelta(days=90),
        )
        db.add(log)
        db.flush()
        snapshot = LlmReplaySnapshotModel(
            call_log_id=log.id,
            snapshot_type="replay_snapshot_v1",
            created_at=now,
            expires_at=now + timedelta(days=1),
            input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "d" * 64},
            input_hash="d" * 64,
            version_identity={},
            provenance={},
            redaction_state="encrypted_isolated_redacted_metadata_v1",
            input_enc=b"encrypted",
        )
        db.add(snapshot)
        db.flush()

        result = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=snapshot.id,
            request_id="audit-purge-request",
            actor_role="admin",
            now=now,
        )

        event = db.execute(select(AuditEventModel)).scalar_one()
        assert isinstance(result.audit_details, ReplaySnapshotActivityAuditDetails)
        assert set(to_safe_details(result.audit_details)) == {
            "action",
            "snapshot_id",
            "request_id",
            "status",
        }
        assert event.action == "replay_snapshot_v1.purge"
        assert event.target_id == str(snapshot.id)
        assert "encrypted" not in str(event.details)
        assert "payload" not in str(event.details)
    finally:
        db.close()
