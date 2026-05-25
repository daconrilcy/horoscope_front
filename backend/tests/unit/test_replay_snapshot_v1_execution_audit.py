# Commentaire global: ces tests prouvent l'audit d'execution replay_snapshot_v1 sans fuite.
"""Tests unitaires CS-298 pour les audits de lecture, replay et purge."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.domain.llm.runtime.contracts import GatewayError, GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.observability_service import log_call
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.ops.llm.replay_service import replay
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service

FORBIDDEN_AUDIT_FIELDS = {
    "raw_prompt",
    "birth_date",
    "birth_time",
    "birth_place",
    "latitude",
    "longitude",
    "email",
    "password",
    "api_key",
    "payload_enc",
}


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _snapshot(
    db: Session,
    *,
    expires_at: datetime,
    input_enc: bytes = b"encrypted",
    redaction_state: str = "encrypted_isolated_redacted_metadata_v1",
    input_ref: dict[str, Any] | None = None,
) -> LlmReplaySnapshotModel:
    """Cree un snapshot v1 minimal pour les audits d'execution."""
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    log = LlmCallLogModel(
        use_case="story-cs-298",
        model="gpt-test",
        latency_ms=1,
        tokens_in=1,
        tokens_out=1,
        cost_usd_estimated=0.0,
        validation_status="valid",
        request_id=f"request-{uuid.uuid4().hex}",
        trace_id="trace-execution-audit",
        input_hash="e" * 64,
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
        input_ref=input_ref or {"kind": "encrypted_isolated_payload_ref", "input_hash": "e" * 64},
        input_hash="e" * 64,
        version_identity={"model": "gpt-test", "prompt_version_id": "prompt-v1"},
        provenance={"request_ref": log.request_id},
        redaction_state=redaction_state,
        input_enc=input_enc,
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def _single_event(db: Session) -> AuditEventModel:
    """Retourne l'unique evenement d'audit produit par le scenario."""
    return db.execute(select(AuditEventModel)).scalar_one()


def _assert_safe_details(details: dict[str, object]) -> None:
    """Verifie que les details d'audit restent dans le contrat borne."""
    assert set(details) <= {
        "action",
        "status",
        "snapshot_id",
        "request_id",
        "reason",
        "diff_summary",
    }
    assert FORBIDDEN_AUDIT_FIELDS.isdisjoint(details)
    serialized = str(details)
    assert all(field not in serialized for field in FORBIDDEN_AUDIT_FIELDS)


def test_metadata_read_is_audited_with_bounded_details() -> None:
    """Prouve l'audit de lecture metadata sans exposer les champs sensibles."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(db, expires_at=now + timedelta(days=1))

        result = ReplaySnapshotV1Service.get_snapshot_metadata(
            db,
            snapshot_id=snapshot.id,
            now=now,
            request_id="req-metadata-unit",
            actor_role="admin",
            audit=True,
        )

        event = _single_event(db)
        assert result.status == "success"
        assert result.audit_event_id == event.id
        assert event.action == "replay_snapshot_v1.metadata_read"
        assert event.status == "success"
        assert event.details["request_id"] == "req-metadata-unit"
        _assert_safe_details(event.details)
    finally:
        db.close()


def test_replay_attempt_success_and_failure_are_audited() -> None:
    """Prouve les audits de tentative de replay succes et refus."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        active = _snapshot(db, expires_at=now + timedelta(days=1))
        expired = _snapshot(db, expires_at=now - timedelta(seconds=1))

        accepted = ReplaySnapshotV1Service.start_replay_attempt(
            db,
            snapshot_id=active.id,
            request_id="req-replay-success",
            actor_role="admin",
            now=now,
        )
        refused = ReplaySnapshotV1Service.start_replay_attempt(
            db,
            snapshot_id=expired.id,
            request_id="req-replay-expired",
            actor_role="admin",
            now=now,
        )

        events = db.execute(select(AuditEventModel).order_by(AuditEventModel.id)).scalars().all()
        assert accepted.status == "success"
        assert accepted.replay_attempt_id
        assert refused.status == "expired"
        assert [event.action for event in events] == [
            "replay_snapshot_v1.replay_attempt",
            "replay_snapshot_v1.replay_attempt",
        ]
        assert [event.status for event in events] == ["success", "failed"]
        assert events[1].details["reason"] == "expired"
        for event in events:
            _assert_safe_details(event.details)
    finally:
        db.close()


def test_purge_failure_is_audited_without_sensitive_details() -> None:
    """Prouve qu'une purge refusee produit un audit borne."""
    db = _db_session()
    try:
        missing_id = uuid.uuid4()

        result = ReplaySnapshotV1Service.purge_snapshot(
            db,
            snapshot_id=missing_id,
            request_id="req-purge-missing",
            actor_role="admin",
        )

        event = _single_event(db)
        assert result.status == "not_found"
        assert event.action == "replay_snapshot_v1.purge"
        assert event.status == "failed"
        assert event.details["reason"] == "not_found"
        _assert_safe_details(event.details)
    finally:
        db.close()


def test_incomplete_snapshot_is_refused_before_replay_payload_use() -> None:
    """Prouve le refus d'un snapshot incomplet avant toute execution provider."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        snapshot = _snapshot(
            db,
            expires_at=now + timedelta(days=1),
            input_enc=b"",
            redaction_state="partial_write_detected",
        )

        result = ReplaySnapshotV1Service.get_replay_payload_snapshot(
            db,
            call_log_id=snapshot.call_log_id,
            now=now,
        )

        assert result.status == "incomplete"
        assert result.metadata is None
    finally:
        db.close()


class _SuccessfulGateway:
    """Double de gateway qui prouve l'execution sans appeler de provider externe."""

    async def execute(self, **kwargs: Any) -> GatewayResult:
        """Retourne un resultat borne representatif d'un replay execute."""
        return GatewayResult(
            use_case=kwargs["use_case"],
            request_id=kwargs["request_id"],
            trace_id=kwargs["trace_id"],
            raw_output="provider text hidden by replay result",
            structured_output={"hidden": "provider"},
            usage=UsageInfo(input_tokens=3, output_tokens=5, total_tokens=8),
            meta=GatewayMeta(latency_ms=12, prompt_version_id="prompt-v2", model="gpt-test"),
        )


class _FailingGateway:
    """Double de gateway qui simule une erreur provider apres validation snapshot."""

    async def execute(self, **_kwargs: Any) -> GatewayResult:
        """Leve une erreur apres que le snapshot a ete valide."""
        raise GatewayError("provider unavailable")


async def _replay_ready_snapshot(db: Session, *, request_id: str) -> LlmReplaySnapshotModel:
    """Cree le snapshot par le chemin applicatif log_call -> create_snapshot."""
    await log_call(
        db,
        "story-cs-300",
        request_id,
        "trace-replay-execution",
        {"question": "safe replay input"},
        result=None,
    )
    return db.execute(select(LlmReplaySnapshotModel)).scalar_one()


@pytest.mark.asyncio
async def test_real_replay_execution_success_is_audited(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prouve que le chemin de replay reel audite le succes sans payload provider."""
    db = _db_session()
    try:
        snapshot = await _replay_ready_snapshot(db, request_id="req-real-replay-success")
        monkeypatch.setattr("app.domain.llm.runtime.gateway.LLMGateway", _SuccessfulGateway)

        result = await replay(db, "req-real-replay-success", "prompt-v2")

        event = _single_event(db)
        assert result.raw_output is None
        assert result.structured_output is None
        assert event.action == "replay_snapshot_v1.replay_attempt"
        assert event.status == "success"
        assert event.target_id == str(snapshot.id)
        assert event.details["diff_summary"] == result.diff_vs_original
        _assert_safe_details(event.details)
        assert "provider text hidden" not in str(event.details)
    finally:
        db.close()


@pytest.mark.asyncio
async def test_real_replay_execution_failure_is_audited(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prouve que l'erreur provider du replay reel produit un audit failed."""
    db = _db_session()
    try:
        snapshot = await _replay_ready_snapshot(db, request_id="req-real-replay-failed")
        monkeypatch.setattr("app.domain.llm.runtime.gateway.LLMGateway", _FailingGateway)

        with pytest.raises(GatewayError):
            await replay(db, "req-real-replay-failed", "prompt-v2")

        event = _single_event(db)
        assert event.action == "replay_snapshot_v1.replay_attempt"
        assert event.status == "failed"
        assert event.target_id == str(snapshot.id)
        assert event.details["reason"] == "provider_execution_failed"
        _assert_safe_details(event.details)
    finally:
        db.close()


@pytest.mark.asyncio
async def test_real_replay_canonical_hash_mismatch_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prouve le refus explicite quand le hash canonique du snapshot diverge."""
    db = _db_session()
    try:
        snapshot = await _replay_ready_snapshot(db, request_id="req-real-replay-hash-mismatch")
        snapshot.input_hash = "0" * 64
        db.flush()
        monkeypatch.setattr("app.domain.llm.runtime.gateway.LLMGateway", _SuccessfulGateway)

        with pytest.raises(GatewayError):
            await replay(db, "req-real-replay-hash-mismatch", "prompt-v2")

        event = _single_event(db)
        assert event.action == "replay_snapshot_v1.replay_attempt"
        assert event.status == "failed"
        assert event.target_id == str(snapshot.id)
        assert event.details["reason"] == "input_hash_mismatch"
        _assert_safe_details(event.details)
    finally:
        db.close()
