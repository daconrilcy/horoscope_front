# Commentaire global: ces tests prouvent la forme de stockage approuvee replay_snapshot_v1.
"""Tests du contrat de schema et metadonnees des snapshots de rejeu."""

from __future__ import annotations

import json

from app.domain.llm.runtime.contracts import GatewayMeta, GatewayResult, UsageInfo
from app.domain.llm.runtime.observability_service import (
    REPLAY_SNAPSHOT_V1_REDACTION_STATE,
    REPLAY_SNAPSHOT_V1_TYPE,
    build_replay_snapshot_v1_metadata,
)
from app.infra.db.models.llm.llm_observability import LlmReplaySnapshotModel


def _gateway_result() -> GatewayResult:
    """Construit un resultat minimal porteur d'identite de version."""
    return GatewayResult(
        use_case="story-cs-295",
        request_id="request-cs-295",
        trace_id="trace-cs-295",
        raw_output="",
        structured_output={},
        usage=UsageInfo(),
        meta=GatewayMeta(
            latency_ms=12,
            model="gpt-test",
            prompt_version_id="prompt-template-v7",
            schema_version="structured-facts-v1",
            template_source="catalog",
            validation_status="valid",
        ),
    )


def test_replay_snapshot_model_contains_approved_v1_columns() -> None:
    """Verifie que le modele porte les champs approuves sans second store."""
    columns = set(LlmReplaySnapshotModel.__table__.columns.keys())

    assert {
        "snapshot_type",
        "call_log_id",
        "created_at",
        "expires_at",
        "input_ref",
        "input_hash",
        "version_identity",
        "provenance",
        "redaction_state",
        "input_enc",
        "payload_enc",
    }.issubset(columns)
    assert LlmReplaySnapshotModel.__tablename__ == "llm_replay_snapshots"


def test_replay_snapshot_metadata_keeps_only_references_hashes_and_versions() -> None:
    """Verifie que les metadonnees persistables excluent le contenu utilisateur brut."""
    metadata = build_replay_snapshot_v1_metadata(
        user_input={
            "message": "je veux une interpretation complete",
            "birth_date": "1991-04-05",
            "birth_time": "12:34",
            "birth_place": "Paris",
            "email": "person@example.com",
            "api_key": "sk-secret",
        },
        input_hash="a" * 64,
        request_id="request-cs-295",
        trace_id="trace-cs-295",
        use_case="story-cs-295",
        result=_gateway_result(),
    )

    assert metadata["input_ref"]["kind"] == "encrypted_isolated_payload_ref"
    assert metadata["input_ref"]["input_hash"] == "a" * 64
    assert metadata["redaction_state"] == REPLAY_SNAPSHOT_V1_REDACTION_STATE
    assert metadata["version_identity"]["prompt_version_id"] == "prompt-template-v7"

    persisted_metadata = {
        "snapshot_type": REPLAY_SNAPSHOT_V1_TYPE,
        "input_ref": metadata["input_ref"],
        "version_identity": metadata["version_identity"],
        "provenance": metadata["provenance"],
        "redaction_state": metadata["redaction_state"],
    }
    encoded = json.dumps(persisted_metadata, sort_keys=True)

    for forbidden in (
        "je veux une interpretation complete",
        "1991-04-05",
        "12:34",
        "Paris",
        "person@example.com",
        "sk-secret",
    ):
        assert forbidden not in encoded
