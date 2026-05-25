# Commentaire global: ces tests verrouillent l'absence de cascade hors snapshots replay.
"""Tests d'integration de non-cascade pour replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmReplaySnapshotModel
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service


def _db_session() -> Session:
    """Cree une session SQLite memoire avec le schema applicatif."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_replay_snapshot_purge_does_not_delete_call_logs_or_release_snapshots() -> None:
    """Prouve que la purge ne cascade pas vers journaux ou releases LLM."""
    db = _db_session()
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    try:
        release = LlmReleaseSnapshotModel(
            version="release-cs-296",
            manifest={"scope": "non-cascade"},
            status="draft",
            comment="release fixture",
            created_by="test",
        )
        log = LlmCallLogModel(
            use_case="story-cs-296",
            model="gpt-test",
            latency_ms=1,
            tokens_in=1,
            tokens_out=1,
            cost_usd_estimated=0.0,
            validation_status="valid",
            request_id="request-non-cascade",
            trace_id="trace-non-cascade",
            input_hash="e" * 64,
            environment="test",
            expires_at=now + timedelta(days=90),
        )
        db.add_all([release, log])
        db.flush()
        snapshot = LlmReplaySnapshotModel(
            call_log_id=log.id,
            snapshot_type="replay_snapshot_v1",
            created_at=now - timedelta(days=31),
            expires_at=now - timedelta(days=1),
            input_ref={"kind": "encrypted_isolated_payload_ref", "input_hash": "e" * 64},
            input_hash="e" * 64,
            version_identity={},
            provenance={},
            redaction_state="encrypted_isolated_redacted_metadata_v1",
            input_enc=b"encrypted",
        )
        db.add(snapshot)
        db.commit()

        before_logs = db.scalar(select(func.count()).select_from(LlmCallLogModel))
        before_releases = db.scalar(select(func.count()).select_from(LlmReleaseSnapshotModel))

        result = ReplaySnapshotV1Service.purge_expired(db, now=now)

        after_logs = db.scalar(select(func.count()).select_from(LlmCallLogModel))
        after_releases = db.scalar(select(func.count()).select_from(LlmReleaseSnapshotModel))
        service_source = (
            Base.metadata.tables["llm_replay_snapshots"].name
            + PathLikeSource.replay_service_source()
        )
        assert result.purged_count == 1
        assert after_logs == before_logs
        assert after_releases == before_releases
        assert "narrative_answer_audit" not in service_source
        assert "admin_chart_diagnostics" not in service_source
    finally:
        db.close()


class PathLikeSource:
    """Expose la source service sans ajouter de dependance aux chemins globaux de test."""

    @staticmethod
    def replay_service_source() -> str:
        """Retourne la source du service pour le scan non-cascade cible."""
        from pathlib import Path

        return Path("backend/app/services/replay_snapshot_v1_service.py").read_text(
            encoding="utf-8"
        )
