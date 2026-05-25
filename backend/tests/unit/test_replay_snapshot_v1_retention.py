# Commentaire global: ces tests verrouillent la retention 30 jours des snapshots replay.
"""Tests de retention pour replay_snapshot_v1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.infra.db.models  # noqa: F401
from app.domain.llm.runtime.observability_service import log_call
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import LlmReplaySnapshotModel


class _FrozenClock:
    """Horloge de test deterministe pour la retention."""

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


@pytest.mark.asyncio
async def test_new_replay_snapshot_expires_exactly_thirty_days_after_creation(
    db: Session,
) -> None:
    """Prouve que `expires_at` derive exactement de `created_at + 30 jours`."""
    now = datetime(2026, 5, 25, 8, 30, tzinfo=UTC)
    with patch(
        "app.domain.llm.runtime.observability_service.datetime_provider",
        _FrozenClock(now),
    ):
        await log_call(
            db,
            "story-cs-295",
            "request-retention",
            "trace-retention",
            {"message": "bonjour"},
            result=None,
        )

    snapshot = db.execute(select(LlmReplaySnapshotModel)).scalar_one()

    assert snapshot.snapshot_type == "replay_snapshot_v1"
    stored_created_at = snapshot.created_at.replace(tzinfo=UTC)
    stored_expires_at = snapshot.expires_at.replace(tzinfo=UTC)

    assert stored_created_at == now
    assert stored_expires_at == now + timedelta(days=30)
