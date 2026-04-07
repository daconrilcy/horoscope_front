from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.ai_engine.services.log_sanitizer import sanitize_for_logging
from app.core.config import settings
from app.infra.db.models import LlmPersonaModel, LlmPromptVersionModel
from app.infra.db.models.llm_observability import (
    LlmCallLogModel,
    LlmReplaySnapshotModel,
    LlmValidationStatus,
    map_status_to_enum,
)
from app.llm_orchestration.models import GatewayResult
from app.llm_orchestration.services.crypto_utils import encrypt_input

logger = logging.getLogger(__name__)


def safe_uuid(val: Any) -> uuid.UUID | None:
    """
    Safely converts a value to a UUID. Returns None if invalid.
    """
    if not val:
        return None
    try:
        if isinstance(val, uuid.UUID):
            return val
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return None


def _resolve_existing_fk_uuid(db: Session, model: type[Any], raw_value: Any) -> uuid.UUID | None:
    """
    Returns a UUID only when it is syntactically valid and the referenced row exists.
    This keeps observability best-effort even when runtime metadata carries stale IDs.
    """
    resolved_uuid = safe_uuid(raw_value)
    if resolved_uuid is None:
        return None

    try:
        if db.get(model, resolved_uuid) is None:
            return None
    except Exception:
        return None

    return resolved_uuid


def compute_input_hash(user_input: Dict[str, Any]) -> str:
    """
    Computes a SHA-256 hash of the sanitized user input.
    Keys are sorted to ensure reproducibility.
    """
    sanitized = sanitize_for_logging(user_input)
    # Sort keys for consistent hashing
    serialized = json.dumps(sanitized, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def count_evidence_warnings(structured_output: Dict[str, Any] | None) -> int:
    """
    Counts items in 'evidence' that don't match standard format.
    Accepts UPPER_SNAKE_CASE and standard separators used in AstroResponse_v1.
    """
    if not structured_output or "evidence" not in structured_output:
        return 0

    evidence = structured_output["evidence"]
    if not isinstance(evidence, list):
        return 0

    warnings = 0
    # Pattern aligned with AstroResponse_v1 schema
    pattern = re.compile(r"^[A-Z][A-Z0-9_.:-]*$")

    for item in evidence:
        if isinstance(item, str) and not pattern.match(item):
            warnings += 1

    return warnings


async def log_call(
    db: Session,
    use_case: str,
    request_id: str,
    trace_id: str,
    user_input: Dict[str, Any],
    result: GatewayResult | None = None,
    error: Exception | None = None,
) -> None:
    """
    Persists an LLM call log to the database.
    """
    try:
        # Calculate hash from user_input (sanitized)
        input_hash = compute_input_hash(user_input)

        # Prepare fields
        status = LlmValidationStatus.ERROR
        prompt_version_id = None
        persona_id = None
        model = "unknown"
        latency_ms = 0
        tokens_in = 0
        tokens_out = 0
        cost_usd = 0.0
        repair_attempted = False
        fallback_triggered = False
        evidence_warnings = 0

        if result:
            status = map_status_to_enum(result.meta.validation_status)

            if error:  # Force error status if exception occurred
                status = LlmValidationStatus.ERROR

            prompt_version_id = _resolve_existing_fk_uuid(
                db, LlmPromptVersionModel, result.meta.prompt_version_id
            )
            persona_id = _resolve_existing_fk_uuid(db, LlmPersonaModel, result.meta.persona_id)
            model = result.meta.model or "unknown"
            latency_ms = int(result.meta.latency_ms or 0)
            tokens_in = result.usage.input_tokens
            tokens_out = result.usage.output_tokens
            cost_usd = result.usage.estimated_cost_usd
            repair_attempted = result.meta.repair_attempted
            fallback_triggered = result.meta.fallback_triggered
            evidence_warnings = count_evidence_warnings(result.structured_output)

        transaction = db.begin_nested() if db.in_transaction() else db.begin()
        with transaction:
            log_entry = LlmCallLogModel(
                use_case=use_case,
                prompt_version_id=prompt_version_id,
                persona_id=persona_id,
                model=model,
                latency_ms=latency_ms,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd_estimated=cost_usd,
                validation_status=status,
                repair_attempted=repair_attempted,
                fallback_triggered=fallback_triggered,
                request_id=request_id,
                trace_id=trace_id,
                input_hash=input_hash,
                environment=settings.app_env,
                evidence_warnings_count=evidence_warnings,
            )

            db.add(log_entry)
            db.flush()  # Generate log_entry.id inside an isolated transaction scope.

            if user_input:
                snapshot = LlmReplaySnapshotModel(
                    call_log_id=log_entry.id,
                    input_enc=encrypt_input(user_input),
                )
                db.add(snapshot)

    except Exception as e:
        # Observability should not break the main flow
        logger.error("observability_log_call_failed request_id=%s error=%s", request_id, str(e))


async def purge_expired_logs(db: Session) -> int:
    """
    Deletes logs and snapshots that have reached their expiration date.
    Returns the number of deleted records.
    """
    now = datetime.now(timezone.utc)
    from sqlalchemy import delete

    # Delete snapshots first
    stmt_snapshots = delete(LlmReplaySnapshotModel).where(LlmReplaySnapshotModel.expires_at <= now)
    res_snapshots = db.execute(stmt_snapshots)

    # Delete logs
    stmt_logs = delete(LlmCallLogModel).where(LlmCallLogModel.expires_at <= now)
    res_logs = db.execute(stmt_logs)

    db.commit()
    return res_logs.rowcount + res_snapshots.rowcount
