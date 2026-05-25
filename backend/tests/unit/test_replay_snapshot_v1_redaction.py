# Commentaire global: ces tests bloquent la persistance de donnees sensibles brutes en replay.
"""Tests de redaction pour replay_snapshot_v1."""

from __future__ import annotations

import json

from app.core.sensitive_data import Sink, sanitize_payload
from app.domain.llm.runtime.crypto_utils import decrypt_input, encrypt_input
from app.domain.llm.runtime.observability_service import build_replay_snapshot_v1_metadata


def test_replay_sink_removes_provider_secrets_before_encryption() -> None:
    """Verifie que les valeurs brutes interdites ne franchissent pas la frontiere chiffree."""
    sanitized = sanitize_payload(
        {
            "prompt": "question utilisateur",
            "api_key": "sk-forbidden",
            "token": "token-forbidden",
            "birth_date": "1991-04-05",
        },
        Sink.LLM_REPLAY_SNAPSHOTS,
    )

    encrypted = encrypt_input(sanitized)
    decrypted = decrypt_input(encrypted)

    assert "api_key" not in decrypted
    assert "token" not in decrypted
    assert decrypted["prompt"] != "question utilisateur"
    assert decrypted["birth_date"] != "1991-04-05"
    assert decrypted["prompt"].endswith("...")
    assert decrypted["birth_date"].endswith("...")


def test_replay_snapshot_metadata_does_not_include_forbidden_raw_values() -> None:
    """Verifie que les colonnes JSON ne portent que des references et hashes."""
    metadata = build_replay_snapshot_v1_metadata(
        user_input={
            "raw_prompt": "texte prompt interdit",
            "birth_date": "1991-04-05",
            "birth_time": "12:34",
            "birth_place": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "email": "person@example.com",
            "password": "admin123",
        },
        request_id="request-redaction",
        trace_id="trace-redaction",
        use_case="story-cs-295",
        result=None,
    )

    encoded = json.dumps(
        {
            "input_ref": metadata["input_ref"],
            "version_identity": metadata["version_identity"],
            "provenance": metadata["provenance"],
            "redaction_state": metadata["redaction_state"],
        },
        sort_keys=True,
    )

    for forbidden in (
        "texte prompt interdit",
        "1991-04-05",
        "12:34",
        "Paris",
        "48.8566",
        "2.3522",
        "person@example.com",
        "admin123",
    ):
        assert forbidden not in encoded
