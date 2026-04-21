from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.llm.runtime.contracts import GatewayError, ReplayResult
from app.domain.llm.runtime.crypto_utils import decrypt_input
from app.domain.llm.runtime.observability_service import compute_input_hash
from app.infra.db.models.llm_observability import (
    LlmCallLogModel,
    LlmReplaySnapshotModel,
    map_status_to_enum,
)

logger = logging.getLogger(__name__)


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

    # 2. Fetch encrypted input snapshot
    stmt_snap = select(LlmReplaySnapshotModel).where(
        LlmReplaySnapshotModel.call_log_id == original_log.id
    )
    snapshot = db.execute(stmt_snap).scalar_one_or_none()
    if not snapshot:
        raise GatewayError(f"Input snapshot not found or expired for request_id: {request_id}")

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

    result = await gateway.execute(
        use_case=original_log.use_case,
        user_input=user_input,
        context=context,
        request_id=f"replay-{uuid.uuid4().hex[:8]}",
        trace_id=f"replay-{original_log.trace_id}",
        db=db,
    )

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
