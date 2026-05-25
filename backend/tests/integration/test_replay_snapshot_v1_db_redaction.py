# Commentaire global: ces tests inspectent les lignes DB replay_snapshot_v1 contre les
# fuites brutes.
"""Tests d'integration de redaction DB pour replay_snapshot_v1."""

from __future__ import annotations

import json
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.llm.runtime.crypto_utils import decrypt_input
from app.domain.llm.runtime.observability_service import log_call
from app.infra.db.models.llm.llm_observability import LlmReplaySnapshotModel
from app.services.replay_snapshot_v1_service import compute_replay_snapshot_v1_payload_hash


@pytest.mark.asyncio
async def test_persisted_replay_snapshot_metadata_excludes_raw_sensitive_values(
    db: Session,
) -> None:
    """Prouve que les colonnes inspectables ne contiennent pas de donnees brutes."""
    request_id = f"request-cs-295-{uuid.uuid4().hex}"
    await log_call(
        db,
        "story-cs-295",
        request_id,
        "trace-cs-295",
        {
            "message": "interpretation confidentielle",
            "birth_date": "1991-04-05",
            "birth_time": "12:34",
            "birth_place": "Paris",
            "email": "person@example.com",
            "password": "admin123",
        },
        result=None,
    )

    snapshot = db.execute(select(LlmReplaySnapshotModel)).scalar_one()
    inspectable_payload = json.dumps(
        {
            "input_ref": snapshot.input_ref,
            "version_identity": snapshot.version_identity,
            "provenance": snapshot.provenance,
            "redaction_state": snapshot.redaction_state,
            "snapshot_type": snapshot.snapshot_type,
        },
        sort_keys=True,
        default=str,
    )

    for forbidden in (
        "interpretation confidentielle",
        "1991-04-05",
        "12:34",
        "Paris",
        "person@example.com",
        "admin123",
    ):
        assert forbidden not in inspectable_payload

    encrypted_payload = decrypt_input(snapshot.input_enc)
    assert snapshot.input_hash == compute_replay_snapshot_v1_payload_hash(encrypted_payload)
    assert snapshot.input_ref["input_hash"] == snapshot.input_hash
    assert encrypted_payload["message"] != "interpretation confidentielle"
    assert encrypted_payload["birth_date"] != "1991-04-05"
    assert encrypted_payload["birth_time"] != "12:34"
    assert encrypted_payload["birth_place"] != "Paris"
    assert encrypted_payload["email"] != "person@example.com"
    assert "password" not in encrypted_payload
