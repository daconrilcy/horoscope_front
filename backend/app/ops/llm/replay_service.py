# Commentaire global: ce module orchestre le rejeu LLM sans posseder la politique de snapshot.
"""Service d'execution de replay LLM adosse au cycle de vie replay_snapshot_v1."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.audit.safe_details import ReplaySnapshotActivityAuditDetails
from app.domain.llm.runtime.contracts import GatewayError, ReplayResult
from app.domain.llm.runtime.crypto_utils import decrypt_input
from app.domain.llm.runtime.observability_service import compute_input_hash
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmReplaySnapshotModel,
    map_status_to_enum,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.replay_snapshot_v1_service import ReplaySnapshotV1Service

logger = logging.getLogger(__name__)


def _record_replay_attempt_audit(
    db: Session,
    *,
    snapshot_id: uuid.UUID,
    request_id: str,
    status: str,
    reason: str | None = None,
    diff_summary: dict[str, Any] | None = None,
) -> None:
    """Trace une tentative de replay reelle avec un detail d'audit borne."""
    details = ReplaySnapshotActivityAuditDetails(
        action="replay_snapshot_v1.replay_attempt",
        status=status,
        snapshot_id=str(snapshot_id),
        request_id=request_id,
        reason=reason,
        diff_summary=diff_summary,
    )
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="system",
            action="replay_snapshot_v1.replay_attempt",
            target_type="llm_replay_snapshot",
            target_id=str(snapshot_id),
            status=status,
            details=details.model_dump(exclude_none=True),
        ),
    )


async def replay(
    db: Session,
    request_id: str,
    prompt_version_id: str,
) -> ReplayResult:
    """
    Replays an LLM call with a different prompt version.
    """
    # AC7: Refuse in production - LOCKED to settings.app_env
    env = settings.app_env
    if env.lower() in ["prod", "production"]:
        raise GatewayError(
            "Replay tool is disabled in production environments.", details={"env": env}
        )

    # 1. Fetch original call log
    stmt = select(LlmCallLogModel).where(LlmCallLogModel.request_id == request_id)
    original_log = db.execute(stmt).scalar_one_or_none()
    if not original_log:
        raise GatewayError(f"Call log not found for request_id: {request_id}")

    # 2. Fetch encrypted input snapshot through the canonical lifecycle service
    snapshot_result = ReplaySnapshotV1Service.get_replay_payload_snapshot(
        db,
        call_log_id=original_log.id,
    )
    if snapshot_result.status != "success" or snapshot_result.metadata is None:
        candidate_snapshot = db.execute(
            select(LlmReplaySnapshotModel).where(
                LlmReplaySnapshotModel.call_log_id == original_log.id,
                LlmReplaySnapshotModel.snapshot_type == "replay_snapshot_v1",
            )
        ).scalar_one_or_none()
        if candidate_snapshot is not None:
            _record_replay_attempt_audit(
                db,
                snapshot_id=candidate_snapshot.id,
                request_id=request_id,
                status="failed",
                reason=snapshot_result.status,
            )
        raise GatewayError(
            f"Input snapshot unavailable for request_id: {request_id}",
            details={"status": snapshot_result.status},
        )
    snapshot = db.get(LlmReplaySnapshotModel, snapshot_result.metadata.snapshot_id)
    if snapshot is None:
        _record_replay_attempt_audit(
            db,
            snapshot_id=snapshot_result.metadata.snapshot_id,
            request_id=request_id,
            status="failed",
            reason="not_found",
        )
        raise GatewayError(
            f"Input snapshot unavailable for request_id: {request_id}",
            details={"status": "not_found"},
        )

    # 3. Decrypt user_input
    user_input = decrypt_input(snapshot.input_enc)

    # 3b. Integrity check: recompute hash and compare with original log
    recomputed_hash = compute_input_hash(user_input)
    if recomputed_hash != original_log.input_hash:
        logger.error(
            "replay_integrity_check_failed request_id=%s expected=%s computed=%s",
            request_id,
            original_log.input_hash,
            recomputed_hash,
        )
        _record_replay_attempt_audit(
            db,
            snapshot_id=snapshot.id,
            request_id=request_id,
            status="failed",
            reason="input_hash_mismatch",
        )
        raise GatewayError(
            "Integrity check failed for replay: input hash mismatch.",
            details={"request_id": request_id},
        )

    # 4. Execute Gateway with new prompt_version_id
    from app.domain.llm.runtime.gateway import LLMGateway

    gateway = LLMGateway()

    # We add a special key to context to override the prompt version
    context = {
        "_override_prompt_version_id": prompt_version_id,
        "persona_id": str(original_log.persona_id) if original_log.persona_id else None,
    }

    try:
        result = await gateway.execute(
            use_case=original_log.use_case,
            user_input=user_input,
            context=context,
            request_id=f"replay-{uuid.uuid4().hex[:8]}",
            trace_id=f"replay-{original_log.trace_id}",
            db=db,
        )
    except Exception:
        _record_replay_attempt_audit(
            db,
            snapshot_id=snapshot.id,
            request_id=request_id,
            status="failed",
            reason="provider_execution_failed",
        )
        raise

    # 5. Build diff vs original
    new_status = map_status_to_enum(result.meta.validation_status)
    orig_status = original_log.validation_status

    # Normalize values to strings
    orig_val = orig_status.value if hasattr(orig_status, "value") else str(orig_status)
    new_val = new_status.value

    diff = {
        "original_validation_status": orig_val,
        "new_validation_status": new_val,
        "status_changed": orig_val != new_val,
    }
    _record_replay_attempt_audit(
        db,
        snapshot_id=snapshot.id,
        request_id=request_id,
        status="success",
        diff_summary=diff,
    )

    return ReplayResult(
        use_case=result.use_case,
        prompt_version_id=result.meta.prompt_version_id,
        persona_id=result.meta.persona_id,
        raw_output=None,  # AC7: Strict non-textual default
        structured_output=None,  # AC7: Strict non-textual default
        validation_status=new_val,
        latency_ms=result.meta.latency_ms,
        tokens_in=result.usage.input_tokens,
        tokens_out=result.usage.output_tokens,
        diff_vs_original=diff,
    )
