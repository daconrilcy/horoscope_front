# Commentaire global: ce service centralise le cycle de vie des snapshots replay.
"""Service interne de creation, lecture de metadonnees et purge des snapshots replay."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Any, Dict, Literal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.core.sensitive_data import Sink, sanitize_payload
from app.domain.audit.safe_details import (
    BaseSafeAuditDetails,
    ReplaySnapshotActivityAuditDetails,
    ReplaySnapshotBulkPurgeAuditDetails,
    ReplaySnapshotPurgeAuditDetails,
)
from app.domain.llm.runtime.contracts import GatewayResult
from app.domain.llm.runtime.crypto_utils import encrypt_input
from app.infra.db.models.llm.llm_observability import LlmReplaySnapshotModel
from app.services.ops.audit_service import AuditEventCreatePayload, AuditEventData, AuditService

REPLAY_SNAPSHOT_V1_TYPE = "replay_snapshot_v1"
REPLAY_SNAPSHOT_V1_RETENTION_DAYS = 30
REPLAY_SNAPSHOT_V1_REDACTION_STATE = "encrypted_isolated_redacted_metadata_v1"
REPLAY_SNAPSHOT_V1_PURGED_STATE = "payload_purged_tombstone_v1"

ReplaySnapshotStatus = Literal[
    "success", "not_found", "expired", "already_purged", "incomplete", "validation_failed"
]


@dataclass(frozen=True)
class ReplaySnapshotMetadata:
    """Metadonnees controlees exposees par le service interne replay."""

    snapshot_id: uuid.UUID
    call_log_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    status: ReplaySnapshotStatus
    snapshot_type: str
    input_hash: str
    redaction_state: str
    input_ref: dict[str, Any]
    version_identity: dict[str, Any]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class ReplaySnapshotResult:
    """Resultat metier controle pour une operation replay_snapshot_v1."""

    status: ReplaySnapshotStatus
    metadata: ReplaySnapshotMetadata | None = None
    purged_count: int = 0
    audit_details: BaseSafeAuditDetails | None = None
    audit_event_id: int | None = None
    replay_attempt_id: str | None = None


def _stable_hash(payload: Any) -> str:
    """Produit un hash stable pour une valeur autorisee en reference."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_replay_snapshot_v1_payload(user_input: Dict[str, Any]) -> dict[str, Any]:
    """Construit le payload canonique autorise pour le replay chiffre."""
    return sanitize_payload(user_input, Sink.LLM_REPLAY_SNAPSHOTS)


def compute_replay_snapshot_v1_payload_hash(replay_payload: Dict[str, Any]) -> str:
    """Calcule le hash d'integrite sur le payload replay canonique."""
    return _stable_hash(replay_payload)


def _public_meta_value(value: Any) -> Any:
    """Normalise une valeur runtime en metadonnee JSON sans objet applicatif."""
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def build_replay_snapshot_v1_metadata(
    *,
    user_input: Dict[str, Any],
    request_id: str,
    trace_id: str,
    use_case: str,
    result: GatewayResult | None,
) -> dict[str, Any]:
    """Construit les metadonnees approuvees du snapshot sans donnees brutes."""
    replay_payload = build_replay_snapshot_v1_payload(user_input)
    input_hash = compute_replay_snapshot_v1_payload_hash(replay_payload)
    input_key_hashes = sorted(_stable_hash(key) for key in replay_payload)
    input_ref: dict[str, Any] = {
        "kind": "encrypted_isolated_payload_ref",
        "input_hash": input_hash,
        "input_schema_version": "user_input_key_hashes_v1",
        "input_key_hashes": input_key_hashes,
    }
    if any("birth" in key.lower() for key in replay_payload):
        input_ref["birth_data_ref_hash"] = _stable_hash(replay_payload)

    obs = getattr(result.meta, "obs_snapshot", None) if result else None
    version_identity = {
        "prompt_version_id": getattr(result.meta, "prompt_version_id", None) if result else None,
        "schema_version": getattr(result.meta, "schema_version", None) if result else None,
        "model": getattr(result.meta, "model", None) if result else None,
        "template_source": getattr(result.meta, "template_source", None) if result else None,
        "active_snapshot_version": (
            getattr(obs, "active_snapshot_version", None) if obs is not None else None
        ),
        "manifest_entry_id": getattr(obs, "manifest_entry_id", None) if obs is not None else None,
    }

    provenance = {
        "use_case": use_case,
        "request_ref": request_id,
        "trace_ref": trace_id,
        "diagnostics_ref": getattr(obs, "active_snapshot_id", None) if obs is not None else None,
        "correlation_ref": trace_id,
    }

    return {
        "replay_payload": replay_payload,
        "input_ref": sanitize_payload(input_ref, Sink.LLM_REPLAY_SNAPSHOTS),
        "input_hash": input_hash,
        "version_identity": sanitize_payload(
            {key: _public_meta_value(value) for key, value in version_identity.items()},
            Sink.LLM_REPLAY_SNAPSHOTS,
        ),
        "provenance": sanitize_payload(
            {key: _public_meta_value(value) for key, value in provenance.items()},
            Sink.LLM_REPLAY_SNAPSHOTS,
        ),
        "redaction_state": REPLAY_SNAPSHOT_V1_REDACTION_STATE,
    }


class ReplaySnapshotV1Service:
    """Service canonique du cycle de vie interne des snapshots replay."""

    @staticmethod
    def create_snapshot(
        db: Session,
        *,
        call_log_id: uuid.UUID,
        user_input: Dict[str, Any],
        request_id: str,
        trace_id: str,
        use_case: str,
        result: GatewayResult | None,
        created_at: datetime | None = None,
    ) -> ReplaySnapshotResult:
        """Cree un snapshot replay avec une retention exacte de trente jours."""
        if not user_input:
            return ReplaySnapshotResult(status="validation_failed")

        snapshot_created_at = created_at or datetime_provider.utcnow()
        snapshot_metadata = build_replay_snapshot_v1_metadata(
            user_input=user_input,
            request_id=request_id,
            trace_id=trace_id,
            use_case=use_case,
            result=result,
        )
        snapshot = LlmReplaySnapshotModel(
            call_log_id=call_log_id,
            snapshot_type=REPLAY_SNAPSHOT_V1_TYPE,
            created_at=snapshot_created_at,
            expires_at=snapshot_created_at + timedelta(days=REPLAY_SNAPSHOT_V1_RETENTION_DAYS),
            input_ref=snapshot_metadata["input_ref"],
            input_hash=snapshot_metadata["input_hash"],
            version_identity=snapshot_metadata["version_identity"],
            provenance=snapshot_metadata["provenance"],
            redaction_state=snapshot_metadata["redaction_state"],
            input_enc=encrypt_input(snapshot_metadata["replay_payload"]),
        )
        db.add(snapshot)
        db.flush()
        return ReplaySnapshotResult(
            status="success",
            metadata=ReplaySnapshotV1Service._to_metadata(snapshot, status="success"),
        )

    @staticmethod
    def get_snapshot_metadata(
        db: Session,
        *,
        snapshot_id: uuid.UUID,
        now: datetime | None = None,
        request_id: str | None = None,
        actor_user_id: int | None = None,
        actor_role: str | None = None,
        audit: bool = False,
    ) -> ReplaySnapshotResult:
        """Retourne des metadonnees controlees ou un etat d'indisponibilite explicite."""
        snapshot = ReplaySnapshotV1Service._get_v1_snapshot(db, snapshot_id)
        if snapshot is None:
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=ReplaySnapshotResult(status="not_found"),
                action="replay_snapshot_v1.metadata_read",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )
        if ReplaySnapshotV1Service._is_purged(snapshot):
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=ReplaySnapshotResult(status="already_purged"),
                action="replay_snapshot_v1.metadata_read",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )
        if ReplaySnapshotV1Service._is_expired(snapshot, now=now):
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=ReplaySnapshotResult(status="expired"),
                action="replay_snapshot_v1.metadata_read",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )
        if ReplaySnapshotV1Service._is_incomplete(snapshot):
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=ReplaySnapshotResult(status="incomplete"),
                action="replay_snapshot_v1.metadata_read",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )
        result = ReplaySnapshotResult(
            status="success",
            metadata=ReplaySnapshotV1Service._to_metadata(snapshot, status="success"),
        )
        return ReplaySnapshotV1Service._with_activity_audit(
            db,
            result=result,
            action="replay_snapshot_v1.metadata_read",
            snapshot_id=snapshot_id,
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            audit=audit,
        )

    @staticmethod
    def get_replay_payload_snapshot(
        db: Session,
        *,
        call_log_id: uuid.UUID,
        now: datetime | None = None,
    ) -> ReplaySnapshotResult:
        """Retourne le snapshot utilisable pour l'execution de replay."""
        snapshot = db.execute(
            select(LlmReplaySnapshotModel).where(
                LlmReplaySnapshotModel.call_log_id == call_log_id,
                LlmReplaySnapshotModel.snapshot_type == REPLAY_SNAPSHOT_V1_TYPE,
            )
        ).scalar_one_or_none()
        if snapshot is None:
            return ReplaySnapshotResult(status="not_found")
        metadata_result = ReplaySnapshotV1Service.get_snapshot_metadata(
            db, snapshot_id=snapshot.id, now=now
        )
        if metadata_result.status != "success":
            return metadata_result
        return metadata_result

    @staticmethod
    def purge_expired(
        db: Session,
        *,
        now: datetime | None = None,
        request_id: str | None = None,
        actor_user_id: int | None = None,
        actor_role: str | None = None,
    ) -> ReplaySnapshotResult:
        """Supprime les snapshots v1 expires et prepare un audit borne."""
        effective_now = now or datetime_provider.utcnow()
        result = db.execute(
            delete(LlmReplaySnapshotModel).where(
                LlmReplaySnapshotModel.snapshot_type == REPLAY_SNAPSHOT_V1_TYPE,
                LlmReplaySnapshotModel.expires_at <= effective_now,
            )
        )
        purged_count = int(result.rowcount or 0)
        details = ReplaySnapshotBulkPurgeAuditDetails(
            snapshot_type=REPLAY_SNAPSHOT_V1_TYPE,
            status="success",
            purge_policy="automatic_expired_delete_v1",
            purged_count=purged_count,
        )
        if request_id is not None:
            ReplaySnapshotV1Service._record_bulk_purge_audit(
                db,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                details=details,
            )
        return ReplaySnapshotResult(
            status="success", purged_count=purged_count, audit_details=details
        )

    @staticmethod
    def purge_snapshot(
        db: Session,
        *,
        snapshot_id: uuid.UUID,
        request_id: str,
        actor_user_id: int | None = None,
        actor_role: str | None = None,
        now: datetime | None = None,
        audit: bool = True,
    ) -> ReplaySnapshotResult:
        """Purge manuellement un snapshot par tombstone et prepare un audit borne."""
        snapshot = ReplaySnapshotV1Service._get_v1_snapshot(db, snapshot_id)
        if snapshot is None:
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=ReplaySnapshotResult(status="not_found"),
                action="replay_snapshot_v1.purge",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )
        if ReplaySnapshotV1Service._is_purged(snapshot):
            result = ReplaySnapshotV1Service._manual_purge_result(snapshot, "already_purged")
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=result,
                action="replay_snapshot_v1.purge",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=audit,
            )

        status: ReplaySnapshotStatus = (
            "expired" if ReplaySnapshotV1Service._is_expired(snapshot, now=now) else "success"
        )
        snapshot.input_enc = b""
        snapshot.payload_enc = None
        snapshot.input_ref = {
            "kind": "replay_snapshot_payload_tombstone",
            "snapshot_id": str(snapshot.id),
            "purge_policy": "manual_tombstone_v1",
        }
        snapshot.redaction_state = REPLAY_SNAPSHOT_V1_PURGED_STATE
        db.flush()

        result = ReplaySnapshotV1Service._manual_purge_result(snapshot, status, purged_count=1)
        if audit:
            result = ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=result,
                action="replay_snapshot_v1.purge",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=True,
            )
        return result

    @staticmethod
    def start_replay_attempt(
        db: Session,
        *,
        snapshot_id: uuid.UUID,
        request_id: str,
        actor_user_id: int | None = None,
        actor_role: str | None = None,
        now: datetime | None = None,
    ) -> ReplaySnapshotResult:
        """Accepte une tentative de replay controlee sans exposer le payload chiffre."""
        metadata_result = ReplaySnapshotV1Service.get_snapshot_metadata(
            db,
            snapshot_id=snapshot_id,
            now=now,
        )
        if metadata_result.status != "success" or metadata_result.metadata is None:
            return ReplaySnapshotV1Service._with_activity_audit(
                db,
                result=metadata_result,
                action="replay_snapshot_v1.replay_attempt",
                snapshot_id=snapshot_id,
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                audit=True,
            )

        replay_attempt_id = f"replay-attempt-{uuid.uuid4().hex}"
        details = ReplaySnapshotActivityAuditDetails(
            action="replay_snapshot_v1.replay_attempt",
            status="success",
            snapshot_id=str(snapshot_id),
            request_id=request_id,
            diff_summary={"replay_attempt_id": replay_attempt_id},
        )
        audit_event = ReplaySnapshotV1Service._record_activity_audit(
            db,
            action="replay_snapshot_v1.replay_attempt",
            audit_status="success",
            target_id=str(snapshot_id),
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            details=details,
        )
        return ReplaySnapshotResult(
            status="success",
            metadata=metadata_result.metadata,
            audit_details=details,
            audit_event_id=audit_event.event_id,
            replay_attempt_id=replay_attempt_id,
        )

    @staticmethod
    def _get_v1_snapshot(db: Session, snapshot_id: uuid.UUID) -> LlmReplaySnapshotModel | None:
        """Retourne uniquement une ligne appartenant au contrat replay_snapshot_v1."""
        snapshot = db.get(LlmReplaySnapshotModel, snapshot_id)
        if snapshot is None or snapshot.snapshot_type != REPLAY_SNAPSHOT_V1_TYPE:
            return None
        return snapshot

    @staticmethod
    def _is_expired(snapshot: LlmReplaySnapshotModel, *, now: datetime | None = None) -> bool:
        """Indique si un snapshot a depasse sa date d'expiration."""
        effective_now = now or datetime_provider.utcnow()
        expires_at = snapshot.expires_at
        if expires_at.tzinfo is None and effective_now.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=effective_now.tzinfo)
        return expires_at <= effective_now

    @staticmethod
    def _is_purged(snapshot: LlmReplaySnapshotModel) -> bool:
        """Indique si le payload replay a deja ete remplace par une tombstone."""
        return snapshot.redaction_state == REPLAY_SNAPSHOT_V1_PURGED_STATE

    @staticmethod
    def _is_incomplete(snapshot: LlmReplaySnapshotModel) -> bool:
        """Refuse un snapshot qui ne porte pas l'etat chiffre approuve."""
        return (
            snapshot.redaction_state != REPLAY_SNAPSHOT_V1_REDACTION_STATE
            or not snapshot.input_enc
            or not snapshot.input_hash
            or dict(snapshot.input_ref or {}).get("kind") != "encrypted_isolated_payload_ref"
        )

    @staticmethod
    def _to_metadata(
        snapshot: LlmReplaySnapshotModel,
        *,
        status: ReplaySnapshotStatus,
    ) -> ReplaySnapshotMetadata:
        """Convertit une ligne persistante en metadonnees internes controlees."""
        return ReplaySnapshotMetadata(
            snapshot_id=snapshot.id,
            call_log_id=snapshot.call_log_id,
            created_at=snapshot.created_at,
            expires_at=snapshot.expires_at,
            status=status,
            snapshot_type=snapshot.snapshot_type,
            input_hash=snapshot.input_hash,
            redaction_state=snapshot.redaction_state,
            input_ref=dict(snapshot.input_ref or {}),
            version_identity=dict(snapshot.version_identity or {}),
            provenance=dict(snapshot.provenance or {}),
        )

    @staticmethod
    def _manual_purge_result(
        snapshot: LlmReplaySnapshotModel,
        status: ReplaySnapshotStatus,
        *,
        purged_count: int = 0,
    ) -> ReplaySnapshotResult:
        """Construit le resultat controle d'une purge manuelle."""
        details = ReplaySnapshotPurgeAuditDetails(
            snapshot_id=str(snapshot.id),
            call_log_id=str(snapshot.call_log_id),
            status=status,
            purge_policy="manual_tombstone_v1",
            purged_count=purged_count,
        )
        return ReplaySnapshotResult(
            status=status,
            metadata=ReplaySnapshotV1Service._to_metadata(snapshot, status=status),
            purged_count=purged_count,
            audit_details=details,
        )

    def _with_activity_audit(
        db: Session,
        *,
        result: ReplaySnapshotResult,
        action: str,
        snapshot_id: uuid.UUID,
        request_id: str | None,
        actor_user_id: int | None,
        actor_role: str | None,
        audit: bool,
    ) -> ReplaySnapshotResult:
        """Ajoute l'audit admin CS-298 sans changer le resultat metier."""
        if not audit or request_id is None:
            return result
        reason = None if result.status == "success" else result.status
        details = ReplaySnapshotActivityAuditDetails(
            action=action,
            status="success" if result.status == "success" else "failed",
            snapshot_id=str(snapshot_id),
            request_id=request_id,
            reason=reason,
        )
        event = ReplaySnapshotV1Service._record_activity_audit(
            db,
            action=action,
            audit_status=details.status,
            target_id=str(snapshot_id),
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            details=details,
        )
        return replace(result, audit_details=details, audit_event_id=event.event_id)

    @staticmethod
    def _record_activity_audit(
        db: Session,
        *,
        action: str,
        audit_status: str,
        target_id: str,
        request_id: str,
        actor_user_id: int | None,
        actor_role: str | None,
        details: ReplaySnapshotActivityAuditDetails,
    ) -> AuditEventData:
        """Persiste un evenement admin borne pour replay_snapshot_v1."""
        return AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role or "system",
                action=action,
                target_type="llm_replay_snapshot",
                target_id=target_id,
                status=audit_status,
                details=details.model_dump(exclude_none=True),
            ),
        )

    @staticmethod
    def _record_bulk_purge_audit(
        db: Session,
        *,
        request_id: str,
        actor_user_id: int | None,
        actor_role: str | None,
        details: ReplaySnapshotBulkPurgeAuditDetails,
    ) -> None:
        """Enregistre l'audit borne d'une purge automatique sans lister les payloads."""
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role or "system",
                action="llm_replay_snapshots_expired_purged",
                target_type="llm_replay_snapshot_batch",
                target_id=None,
                status="success",
                details=details.model_dump(exclude_none=True),
            ),
        )
