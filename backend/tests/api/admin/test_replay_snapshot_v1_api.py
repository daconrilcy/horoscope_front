# Commentaire global: ces tests prouvent l'exposition admin interne des snapshots replay v1.
"""Tests API admin pour le contrat `admin_replay_snapshot_v1`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.admin.audit import get_replay_snapshot_v1_service
from app.core.auth_context import AuthenticatedUser
from app.infra.db.session import get_db_session
from app.main import app
from app.services.replay_snapshot_v1_service import (
    REPLAY_SNAPSHOT_V1_REDACTION_STATE,
    ReplaySnapshotMetadata,
    ReplaySnapshotResult,
)

CLIENT = TestClient(app)
SNAPSHOT_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
CALL_LOG_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
FORBIDDEN_FIELDS = {
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


class _DbStub:
    """Session minimale pour verifier les commits d'ecriture API."""

    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        """Marque un commit attendu par les endpoints mutateurs."""
        self.committed = True


class _ReplayServiceStub:
    """Service replay controle par test pour isoler le contrat HTTP."""

    def __init__(self, result: ReplaySnapshotResult) -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_snapshot_metadata(
        self,
        db: _DbStub,
        *,
        snapshot_id: uuid.UUID,
        request_id: str,
        actor_user_id: int | None,
        actor_role: str | None,
        audit: bool,
    ) -> ReplaySnapshotResult:
        """Capture l'appel de lecture metadata."""
        self.calls.append(
            (
                "get",
                {
                    "snapshot_id": snapshot_id,
                    "request_id": request_id,
                    "actor_user_id": actor_user_id,
                    "actor_role": actor_role,
                    "audit": audit,
                },
            )
        )
        return self.result

    def start_replay_attempt(
        self,
        db: _DbStub,
        *,
        snapshot_id: uuid.UUID,
        request_id: str,
        actor_user_id: int | None,
        actor_role: str | None,
    ) -> ReplaySnapshotResult:
        """Capture l'appel de tentative controlee."""
        self.calls.append(
            (
                "attempt",
                {
                    "snapshot_id": snapshot_id,
                    "request_id": request_id,
                    "actor_user_id": actor_user_id,
                    "actor_role": actor_role,
                },
            )
        )
        return self.result

    def purge_snapshot(
        self,
        db: _DbStub,
        *,
        snapshot_id: uuid.UUID,
        request_id: str,
        actor_user_id: int | None,
        actor_role: str | None,
    ) -> ReplaySnapshotResult:
        """Capture l'appel de purge manuelle auditee."""
        self.calls.append(
            (
                "purge",
                {
                    "snapshot_id": snapshot_id,
                    "request_id": request_id,
                    "actor_user_id": actor_user_id,
                    "actor_role": actor_role,
                },
            )
        )
        return self.result


@pytest.fixture(autouse=True)
def _clear_overrides() -> None:
    """Nettoie les substitutions FastAPI entre tests."""
    app.dependency_overrides.clear()
    app.openapi_schema = None
    yield
    app.dependency_overrides.clear()
    app.openapi_schema = None


def _metadata(*, status: str = "success") -> ReplaySnapshotMetadata:
    """Construit des metadonnees redigees representatives."""
    created_at = datetime(2026, 5, 25, 8, 0, tzinfo=UTC)
    return ReplaySnapshotMetadata(
        snapshot_id=SNAPSHOT_ID,
        call_log_id=CALL_LOG_ID,
        created_at=created_at,
        expires_at=created_at + timedelta(days=30),
        status=status,
        snapshot_type="replay_snapshot_v1",
        input_hash="0" * 64,
        redaction_state=REPLAY_SNAPSHOT_V1_REDACTION_STATE,
        input_ref={"kind": "encrypted_isolated_payload_ref"},
        version_identity={"model": "gpt-5-mini", "prompt_version_id": "prompt-v1"},
        provenance={"trace_ref": "trace-safe", "diagnostics_ref": "diag-safe"},
    )


def _result(
    *,
    status: str = "success",
    replay_attempt_id: str | None = None,
    audit_event_id: int | None = None,
) -> ReplaySnapshotResult:
    """Construit un resultat service pour les cas HTTP."""
    return ReplaySnapshotResult(
        status=status,
        metadata=_metadata(status=status) if status == "success" else None,
        replay_attempt_id=replay_attempt_id,
        audit_event_id=audit_event_id,
    )


def _admin_user() -> AuthenticatedUser:
    """Retourne une identite admin pour les tests de surface protegee."""
    return AuthenticatedUser(
        id=42,
        role="admin",
        email="admin@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=UTC),
    )


def _user_with_role(role: str) -> AuthenticatedUser:
    """Retourne une identite non admin pour verifier le refus."""
    return AuthenticatedUser(
        id=43,
        role=role,
        email=f"{role}@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=UTC),
    )


def _install_overrides(service: _ReplayServiceStub, db: _DbStub | None = None) -> _DbStub:
    """Installe les dependances FastAPI controlees par les tests."""
    db_stub = db or _DbStub()
    app.dependency_overrides[require_authenticated_user] = _admin_user
    app.dependency_overrides[get_db_session] = lambda: db_stub
    app.dependency_overrides[get_replay_snapshot_v1_service] = lambda: service
    return db_stub


def test_admin_get_metadata_returns_redacted_contract() -> None:
    """Verifie le contrat metadata sans champ brut ou identifiant direct."""
    service = _ReplayServiceStub(_result(audit_event_id=789))
    db = _install_overrides(service)

    response = CLIENT.get(
        f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}",
        headers={"X-Request-Id": "req-metadata-api"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["contract_id"] == "admin_replay_snapshot_v1"
    assert payload["snapshot_id"] == str(SNAPSHOT_ID)
    assert payload["status"] == "success"
    assert payload["audit_event_id"] == 789
    assert payload["redaction_state"] == REPLAY_SNAPSHOT_V1_REDACTION_STATE
    assert payload["version_identity"] == {"model": "gpt-5-mini", "prompt_version_id": "prompt-v1"}
    assert payload["provenance_refs"] == {"trace_ref": "trace-safe", "diagnostics_ref": "diag-safe"}
    assert FORBIDDEN_FIELDS.isdisjoint(payload)
    assert db.committed is True
    assert service.calls == [
        (
            "get",
            {
                "snapshot_id": SNAPSHOT_ID,
                "request_id": "req-metadata-api",
                "actor_user_id": 42,
                "actor_role": "admin",
                "audit": True,
            },
        )
    ]


def test_admin_replay_attempt_is_accepted_and_audited() -> None:
    """Verifie la tentative controlee et le commit de son audit."""
    service = _ReplayServiceStub(
        _result(replay_attempt_id="replay-attempt-test", audit_event_id=123)
    )
    db = _install_overrides(service)

    response = CLIENT.post(
        f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}/replay-attempt",
        headers={"X-Request-Id": "req-replay-api"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["replay_attempt_id"] == "replay-attempt-test"
    assert payload["audit_event_id"] == 123
    assert FORBIDDEN_FIELDS.isdisjoint(payload)
    assert db.committed is True
    assert service.calls == [
        (
            "attempt",
            {
                "snapshot_id": SNAPSHOT_ID,
                "request_id": "req-replay-api",
                "actor_user_id": 42,
                "actor_role": "admin",
            },
        )
    ]


def test_admin_manual_purge_returns_204_and_commits_audit() -> None:
    """Verifie la purge manuelle via service canonique et audit."""
    service = _ReplayServiceStub(_result(audit_event_id=456))
    db = _install_overrides(service)

    response = CLIENT.delete(
        f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}",
        headers={"X-Request-Id": "req-purge-api"},
    )

    assert response.status_code == 204
    assert response.content == b""
    assert db.committed is True
    assert service.calls == [
        (
            "purge",
            {
                "snapshot_id": SNAPSHOT_ID,
                "request_id": "req-purge-api",
                "actor_user_id": 42,
                "actor_role": "admin",
            },
        )
    ]


def test_non_admin_and_unauthenticated_access_are_denied() -> None:
    """Prouve les refus 401 et 403 par la dependance admin approuvee."""
    service = _ReplayServiceStub(_result())
    app.dependency_overrides[get_replay_snapshot_v1_service] = lambda: service
    app.dependency_overrides[get_db_session] = lambda: _DbStub()

    missing_auth = CLIENT.get(f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}")

    app.dependency_overrides[require_authenticated_user] = lambda: _user_with_role("user")
    forbidden_user = CLIENT.get(f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}")

    app.dependency_overrides[require_authenticated_user] = lambda: _user_with_role("support")
    forbidden_support = CLIENT.get(f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}")

    assert missing_auth.status_code == 401
    assert forbidden_user.status_code == 403
    assert forbidden_support.status_code == 403
    assert service.calls == []


@pytest.mark.parametrize(
    ("service_status", "expected_status"),
    [
        ("not_found", 404),
        ("expired", 410),
        ("already_purged", 410),
    ],
)
def test_missing_expired_and_purged_states_are_stable_errors(
    service_status: str,
    expected_status: int,
) -> None:
    """Verifie le mapping HTTP des etats indisponibles."""
    service = _ReplayServiceStub(_result(status=service_status, audit_event_id=999))
    db = _install_overrides(service)

    response = CLIENT.get(f"/v1/admin/audit/replay_snapshot_v1/{SNAPSHOT_ID}")

    assert response.status_code == expected_status
    assert db.committed is True


def test_runtime_routes_and_openapi_expose_only_admin_replay_snapshot() -> None:
    """Bloque les chemins publics, support, client et frontend."""
    runtime_paths = {getattr(route, "path", "") for route in app.routes}
    openapi_paths = set(app.openapi()["paths"])

    expected_paths = {
        "/v1/admin/audit/replay_snapshot_v1/{snapshot_id}",
        "/v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt",
    }
    assert expected_paths <= runtime_paths
    assert expected_paths <= openapi_paths

    forbidden_paths = {
        "/v1/replay_snapshot_v1",
        "/v1/public/replay_snapshot_v1",
        "/v1/support/replay_snapshot_v1",
        "/api/replay_snapshot_v1",
        "/replay_snapshot_v1",
    }
    assert forbidden_paths.isdisjoint(runtime_paths)
    assert forbidden_paths.isdisjoint(openapi_paths)
    assert all(
        path.startswith("/v1/admin/audit") for path in openapi_paths if "replay_snapshot_v1" in path
    )
