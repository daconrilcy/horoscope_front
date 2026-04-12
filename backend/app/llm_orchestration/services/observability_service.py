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
from app.infra.observability.metrics import increment_counter
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


def log_governance_event(
    event_type: str,
    provider: str | None = None,
    feature: str | None = None,
    subfeature: str | None = None,
    is_nominal: bool = True,
    reason: str | None = None,
) -> None:
    """
    Emits unified governance metrics (AC6, Story 66.23 AC10, 66.30 AC8).
    event_type: publish_rejected | runtime_rejected | non_nominal_tolerated
                | legacy_feature_alias_used
    """
    labels = {
        "event_type": event_type,
        "provider": provider or "unknown",
        "feature": feature or "unknown",
        "subfeature": subfeature or "unknown",
        "is_nominal": str(is_nominal).lower(),
        "reason": reason or "unknown",
    }
    increment_counter("llm_governance_event_total", labels=labels)
    if event_type == "runtime_rejected":
        increment_counter(
            "llm_runtime_rejection_total",
            labels={
                "feature": feature or "unknown",
                "subfeature": subfeature or "unknown",
                "provider": provider or "unknown",
                "is_nominal": str(is_nominal).lower(),
                "reason": reason or "unknown",
            },
        )
    logger.info(
        "llm_governance_event type=%s provider=%s feature=%s subfeature=%s is_nominal=%s reason=%s",
        event_type,
        provider,
        feature,
        subfeature,
        is_nominal,
        reason,
    )


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
        assembly_id = None
        feature = None
        subfeature = None
        plan = None
        template_source = None
        prompt_version_id = None
        persona_id = None
        provider = "openai"
        model = "unknown"
        latency_ms = 0
        tokens_in = 0
        tokens_out = 0
        cost_usd = 0.0
        repair_attempted = False
        fallback_triggered = False
        evidence_warnings = 0

        # --- Story 66.25: Operational Observability Init ---
        pipeline_kind = None
        execution_path_kind = None
        fallback_kind = None
        requested_provider = None
        resolved_provider = None
        executed_provider = None
        context_compensation_status = None
        max_output_tokens_source = None
        max_output_tokens_final = None

        # --- Story 66.33: Operational Hardening Init ---
        executed_provider_mode = "nominal"
        attempt_count = 1
        provider_error_code = None
        breaker_state = None
        breaker_scope = None

        active_snapshot_id = None
        active_snapshot_version = None
        manifest_entry_id = None

        if result:
            status = map_status_to_enum(result.meta.validation_status)

            # Story 66.32 AC12: Resolve Snapshot info
            active_snapshot_id = safe_uuid(
                getattr(result.meta.obs_snapshot, "active_snapshot_id", None)
            )
            active_snapshot_version = getattr(
                result.meta.obs_snapshot, "active_snapshot_version", None
            )
            manifest_entry_id = getattr(result.meta.obs_snapshot, "manifest_entry_id", None)

            if error:  # Force error status if exception occurred
                status = LlmValidationStatus.ERROR

            # Resolve Assembly metadata if present (Story 66.8 AC10)
            assembly_id = safe_uuid(getattr(result.meta, "assembly_id", None))
            feature = getattr(result.meta, "feature", None)
            subfeature = getattr(result.meta, "subfeature", None)
            plan = getattr(result.meta, "plan", None)
            template_source = getattr(result.meta, "template_source", None)

            prompt_version_id = _resolve_existing_fk_uuid(
                db, LlmPromptVersionModel, result.meta.prompt_version_id
            )
            persona_id = _resolve_existing_fk_uuid(db, LlmPersonaModel, result.meta.persona_id)
            provider = result.meta.provider or "openai"
            model = result.meta.model or "unknown"
            latency_ms = int(result.meta.latency_ms or 0)
            tokens_in = result.usage.input_tokens
            tokens_out = result.usage.output_tokens
            cost_usd = result.usage.estimated_cost_usd
            repair_attempted = result.meta.repair_attempted
            fallback_triggered = result.meta.fallback_triggered
            evidence_warnings = count_evidence_warnings(result.structured_output)

            # --- Story 66.33: Operational Hardening ---
            executed_provider_mode = getattr(result.meta, "executed_provider_mode", "nominal")
            attempt_count = getattr(result.meta, "attempt_count", 1)
            provider_error_code = getattr(result.meta, "provider_error_code", None)
            breaker_state = getattr(result.meta, "breaker_state", None)
            breaker_scope = getattr(result.meta, "breaker_scope", None)

            # --- Story 66.25: Operational Observability ---
            obs = getattr(result.meta, "obs_snapshot", None)
            if obs:
                pipeline_kind = obs.pipeline_kind
                execution_path_kind = (
                    obs.execution_path_kind.value
                    if hasattr(obs.execution_path_kind, "value")
                    else obs.execution_path_kind
                )
                fallback_kind = (
                    obs.fallback_kind.value
                    if obs.fallback_kind and hasattr(obs.fallback_kind, "value")
                    else obs.fallback_kind
                )
                requested_provider = obs.requested_provider
                resolved_provider = obs.resolved_provider
                executed_provider = obs.executed_provider
                context_compensation_status = (
                    obs.context_compensation_status.value
                    if hasattr(obs.context_compensation_status, "value")
                    else obs.context_compensation_status
                )
                max_output_tokens_source = (
                    obs.max_output_tokens_source.value
                    if hasattr(obs.max_output_tokens_source, "value")
                    else obs.max_output_tokens_source
                )
                max_output_tokens_final = obs.max_output_tokens_final

        elif error:
            # Story 66.33 Finding High: Recover hardening metadata from exception
            status = LlmValidationStatus.ERROR
            executed_provider_mode = getattr(error, "_executed_provider_mode", "nominal")
            attempt_count = getattr(error, "_attempt_count", 1)
            provider_error_code = getattr(error, "_provider_error_code", None)
            breaker_state = getattr(error, "_breaker_state", None)
            breaker_scope = getattr(error, "_breaker_scope", None)

        # Increment specific metrics (AC8)
        if pipeline_kind and execution_path_kind:
            increment_counter(
                "llm_obs_pipeline_total",
                labels={
                    "pipeline_kind": pipeline_kind,
                    "path_kind": execution_path_kind,
                    "provider": executed_provider or "unknown",
                },
            )

        transaction = db.begin_nested() if db.in_transaction() else db.begin()
        with transaction:
            log_entry = LlmCallLogModel(
                use_case=use_case,
                assembly_id=assembly_id,
                feature=feature,
                subfeature=subfeature,
                plan=plan,
                template_source=template_source,
                prompt_version_id=prompt_version_id,
                persona_id=persona_id,
                provider=provider,
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
                # AC 66.25
                pipeline_kind=pipeline_kind,
                execution_path_kind=execution_path_kind,
                fallback_kind=fallback_kind,
                requested_provider=requested_provider,
                resolved_provider=resolved_provider,
                executed_provider=executed_provider,
                context_compensation_status=context_compensation_status,
                max_output_tokens_source=max_output_tokens_source,
                max_output_tokens_final=max_output_tokens_final,
                # AC 66.33
                executed_provider_mode=executed_provider_mode,
                attempt_count=attempt_count,
                provider_error_code=provider_error_code,
                breaker_state=breaker_state,
                breaker_scope=breaker_scope,
                # Story 66.32
                active_snapshot_id=active_snapshot_id,
                active_snapshot_version=active_snapshot_version,
                manifest_entry_id=manifest_entry_id,
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
