"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies.auth import (
    AuthenticatedUser,
)
from app.api.v1.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.core.sensitive_data import Sink, classify_field, get_policy_action, sanitize_payload
from app.domain.llm.configuration.admin_models import (
    AdminUseCaseAudit,
    LlmPromptVersion,
    LlmUseCaseConfig,
    build_admin_use_case_audit,
)
from app.domain.llm.configuration.assemblies import (
    AssemblyRegistry,
    assemble_developer_prompt,
    resolve_assembly,
)
from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_use_case_contract,
)
from app.domain.llm.governance.feature_taxonomy import (
    normalize_feature,
    normalize_plan_scope,
    normalize_subfeature,
)
from app.domain.llm.governance.governance import get_prompt_governance_registry
from app.domain.llm.prompting.personas import compose_persona_block
from app.domain.llm.prompting.prompt_renderer import PromptRenderer
from app.domain.llm.runtime.composition import ContextQualityInjector, ProviderParameterMapper
from app.domain.llm.runtime.contracts import (
    GatewayResult,
    PromptRenderError,
)
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
)
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel
from app.infra.db.repositories.llm.prompting_repository import (
    get_active_prompt_version as repo_get_active_prompt_version,
)
from app.infra.db.repositories.llm.prompting_repository import (
    get_latest_active_release_snapshot,
    get_sample_payload,
)
from app.ops.llm.services import PromptRegistryV2
from app.services.llm_generation.anonymization_service import (
    LLMAnonymizationError,
    anonymize_text,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)
ADMIN_MANUAL_LLM_EXECUTE_SURFACE = "admin_catalog_manual_execute_sample"
ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER = "X-Admin-Manual-Llm-Execute"
ADMIN_MANUAL_EXECUTE_ROUTE_PATH = "/catalog/{manifest_entry_id}/execute-sample"
router = APIRouter(prefix="/v1/admin/llm", tags=["admin-llm"])
LEGACY_USE_CASE_KEYS_REMOVED: frozenset[str] = frozenset(
    {
        "daily_prediction",
        "horoscope_daily_free",
        "horoscope_daily_full",
        "chat",
        "chat_astrologer",
    }
)
AdminInspectionMode = Literal["assembly_preview", "runtime_preview", "live_execution"]
AdminSelectedComponentType = Literal[
    "domain_instructions",
    "use_case_overlay",
    "plan_overlay",
    "persona_overlay",
    "output_contract",
    "style_lexicon_rules",
    "error_handling_rules",
    "hard_policy",
]
AdminRuntimeArtifactType = Literal[
    "developer_prompt_assembled",
    "developer_prompt_after_persona",
    "developer_prompt_after_injectors",
    "system_prompt",
    "final_provider_payload",
]
from app.api.v1.schemas.routers.admin.llm.prompts import *


def _to_none_if_literal_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    if text == "None":
        return None
    return text


def _classify_admin_render_error_kind(
    inspection_mode: AdminInspectionMode,
    exc: PromptRenderError | None,
) -> str | None:
    """
    Classe l'erreur de rendu admin à partir des métadonnées stables de PromptRenderError
    (préféré aux sous-chaînes sur le message seul).
    """
    if exc is None:
        return None
    details = exc.details or {}
    if details.get("missing_variables"):
        return "execution_failure"
    msg_l = str(exc).lower()
    if details.get("placeholder") is not None:
        if "unauthorized" in msg_l:
            return "execution_failure"
        if "not resolved" in msg_l:
            if inspection_mode == "assembly_preview":
                return "static_preview_incomplete"
            return "execution_failure"
    if inspection_mode == "assembly_preview" and (
        "unauthorized" in msg_l or "missing required legacy" in msg_l or "legacy variables" in msg_l
    ):
        return "execution_failure"
    if inspection_mode == "assembly_preview":
        return "static_preview_incomplete"
    return "execution_failure"


def _catalog_sort_value(entry: AdminLlmCatalogEntry, sort_by: str) -> tuple[int, str]:
    raw = getattr(entry, sort_by, None)
    if raw is None:
        return (1, "")
    return (0, str(raw).lower())


def _to_manifest_entry(feature: str, subfeature: str | None, plan: str | None, locale: str) -> str:
    return f"{feature}:{subfeature}:{plan}:{locale}"


def _parse_manifest_entry_id(manifest_entry_id: str) -> tuple[str, str | None, str | None, str]:
    parts = manifest_entry_id.split(":")
    if len(parts) != 4:
        raise ValueError("manifest_entry_id must follow format feature:subfeature:plan:locale")
    feature, subfeature, plan, locale = parts
    return feature, _to_none_if_literal_none(subfeature), _to_none_if_literal_none(plan), locale


def _collect_catalog_facets(entries: list[AdminLlmCatalogEntry]) -> dict[str, list[str]]:
    def values_for(field: str) -> list[str]:
        values = {
            str(getattr(entry, field))
            for entry in entries
            if getattr(entry, field, None) is not None and str(getattr(entry, field)).strip() != ""
        }
        return sorted(values)

    return {
        "feature": values_for("feature"),
        "subfeature": values_for("subfeature"),
        "plan": values_for("plan"),
        "locale": values_for("locale"),
        "provider": values_for("provider"),
        "source_of_truth_status": values_for("source_of_truth_status"),
        "assembly_status": values_for("assembly_status"),
        "release_health_status": values_for("release_health_status"),
        "catalog_visibility_status": values_for("catalog_visibility_status"),
    }


def _resolve_output_schema_id_by_name(db: Session, schema_name: str | None) -> str | None:
    if not schema_name:
        return None
    stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == schema_name)
    schema = db.execute(stmt).scalar_one_or_none()
    return str(schema.id) if schema else None


def _build_canonical_admin_use_case_config(db: Session, key: str) -> LlmUseCaseConfig | None:
    contract = get_canonical_use_case_contract(key)
    if contract is None:
        return None
    active_prompt = PromptRegistryV2.get_active_prompt(db, key)
    return LlmUseCaseConfig(
        key=contract.key,
        display_name=contract.display_name,
        description=contract.description,
        input_schema=contract.input_schema,
        output_schema_id=_resolve_output_schema_id_by_name(db, contract.output_schema_name),
        persona_strategy=contract.persona_strategy,
        safety_profile=contract.safety_profile,
        required_prompt_placeholders=contract.required_prompt_placeholders,
        eval_fixtures_path=contract.eval_fixtures_path,
        eval_failure_threshold=contract.eval_failure_threshold,
        golden_set_path=contract.golden_set_path,
        active_prompt_version_id=active_prompt.id if active_prompt else None,
    )


def _ensure_admin_use_case_shadow_row(
    db: Session,
    config: LlmUseCaseConfig,
) -> LlmUseCaseConfigModel:
    """Maintient la ligne FK minimale requise pour les versions de prompt admin."""

    use_case = db.get(LlmUseCaseConfigModel, config.key)
    if use_case is None:
        use_case = LlmUseCaseConfigModel(
            key=config.key,
            display_name=config.display_name,
            description=config.description,
            required_prompt_placeholders=config.required_prompt_placeholders,
            eval_fixtures_path=config.eval_fixtures_path,
            eval_failure_threshold=config.eval_failure_threshold or 0.20,
            golden_set_path=config.golden_set_path,
        )
        db.add(use_case)
        db.flush()
        return use_case

    use_case.display_name = config.display_name
    use_case.description = config.description
    use_case.required_prompt_placeholders = config.required_prompt_placeholders
    use_case.eval_fixtures_path = config.eval_fixtures_path
    use_case.eval_failure_threshold = config.eval_failure_threshold or 0.20
    use_case.golden_set_path = config.golden_set_path
    db.flush()
    return use_case


def _legacy_removed_call_log_filter() -> Any:
    return and_(
        LlmCallLogModel.feature.is_(None),
        LlmCallLogModel.use_case.in_(tuple(LEGACY_USE_CASE_KEYS_REMOVED)),
    )


def _call_log_scope_filter(use_case: str) -> Any:
    if use_case == "legacy_removed":
        return _legacy_removed_call_log_filter()
    return LlmCallLogModel.feature == use_case


def _serialize_prompt_version(db: Session, version: LlmPromptVersionModel) -> LlmPromptVersion:
    del db
    return LlmPromptVersion.model_validate(version)


def _normalize_event_type(status: str | None) -> str:
    status_text = str(status or "").strip().lower()
    mapping = {
        "candidate": "created",
        "qualified": "validated",
        "activated": "activated",
        "monitoring": "monitoring",
        "degraded": "degraded",
        "rollback_recommended": "rollback_recommended",
        "rolled_back": "rolled_back",
    }
    return mapping.get(status_text, "backend_unmapped")


def _extract_proof_summaries(snapshot: LlmReleaseSnapshotModel) -> list[ProofSummary]:
    manifest = snapshot.manifest or {}
    targets = manifest.get("targets") or {}
    release_health = manifest.get("release_health") or {}
    history = release_health.get("history") or []
    known_manifest_entry_ids = set(str(entry_id) for entry_id in targets.keys())

    qualification_signal: dict[str, Any] | None = None
    golden_signal: dict[str, Any] | None = None
    smoke_signal: dict[str, Any] | None = None

    for event in history:
        if not isinstance(event, dict):
            continue
        signals = event.get("signals") or {}
        if not isinstance(signals, dict):
            continue
        if signals.get("qualification_verdict") is not None:
            qualification_signal = event
        if signals.get("golden_verdict") is not None:
            golden_signal = event
        if signals.get("active_snapshot_id") is not None:
            smoke_signal = event

    qualification_signals = (qualification_signal or {}).get("signals", {})
    golden_signals = (golden_signal or {}).get("signals", {})
    qualification_verdict = (
        str(qualification_signals.get("qualification_verdict")) if qualification_signal else None
    )
    golden_verdict = str(golden_signals.get("golden_verdict")) if golden_signal else None
    qualification_snapshot_id = (
        str(qualification_signals.get("active_snapshot_id"))
        if qualification_signals.get("active_snapshot_id")
        else None
    )
    golden_snapshot_id = (
        str(golden_signals.get("active_snapshot_id"))
        if golden_signals.get("active_snapshot_id")
        else None
    )
    qualification_manifest_entry_id = (
        str(qualification_signals.get("qualification_manifest_entry_id"))
        if qualification_signals.get("qualification_manifest_entry_id")
        else None
    )
    golden_manifest_entry_id = (
        str(golden_signals.get("golden_manifest_entry_id"))
        if golden_signals.get("golden_manifest_entry_id")
        else None
    )
    smoke_status = (
        str((smoke_signal or {}).get("signals", {}).get("status")) if smoke_signal else None
    )
    smoke_manifest_entry_id = (
        str((smoke_signal or {}).get("signals", {}).get("manifest_entry_id"))
        if smoke_signal and (smoke_signal.get("signals") or {}).get("manifest_entry_id")
        else None
    )
    qualification_correlated = (
        qualification_verdict is not None
        and qualification_snapshot_id == str(snapshot.id)
        and (
            qualification_manifest_entry_id is None
            or qualification_manifest_entry_id in known_manifest_entry_ids
        )
    )
    golden_correlated = (
        golden_verdict is not None
        and golden_snapshot_id == str(snapshot.id)
        and (
            golden_manifest_entry_id is None or golden_manifest_entry_id in known_manifest_entry_ids
        )
    )

    qualification = ProofSummary(
        proof_type="qualification",
        status="present" if qualification_verdict else "missing",
        verdict=qualification_verdict,
        generated_at=str((qualification_signal or {}).get("timestamp"))
        if qualification_signal
        else None,
        manifest_entry_id=qualification_manifest_entry_id,
        correlated=qualification_correlated,
    )
    golden = ProofSummary(
        proof_type="golden",
        status="present" if golden_verdict else "missing",
        verdict=golden_verdict,
        generated_at=str((golden_signal or {}).get("timestamp")) if golden_signal else None,
        manifest_entry_id=golden_manifest_entry_id,
        correlated=golden_correlated,
    )
    smoke_correlated = (
        smoke_manifest_entry_id is not None and smoke_manifest_entry_id in known_manifest_entry_ids
    )
    smoke = ProofSummary(
        proof_type="smoke",
        status=("present" if smoke_status else "missing"),
        verdict=smoke_status,
        generated_at=str((smoke_signal or {}).get("timestamp")) if smoke_signal else None,
        manifest_entry_id=smoke_manifest_entry_id,
        correlated=smoke_correlated,
    )
    readiness_status = "missing"
    readiness_verdict: str | None = None
    if (
        qualification.status == "present"
        and golden.status == "present"
        and smoke.status == "present"
    ):
        if qualification.verdict in {"go", "go-with-constraints"} and golden.verdict == "pass":
            if qualification_correlated and golden_correlated and smoke_correlated:
                readiness_verdict = "valid"
            else:
                readiness_verdict = "uncorrelated"
            readiness_status = "present"
        else:
            readiness_verdict = "invalid"
            readiness_status = "present"
    readiness = ProofSummary(
        proof_type="readiness",
        status=readiness_status,
        verdict=readiness_verdict,
        generated_at=smoke.generated_at or golden.generated_at or qualification.generated_at,
        manifest_entry_id=smoke.manifest_entry_id,
        correlated=qualification_correlated and golden_correlated and smoke_correlated,
    )

    return [qualification, golden, smoke, readiness]


def _build_snapshot_timeline_events(
    snapshot: LlmReleaseSnapshotModel,
) -> list[SnapshotTimelineItem]:
    manifest = snapshot.manifest or {}
    release_health = manifest.get("release_health") or {}
    history = release_health.get("history") or []
    proof_summaries = _extract_proof_summaries(snapshot)
    manifest_entry_count = len((manifest.get("targets") or {}).keys())
    current_status = str(snapshot.status)
    release_health_status = str(release_health.get("status") or snapshot.status)
    history_events = [event for event in history if isinstance(event, dict)]

    timeline_events: list[SnapshotTimelineItem] = []
    timeline_events.append(
        SnapshotTimelineItem(
            event_type="created",
            snapshot_id=str(snapshot.id),
            snapshot_version=snapshot.version,
            occurred_at=snapshot.created_at.isoformat(),
            current_status=current_status,
            release_health_status=release_health_status,
            status_history=history_events,
            reason="Snapshot created.",
            from_snapshot_id=None,
            to_snapshot_id=str(snapshot.id),
            manifest_entry_count=manifest_entry_count,
            proof_summaries=proof_summaries,
        )
    )
    if snapshot.validated_at:
        timeline_events.append(
            SnapshotTimelineItem(
                event_type="validated",
                snapshot_id=str(snapshot.id),
                snapshot_version=snapshot.version,
                occurred_at=snapshot.validated_at.isoformat(),
                current_status=current_status,
                release_health_status=release_health_status,
                status_history=history_events,
                reason="Snapshot validated.",
                from_snapshot_id=None,
                to_snapshot_id=str(snapshot.id),
                manifest_entry_count=manifest_entry_count,
                proof_summaries=proof_summaries,
            )
        )

    for history_event in history_events:
        status = str(history_event.get("status") or "")
        event_type = _normalize_event_type(status)
        signals = history_event.get("signals") or {}
        if not isinstance(signals, dict):
            signals = {}
        from_snapshot_id: str | None = None
        to_snapshot_id: str | None = str(snapshot.id)
        if event_type == "rolled_back":
            from_snapshot_id = str(snapshot.id)
            to_snapshot_id = (
                str(signals.get("restored_snapshot_id"))
                if signals.get("restored_snapshot_id")
                else str(snapshot.id)
            )
        timeline_events.append(
            SnapshotTimelineItem(
                event_type=event_type,  # type: ignore[arg-type]
                snapshot_id=str(snapshot.id),
                snapshot_version=snapshot.version,
                occurred_at=str(history_event.get("timestamp") or snapshot.created_at.isoformat()),
                current_status=current_status,
                release_health_status=release_health_status,
                status_history=history_events,
                reason=(
                    str(history_event.get("reason"))
                    if history_event.get("reason") is not None
                    else None
                ),
                from_snapshot_id=from_snapshot_id,
                to_snapshot_id=to_snapshot_id,
                manifest_entry_count=manifest_entry_count,
                proof_summaries=proof_summaries,
            )
        )

    return timeline_events


def _snapshot_diff_entries(
    *,
    from_snapshot: LlmReleaseSnapshotModel,
    to_snapshot: LlmReleaseSnapshotModel,
) -> list[SnapshotDiffEntry]:
    from_targets = (from_snapshot.manifest or {}).get("targets") or {}
    to_targets = (to_snapshot.manifest or {}).get("targets") or {}
    all_manifest_entry_ids = sorted(set(from_targets.keys()) | set(to_targets.keys()))
    entries: list[SnapshotDiffEntry] = []

    for manifest_entry_id in all_manifest_entry_ids:
        from_bundle = from_targets.get(manifest_entry_id) or {}
        to_bundle = to_targets.get(manifest_entry_id) or {}

        from_assembly = from_bundle.get("assembly") or {}
        to_assembly = to_bundle.get("assembly") or {}
        from_profile = from_bundle.get("profile") or {}
        to_profile = to_bundle.get("profile") or {}

        from_output_contract = (
            from_assembly.get("output_schema_id") if isinstance(from_assembly, dict) else None
        )
        to_output_contract = (
            to_assembly.get("output_schema_id") if isinstance(to_assembly, dict) else None
        )
        assembly_changed = from_assembly != to_assembly
        execution_profile_changed = from_profile != to_profile
        output_contract_changed = from_output_contract != to_output_contract

        if manifest_entry_id not in from_targets:
            category: Literal["added", "removed", "changed", "unchanged"] = "added"
        elif manifest_entry_id not in to_targets:
            category = "removed"
        elif assembly_changed or execution_profile_changed or output_contract_changed:
            category = "changed"
        else:
            category = "unchanged"

        entries.append(
            SnapshotDiffEntry(
                manifest_entry_id=str(manifest_entry_id),
                category=category,
                assembly_changed=assembly_changed,
                execution_profile_changed=execution_profile_changed,
                output_contract_changed=output_contract_changed,
                from_snapshot_id=str(from_snapshot.id),
                to_snapshot_id=str(to_snapshot.id),
            )
        )

    return entries


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    # AC13: Sanitize error details
    sanitized_details = sanitize_payload(details, Sink.ADMIN_API)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": sanitized_details,
                "request_id": request_id,
            }
        },
    )


def _admin_catalog_runtime_preview_blocking_reasons(view: AdminResolvedAssemblyView) -> list[str]:
    reasons: list[str] = []
    msgs = view.resolved_result.provider_messages
    render_error = msgs.get("render_error") if isinstance(msgs, dict) else None
    if render_error:
        reasons.append(f"render_error:{render_error}")
    for placeholder in view.resolved_result.placeholders:
        if placeholder.status in ("blocking_missing", "unknown"):
            reasons.append(f"placeholder:{placeholder.name}:{placeholder.status}")
    return reasons


def _derive_admin_runtime_use_case_key(assembly_model: PromptAssemblyConfigModel) -> str | None:
    """Expose le use case réellement exécuté quand le runtime diverge du template canonique."""
    canonical_use_case_key = (
        assembly_model.feature_template.use_case_key if assembly_model.feature_template else None
    )
    if not canonical_use_case_key:
        return None

    if (
        assembly_model.feature == "natal"
        and assembly_model.subfeature == "interpretation"
        and assembly_model.plan == "free"
    ):
        return "natal_long_free"

    return canonical_use_case_key


def _build_admin_runtime_use_case_audit(
    use_case_key: str | None,
    *,
    canonical_feature: str,
    canonical_subfeature: str | None,
    canonical_plan: str | None,
) -> AdminUseCaseAudit | None:
    return build_admin_use_case_audit(
        use_case_key,
        maintenance_surface="canonical_runtime",
        canonical_feature=canonical_feature,
        canonical_subfeature=canonical_subfeature,
        canonical_plan=canonical_plan,
    )


def _is_removed_legacy_use_case_key(use_case_key: str | None) -> bool:
    if not use_case_key:
        return False
    return use_case_key in LEGACY_USE_CASE_KEYS_REMOVED


def _get_active_prompt_version_for_use_case(
    db: Session, use_case_key: str | None
) -> LlmPromptVersionModel | None:
    if not use_case_key:
        return None
    return repo_get_active_prompt_version(db, use_case_key)


def _json_pretty_admin(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _build_admin_developer_message_bundle(
    *,
    main_prompt: str,
    persona_block: str | None,
    include_persona: bool,
) -> str:
    messages: list[str] = [f"[DEVELOPER MESSAGE 1 / main]\n{main_prompt}"]
    if include_persona and persona_block:
        messages.append(f"[DEVELOPER MESSAGE 2 / persona overlay]\n{persona_block}")
    return "\n\n".join(messages)


def _anonymize_for_admin_manual_execute(text: str, *, field: str) -> str:
    """Ne pas faire échouer la réponse opérateur si l'anonymisation est indisponible."""
    try:
        return anonymize_text(text)
    except LLMAnonymizationError as exc:
        logger.warning("admin manual execute: anonymization skipped for %s: %s", field, exc)
        return "[anonymization_unavailable]"


def _build_admin_manual_execute_response_payload(
    *,
    built: AdminResolvedAssemblyView,
    result: GatewayResult,
    manifest_entry_id: str,
    sample_payload_id: uuid.UUID,
    request_id: str,
    trace_id: str,
    use_case_key: str,
) -> AdminCatalogManualExecuteResponseData:
    """Construit le payload opérateur (prompt, params runtime, sorties, redaction)."""
    rendered = built.transformation_pipeline.rendered_prompt
    prompt_sent = _anonymize_for_admin_manual_execute(
        rendered if rendered else "", field="prompt_sent"
    )

    structured = result.structured_output
    structured_sanitized: dict[str, Any] | None = None
    if isinstance(structured, dict):
        structured_sanitized = sanitize_payload(structured, Sink.ADMIN_API)
    parseable = structured_sanitized is not None

    meta = result.meta
    runtime_params = sanitize_payload(
        {
            "translated_provider_params": meta.translated_provider_params or {},
            "reasoning_profile": meta.reasoning_profile,
            "verbosity_profile": meta.verbosity_profile,
            "output_mode": meta.output_mode,
            "tool_mode": meta.tool_mode,
            "max_output_tokens_source": meta.max_output_tokens_source,
            "model_override_active": meta.model_override_active,
            "prompt_version_id": meta.prompt_version_id,
            "output_schema_id": meta.output_schema_id,
            "schema_version": meta.schema_version,
        },
        Sink.ADMIN_API,
    )

    raw_out = _anonymize_for_admin_manual_execute(result.raw_output or "", field="raw_output")
    val_errors: list[str] | None = None
    if meta.validation_errors:
        val_errors = [
            _anonymize_for_admin_manual_execute(line, field="meta_validation_error")
            for line in meta.validation_errors
        ]

    return AdminCatalogManualExecuteResponseData(
        manifest_entry_id=manifest_entry_id,
        sample_payload_id=str(sample_payload_id),
        use_case_key=use_case_key,
        provider=meta.provider or "openai",
        model=meta.model,
        request_id=request_id,
        trace_id=trace_id,
        gateway_request_id=result.request_id,
        prompt_sent=prompt_sent,
        resolved_runtime_parameters=runtime_params,
        raw_output=raw_out,
        structured_output=structured_sanitized,
        structured_output_parseable=parseable,
        validation_status=meta.validation_status,
        execution_path=meta.execution_path,
        meta_validation_errors=val_errors,
        latency_ms=meta.latency_ms,
        admin_manual_execution=True,
        usage_input_tokens=result.usage.input_tokens,
        usage_output_tokens=result.usage.output_tokens,
    )


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: Any,
) -> None:
    from app.domain.audit.safe_details import to_safe_details

    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor.id,
            actor_role=actor.role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            status=status,
            details=to_safe_details(details),
        ),
    )


def _record_admin_manual_execution_audit(
    db: Session,
    *,
    request_id: str,
    actor: AuthenticatedUser,
    manifest_entry_id: str,
    sample_payload_id: uuid.UUID,
    status: Literal["success", "failed"],
    details: dict[str, Any],
) -> None:
    _record_audit_event(
        db,
        request_id=request_id,
        actor=actor,
        action="llm_catalog_execute_sample",
        target_type="llm_manifest_entry",
        target_id=manifest_entry_id,
        status=status,
        details={
            "execution_surface": ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
            "manifest_entry_id": manifest_entry_id,
            "sample_payload_id": str(sample_payload_id),
            **details,
        },
    )


def _build_admin_resolved_catalog_view(
    *,
    db: Session,
    manifest_entry_id: str,
    inspection_mode: AdminInspectionMode,
    sample_payload_id: uuid.UUID | None,
    request_id: str,
) -> AdminResolvedAssemblyView | JSONResponse:
    active_snapshot = get_latest_active_release_snapshot(db)
    manifest_bundle: dict[str, Any] | None = None
    if active_snapshot:
        manifest_targets = (active_snapshot.manifest or {}).get("targets") or {}
        manifest_bundle = manifest_targets.get(manifest_entry_id)

    assembly_data = (manifest_bundle or {}).get("assembly") or {}
    profile_data = (manifest_bundle or {}).get("profile") or {}

    assembly_model: PromptAssemblyConfigModel | None = None
    snapshot_profile_data: dict[str, Any] | None = None
    snapshot_resolution_error: str | None = None
    if manifest_bundle and isinstance(profile_data, dict) and profile_data:
        snapshot_profile_data = profile_data
    if manifest_bundle and not assembly_data:
        snapshot_resolution_error = "snapshot bundle missing assembly payload"
    if manifest_bundle and assembly_data and snapshot_resolution_error is None:
        try:
            registry = AssemblyRegistry(db)
            assembly_model = registry._reconstruct_config(assembly_data)
            # Some manifests may contain lightweight assembly payloads without transitive refs.
            if assembly_model.feature_template is None:
                raise ValueError("snapshot assembly bundle is incomplete")
            setattr(assembly_model, "_snapshot_bundle", manifest_bundle)
            if active_snapshot:
                setattr(assembly_model, "_active_snapshot_id", active_snapshot.id)
                setattr(assembly_model, "_active_snapshot_version", active_snapshot.version)
            setattr(assembly_model, "_manifest_entry_id", manifest_entry_id)
        except Exception as exc:
            assembly_model = None
            snapshot_resolution_error = str(exc)

    if manifest_bundle and assembly_model is None and snapshot_resolution_error is not None:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.SNAPSHOT_BUNDLE_UNUSABLE.value,
            message="active snapshot bundle is present but cannot be reconstructed safely",
            details={
                "manifest_entry_id": manifest_entry_id,
                "active_snapshot_id": str(active_snapshot.id) if active_snapshot else None,
                "active_snapshot_version": active_snapshot.version if active_snapshot else None,
                "snapshot_resolution_error": snapshot_resolution_error,
            },
        )

    if assembly_model is None:
        try:
            feature, subfeature, plan, locale = _parse_manifest_entry_id(manifest_entry_id)
        except ValueError as exc:
            return _error_response(
                status_code=422,
                request_id=request_id,
                code=AdminLlmErrorCode.INVALID_MANIFEST_ENTRY_ID.value,
                message=str(exc),
                details={"manifest_entry_id": manifest_entry_id},
            )

        assembly_model = db.execute(
            select(PromptAssemblyConfigModel)
            .where(PromptAssemblyConfigModel.feature == feature)
            .where(PromptAssemblyConfigModel.subfeature == subfeature)
            .where(PromptAssemblyConfigModel.plan == plan)
            .where(PromptAssemblyConfigModel.locale == locale)
            .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
            .options(
                selectinload(PromptAssemblyConfigModel.feature_template),
                selectinload(PromptAssemblyConfigModel.subfeature_template),
                selectinload(PromptAssemblyConfigModel.persona),
            )
        ).scalar_one_or_none()

    if assembly_model is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.MANIFEST_ENTRY_NOT_FOUND.value,
            message=f"manifest entry {manifest_entry_id} not found",
            details={"manifest_entry_id": manifest_entry_id},
        )
    source_of_truth_status = "active_snapshot" if manifest_bundle else "live_table_fallback"

    resolved = resolve_assembly(assembly_model, context_quality="full")
    # Base canonical prompt from assembly resolver (includes length budget policy).
    assembled_prompt = assemble_developer_prompt(resolved, assembly_model)

    (
        post_injectors_prompt,
        context_quality_instruction_injected,
        context_quality_handled_by_template,
    ) = ContextQualityInjector.inject(
        assembled_prompt, assembly_model.feature, resolved.context_quality
    )

    execution_profile_model = None
    if not snapshot_profile_data and assembly_model.execution_profile_ref:
        execution_profile_model = db.get(
            LlmExecutionProfileModel, assembly_model.execution_profile_ref
        )

    effective_profile_provider = (
        str(snapshot_profile_data.get("provider"))
        if snapshot_profile_data and snapshot_profile_data.get("provider")
        else execution_profile_model.provider
        if execution_profile_model
        else str(profile_data.get("provider") or "openai")
    )
    effective_profile_model = (
        str(snapshot_profile_data.get("model"))
        if snapshot_profile_data and snapshot_profile_data.get("model")
        else execution_profile_model.model
        if execution_profile_model
        else str(profile_data.get("model") or "unknown")
    )
    effective_reasoning_profile = (
        str(snapshot_profile_data.get("reasoning_profile"))
        if snapshot_profile_data and snapshot_profile_data.get("reasoning_profile")
        else execution_profile_model.reasoning_profile
        if execution_profile_model
        else None
    )
    effective_verbosity_profile = (
        str(snapshot_profile_data.get("verbosity_profile"))
        if snapshot_profile_data and snapshot_profile_data.get("verbosity_profile")
        else execution_profile_model.verbosity_profile
        if execution_profile_model
        else None
    )
    effective_output_mode = (
        str(snapshot_profile_data.get("output_mode"))
        if snapshot_profile_data and snapshot_profile_data.get("output_mode")
        else execution_profile_model.output_mode
        if execution_profile_model
        else "free_text"
    )
    effective_tool_mode = (
        str(snapshot_profile_data.get("tool_mode"))
        if snapshot_profile_data and snapshot_profile_data.get("tool_mode")
        else execution_profile_model.tool_mode
        if execution_profile_model
        else "none"
    )
    effective_profile_max_tokens = (
        int(snapshot_profile_data.get("max_output_tokens"))
        if snapshot_profile_data and snapshot_profile_data.get("max_output_tokens") is not None
        else execution_profile_model.max_output_tokens
        if execution_profile_model
        else None
    )
    effective_profile_timeout = (
        int(snapshot_profile_data.get("timeout_seconds"))
        if snapshot_profile_data and snapshot_profile_data.get("timeout_seconds") is not None
        else execution_profile_model.timeout_seconds
        if execution_profile_model
        else None
    )

    verbosity_instruction = ""
    translated_provider_params: dict[str, Any] = {}
    if effective_verbosity_profile:
        verbosity_instruction, recommended_tokens = (
            ProviderParameterMapper.resolve_verbosity_instruction(effective_verbosity_profile)
        )
    else:
        recommended_tokens = None
    if effective_reasoning_profile and effective_verbosity_profile:
        try:
            translated_provider_params = ProviderParameterMapper.map(
                provider=effective_profile_provider,
                reasoning_profile=effective_reasoning_profile,
                verbosity_profile=effective_verbosity_profile,
                output_mode=effective_output_mode,
                tool_mode=effective_tool_mode,
            )
        except Exception:
            translated_provider_params = {}
    if verbosity_instruction:
        post_injectors_prompt = (
            f"{post_injectors_prompt}\n\n[CONSIGNE DE VERBOSITÉ] {verbosity_instruction}"
        )

    # No fake runtime values: keep deterministic preview faithful to governance state.
    render_variables: dict[str, Any] = {
        "locale": assembly_model.locale,
        "context_quality": resolved.context_quality,
        "use_case": assembly_model.feature_template.use_case_key,
    }
    render_variable_sources: dict[str, str] = {
        "locale": "runtime_context",
        "context_quality": "runtime_context",
        "use_case": "runtime_context",
    }
    if sample_payload_id is not None:
        if inspection_mode != "runtime_preview":
            return _error_response(
                status_code=422,
                request_id=request_id,
                code=AdminLlmErrorCode.SAMPLE_PAYLOAD_RUNTIME_PREVIEW_ONLY.value,
                message="sample_payload_id is only supported in runtime_preview mode",
                details={
                    "sample_payload_id": str(sample_payload_id),
                    "inspection_mode": inspection_mode,
                },
            )
        sample_payload = get_sample_payload(db, sample_payload_id)
        if sample_payload is None:
            return _error_response(
                status_code=404,
                request_id=request_id,
                code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NOT_FOUND.value,
                message=f"sample payload {sample_payload_id} not found",
                details={"sample_payload_id": str(sample_payload_id)},
            )
        if not sample_payload.is_active:
            return _error_response(
                status_code=422,
                request_id=request_id,
                code=AdminLlmErrorCode.SAMPLE_PAYLOAD_INACTIVE.value,
                message="sample payload is inactive and cannot be used for runtime preview",
                details={"sample_payload_id": str(sample_payload_id)},
            )
        sample_feature = normalize_feature(sample_payload.feature)
        sample_subfeature = normalize_subfeature(sample_feature, sample_payload.subfeature) or ""
        sample_plan = normalize_plan_scope(sample_payload.plan)
        target_feature = normalize_feature(assembly_model.feature)
        target_subfeature = (
            normalize_subfeature(
                target_feature,
                assembly_model.subfeature,
            )
            or ""
        )
        target_plan = normalize_plan_scope(assembly_model.plan)
        if (
            sample_feature != target_feature
            or sample_subfeature != target_subfeature
            or sample_plan != target_plan
            or sample_payload.locale != assembly_model.locale
        ):
            return _error_response(
                status_code=422,
                request_id=request_id,
                code=AdminLlmErrorCode.SAMPLE_PAYLOAD_TARGET_MISMATCH.value,
                message=("sample payload canonical scope mismatch with requested manifest entry"),
                details={
                    "sample_payload_id": str(sample_payload_id),
                    "sample_feature": sample_feature,
                    "sample_subfeature": sample_subfeature,
                    "sample_plan": sample_plan,
                    "sample_locale": sample_payload.locale,
                    "target_feature": target_feature,
                    "target_subfeature": target_subfeature,
                    "target_plan": target_plan,
                    "target_locale": assembly_model.locale,
                },
            )
        if not isinstance(sample_payload.payload_json, dict):
            return _error_response(
                status_code=422,
                request_id=request_id,
                code=AdminLlmErrorCode.INVALID_SAMPLE_PAYLOAD.value,
                message="sample payload payload_json must be a JSON object",
                details={"sample_payload_id": str(sample_payload_id)},
            )
        for key, value in sample_payload.payload_json.items():
            if key not in render_variables:
                render_variables[key] = value
                render_variable_sources[key] = "sample_payload"

    render_error: str | None = None
    render_exc: PromptRenderError | None = None
    try:
        rendered_prompt = PromptRenderer.render(
            post_injectors_prompt,
            render_variables,
            feature=assembly_model.feature,
        )
    except PromptRenderError as exc:
        # Keep detail endpoint inspectable on blocking placeholders.
        rendered_prompt = post_injectors_prompt
        render_error = str(exc)
        render_exc = exc

    reg = get_prompt_governance_registry()
    placeholder_defs = {
        item.name: item for item in reg.get_placeholder_defs(assembly_model.feature)
    }
    placeholders: list[ResolvedPlaceholderView] = []
    for placeholder_name in PromptRenderer.extract_placeholders(post_injectors_prompt):
        placeholder_def = placeholder_defs.get(placeholder_name)
        classification = placeholder_def.classification if placeholder_def else None
        safe_to_display = (
            get_policy_action(Sink.ADMIN_API, classify_field(placeholder_name)).value == "allowed"
        )
        if placeholder_name in render_variables and render_variables[placeholder_name] is not None:
            sanitized_value = sanitize_payload(
                {"value": render_variables[placeholder_name]}, Sink.ADMIN_API
            )
            resolution_source = render_variable_sources.get(placeholder_name, "runtime_context")
            placeholders.append(
                ResolvedPlaceholderView(
                    name=placeholder_name,
                    status="resolved",
                    classification=classification,
                    resolution_source=resolution_source,
                    safe_to_display=safe_to_display,
                    value_preview=(
                        str(sanitized_value.get("value"))[:120]
                        if safe_to_display and sanitized_value.get("value") is not None
                        else None
                    ),
                )
            )
            continue

        if placeholder_def and placeholder_def.classification == "optional_with_fallback":
            placeholders.append(
                ResolvedPlaceholderView(
                    name=placeholder_name,
                    status="fallback_used",
                    classification=classification,
                    resolution_source="fallback",
                    reason="fallback_from_registry",
                    safe_to_display=safe_to_display,
                    value_preview=(placeholder_def.fallback or "")[:120]
                    if safe_to_display
                    else None,
                )
            )
        elif placeholder_def and placeholder_def.classification == "optional":
            placeholders.append(
                ResolvedPlaceholderView(
                    name=placeholder_name,
                    status="optional_missing",
                    classification=classification,
                    resolution_source="missing_optional",
                    reason="optional_placeholder_missing",
                    safe_to_display=safe_to_display,
                )
            )
        elif placeholder_def and placeholder_def.classification == "required":
            if inspection_mode == "assembly_preview":
                placeholders.append(
                    ResolvedPlaceholderView(
                        name=placeholder_name,
                        status="expected_missing_in_preview",
                        classification=classification,
                        resolution_source="static_preview_gap",
                        reason="expected_at_runtime_not_in_static_preview",
                        safe_to_display=safe_to_display,
                    )
                )
            else:
                placeholders.append(
                    ResolvedPlaceholderView(
                        name=placeholder_name,
                        status="blocking_missing",
                        classification=classification,
                        resolution_source="missing_required",
                        reason="required_placeholder_missing",
                        safe_to_display=safe_to_display,
                    )
                )
        else:
            # Hors registre : `unknown` en assembly_preview ; runtime_preview et live_execution
            # alignés (bloquant), comme documenté pour l’inspection live.
            if inspection_mode == "assembly_preview":
                placeholders.append(
                    ResolvedPlaceholderView(
                        name=placeholder_name,
                        status="unknown",
                        classification=classification,
                        resolution_source="unknown",
                        reason=None,
                        safe_to_display=safe_to_display,
                    )
                )
            else:
                placeholders.append(
                    ResolvedPlaceholderView(
                        name=placeholder_name,
                        status="blocking_missing",
                        classification=classification,
                        resolution_source="missing_required_untyped",
                        reason="required_placeholder_missing_untyped",
                        safe_to_display=safe_to_display,
                    )
                )

    # Keep execution parameters aligned with canonical gateway arbitration.
    if resolved.length_budget and resolved.length_budget.global_max_tokens is not None:
        final_max_output_tokens = resolved.length_budget.global_max_tokens
        max_output_tokens_source = "length_budget_global"
    elif effective_profile_max_tokens is not None:
        final_max_output_tokens = effective_profile_max_tokens
        max_output_tokens_source = "execution_profile"
    elif recommended_tokens is not None:
        final_max_output_tokens = recommended_tokens
        max_output_tokens_source = "verbosity_fallback"
    else:
        final_max_output_tokens = 2048
        max_output_tokens_source = "default"
    final_timeout_seconds = (
        effective_profile_timeout if effective_profile_timeout is not None else 30
    )

    render_error_kind = _classify_admin_render_error_kind(inspection_mode, render_exc)

    execution_profile_view = {
        "id": (
            str(snapshot_profile_data.get("id"))
            if snapshot_profile_data and snapshot_profile_data.get("id")
            else str(execution_profile_model.id)
            if execution_profile_model
            else None
        ),
        "name": (
            str(snapshot_profile_data.get("name"))
            if snapshot_profile_data and snapshot_profile_data.get("name")
            else execution_profile_model.name
            if execution_profile_model
            else None
        ),
        "provider": effective_profile_provider,
        "model": effective_profile_model,
        "reasoning": effective_reasoning_profile,
        "verbosity": effective_verbosity_profile,
        "provider_params": sanitize_payload(
            {
                "temperature": translated_provider_params.get("temperature"),
                "max_output_tokens_final": final_max_output_tokens,
                "timeout_seconds": final_timeout_seconds,
                "max_output_tokens_source": max_output_tokens_source,
                **translated_provider_params,
            },
            Sink.ADMIN_API,
        ),
    }

    effective_use_case_key = _derive_admin_runtime_use_case_key(assembly_model)
    active_prompt_version = _get_active_prompt_version_for_use_case(
        db, effective_use_case_key or assembly_model.feature_template.use_case_key
    )
    persona_block_content = resolved.persona_block
    if not persona_block_content and assembly_model.persona is not None:
        persona_block_content = compose_persona_block(assembly_model.persona)
    has_effective_persona_overlay = bool(persona_block_content)

    provider_messages = [
        {
            "role": "system",
            "source": "hard_policy",
            "content": resolved.policy_layer_content,
        },
        {
            "role": "developer",
            "source": "assembled_after_injectors",
            "content": rendered_prompt,
        },
    ]
    if persona_block_content:
        provider_messages.append(
            {
                "role": "developer",
                "source": "persona_overlay",
                "content": persona_block_content,
            }
        )
    final_provider_payload = {
        "messages": provider_messages,
        "provider": effective_profile_provider,
        "model": effective_profile_model,
        "provider_params": execution_profile_view["provider_params"],
        "render_error": render_error,
        "inspection_mode": inspection_mode,
    }
    selected_components: list[AdminSelectedComponentView] = [
        AdminSelectedComponentView(
            key="domain_instructions",
            component_type="domain_instructions",
            title="Instructions métier",
            content=resolved.feature_template_prompt,
            summary="Bloc source principal résolu depuis le feature template.",
            ref=str(assembly_model.feature_template_ref),
            source_label="feature_template",
            impact_status="active",
            meta={
                "feature": assembly_model.feature,
                "template_ref": str(assembly_model.feature_template_ref),
            },
        )
    ]
    if effective_use_case_key:
        selected_components.append(
            AdminSelectedComponentView(
                key="use_case_overlay",
                component_type="use_case_overlay",
                title="Use case overlay",
                content=(
                    active_prompt_version.developer_prompt
                    if active_prompt_version
                    else resolved.feature_template_prompt
                ),
                summary=(
                    "Surcharge éditoriale spécifique au use case runtime actif."
                    if active_prompt_version
                    else (
                        "Aucun prompt publié distinct n'est trouvé pour ce use case runtime; "
                        "la couche affichée reprend le bloc éditorial actuellement observable."
                    )
                ),
                ref=str(active_prompt_version.id) if active_prompt_version else None,
                source_label=(
                    active_prompt_version.use_case_key
                    if active_prompt_version
                    else effective_use_case_key
                ),
                version_label=(
                    active_prompt_version.published_at.isoformat()
                    if active_prompt_version and active_prompt_version.published_at
                    else (
                        active_prompt_version.created_at.isoformat()
                        if active_prompt_version
                        else None
                    )
                ),
                impact_status="active",
                editable_use_case_key=effective_use_case_key,
                meta={
                    "use_case_key": effective_use_case_key,
                    "status": (
                        str(active_prompt_version.status) if active_prompt_version else "fallback"
                    ),
                    "model": (
                        getattr(active_prompt_version, "model", None)
                        if active_prompt_version
                        else None
                    ),
                    "fallback_to_feature_template": not bool(active_prompt_version),
                },
            )
        )
    if assembly_model.plan and (resolved.plan_rules_content or assembly_model.plan_rules_ref):
        selected_components.append(
            AdminSelectedComponentView(
                key="plan_overlay",
                component_type="plan_overlay",
                title="Plan overlay",
                content=resolved.plan_rules_content,
                summary=(
                    "Aucun prompt publié distinct n'est trouvé pour cette formule; "
                    "la couche affichée "
                    "reflète uniquement les règles d'assembly actuellement observables."
                ),
                ref=assembly_model.plan_rules_ref,
                source_label="assembly_plan_rules",
                impact_status="active" if resolved.plan_rules_content else "absent",
                meta={"plan": assembly_model.plan},
            )
        )
    elif resolved.plan_rules_content:
        selected_components.append(
            AdminSelectedComponentView(
                key="plan_overlay",
                component_type="plan_overlay",
                title="Plan overlay",
                content=resolved.plan_rules_content,
                summary="Règles de formule injectées dans l'assembly actif.",
                ref=assembly_model.plan_rules_ref,
                source_label="assembly_plan_rules",
                impact_status="active",
                meta={"plan": assembly_model.plan},
            )
        )
    selected_components.append(
        AdminSelectedComponentView(
            key="output_contract",
            component_type="output_contract",
            title="Output contract",
            content=None,
            summary=(
                "Contrat de sortie résolu pour ce contexte. Référence visible, "
                "texte non dupliqué dans l'admin."
            ),
            ref=str(assembly_model.output_schema_id)
            if assembly_model.output_schema_id is not None
            else None,
            source_label="output_schema",
            impact_status="reference_only",
            meta={
                "output_schema_id": str(assembly_model.output_schema_id)
                if assembly_model.output_schema_id is not None
                else None
            },
        )
    )
    if persona_block_content:
        selected_components.append(
            AdminSelectedComponentView(
                key="persona_overlay",
                component_type="persona_overlay",
                title="Persona overlay",
                content=persona_block_content,
                summary="Persona résolue, injectée comme message developer séparé.",
                ref=str(assembly_model.persona_ref) if assembly_model.persona_ref else None,
                source_label=assembly_model.persona.name if assembly_model.persona else None,
                version_label=(
                    str(assembly_model.persona.updated_at) if assembly_model.persona else None
                ),
                merge_mode="separate_developer_message",
                impact_status="active",
                meta={
                    "persona_id": (
                        str(assembly_model.persona_ref) if assembly_model.persona_ref else None
                    ),
                    "persona_name": assembly_model.persona.name if assembly_model.persona else None,
                },
            )
        )
    selected_components.append(
        AdminSelectedComponentView(
            key="hard_policy",
            component_type="hard_policy",
            title="Hard policy",
            content=resolved.policy_layer_content,
            summary="Politique stricte envoyée au provider en message system.",
            ref="astrology",
            source_label="system_prompt",
            merge_mode="system_message",
            impact_status="active",
            meta={"safety_profile": "astrology"},
        )
    )
    runtime_artifacts: list[AdminRuntimeArtifactView] = [
        AdminRuntimeArtifactView(
            key="developer_prompt_assembled",
            artifact_type="developer_prompt_assembled",
            title="Developer prompt assembled",
            content=assembled_prompt,
            summary="Premier artefact textuel après assemblage des couches source.",
            change_status="changed",
            delta_note="Compose les instructions métier et la surcharge éditoriale active.",
            injection_point="developer",
        )
    ]
    if persona_block_content:
        runtime_artifacts.append(
            AdminRuntimeArtifactView(
                key="developer_prompt_after_persona",
                artifact_type="developer_prompt_after_persona",
                title="Developer prompt after persona",
                content=_build_admin_developer_message_bundle(
                    main_prompt=assembled_prompt,
                    persona_block=persona_block_content,
                    include_persona=True,
                ),
                summary="Vue opératoire des messages developer après ajout de la persona.",
                change_status="changed",
                delta_note=(
                    "La persona n'est pas fusionnée dans le texte principal; "
                    "elle part comme second message developer."
                ),
                injection_point="developer",
            )
        )
    runtime_artifacts.append(
        AdminRuntimeArtifactView(
            key="developer_prompt_after_injectors",
            artifact_type="developer_prompt_after_injectors",
            title="Developer prompt after injectors",
            content=_build_admin_developer_message_bundle(
                main_prompt=post_injectors_prompt,
                persona_block=persona_block_content,
                include_persona=bool(persona_block_content),
            ),
            summary=(
                "État developer après compensation context_quality, budget et injecteurs runtime."
            ),
            change_status=(
                "unchanged"
                if post_injectors_prompt.strip() == assembled_prompt.strip()
                else "changed"
            ),
            delta_note=(
                "Aucun delta textuel observable après injecteurs."
                if post_injectors_prompt.strip() == assembled_prompt.strip()
                else "Les injecteurs runtime modifient le message developer principal."
            ),
            injection_point="developer",
        )
    )
    runtime_artifacts.append(
        AdminRuntimeArtifactView(
            key="system_prompt",
            artifact_type="system_prompt",
            title="System prompt(s)",
            content=resolved.policy_layer_content,
            summary="Message system réellement préparé pour le provider.",
            change_status="changed",
            delta_note="La hard policy est envoyée séparément du developer prompt.",
            injection_point="system",
        )
    )
    runtime_artifacts.append(
        AdminRuntimeArtifactView(
            key="final_provider_payload",
            artifact_type="final_provider_payload",
            title="Final provider payload",
            content=_json_pretty_admin(final_provider_payload),
            summary="Payload inspectable réellement prêt pour l'appel provider.",
            change_status="changed",
            delta_note="Agrège system message, messages developer et paramètres provider traduits.",
            injection_point="provider",
        )
    )
    canonical_use_case_key = (
        assembly_model.feature_template.use_case_key if assembly_model.feature_template else None
    )
    selected_use_case_key = effective_use_case_key or canonical_use_case_key
    data = AdminResolvedAssemblyView(
        manifest_entry_id=manifest_entry_id,
        feature=assembly_model.feature,
        subfeature=assembly_model.subfeature,
        plan=assembly_model.plan,
        locale=assembly_model.locale,
        use_case_key=selected_use_case_key,
        canonical_use_case_key=canonical_use_case_key,
        runtime_use_case_key=effective_use_case_key,
        use_case_audit=_build_admin_runtime_use_case_audit(
            selected_use_case_key,
            canonical_feature=assembly_model.feature,
            canonical_subfeature=assembly_model.subfeature,
            canonical_plan=assembly_model.plan,
        ),
        runtime_use_case_audit=_build_admin_runtime_use_case_audit(
            effective_use_case_key,
            canonical_feature=assembly_model.feature,
            canonical_subfeature=assembly_model.subfeature,
            canonical_plan=assembly_model.plan,
        ),
        context_quality=resolved.context_quality,
        assembly_id=str(assembly_model.id),
        inspection_mode=inspection_mode,
        source_of_truth_status=source_of_truth_status,
        active_snapshot_id=str(active_snapshot.id) if active_snapshot else None,
        active_snapshot_version=active_snapshot.version if active_snapshot else None,
        activation=AdminResolvedActivationView(
            manifest_entry_id=manifest_entry_id,
            feature=assembly_model.feature,
            subfeature=assembly_model.subfeature,
            plan=assembly_model.plan,
            locale=assembly_model.locale,
            active_snapshot_id=str(active_snapshot.id) if active_snapshot else None,
            active_snapshot_version=active_snapshot.version if active_snapshot else None,
            execution_profile=execution_profile_view["name"] or execution_profile_view["id"],
            provider_target=f"{effective_profile_provider} / {effective_profile_model}",
            policy_family="astrology",
            output_schema=(
                str(assembly_model.output_schema_id)
                if assembly_model.output_schema_id is not None
                else None
            ),
            injector_set=[
                "context_quality_injector",
                "length_budget_injector" if resolved.length_budget else "length_budget_inactive",
                "verbosity_instruction" if verbosity_instruction else "verbosity_inactive",
            ],
            persona_policy="enabled" if has_effective_persona_overlay else "none",
        ),
        selected_components=selected_components,
        runtime_artifacts=runtime_artifacts,
        composition_sources=ResolvedCompositionSources(
            feature_template={
                "id": str(assembly_model.feature_template_ref),
                "content": resolved.feature_template_prompt,
            },
            subfeature_template=(
                {
                    "id": str(assembly_model.subfeature_template_ref),
                    "content": resolved.subfeature_template_prompt,
                }
                if resolved.subfeature_template_prompt
                else None
            ),
            plan_rules=(
                {"ref": assembly_model.plan_rules_ref, "content": resolved.plan_rules_content}
                if resolved.plan_rules_content
                else None
            ),
            persona_block=(
                {
                    "id": str(assembly_model.persona_ref),
                    "name": assembly_model.persona.name if assembly_model.persona else None,
                    "content": resolved.persona_block,
                }
                if resolved.persona_block
                else None
            ),
            hard_policy={
                "safety_profile": "astrology",
                "content": resolved.policy_layer_content,
            },
            execution_profile=execution_profile_view,
        ),
        transformation_pipeline=ResolvedTransformationPipeline(
            assembled_prompt=assembled_prompt,
            post_injectors_prompt=post_injectors_prompt,
            rendered_prompt=rendered_prompt,
        ),
        resolved_result=ResolvedResultView(
            provider_messages={
                "system_hard_policy": resolved.policy_layer_content,
                "developer_content_rendered": rendered_prompt,
                "persona_block": persona_block_content,
                "execution_parameters": execution_profile_view["provider_params"],
                "provider_payload_messages": provider_messages,
                "render_error": render_error,
                "render_error_kind": render_error_kind,
            },
            placeholders=placeholders,
            context_quality_handled_by_template=context_quality_handled_by_template,
            context_quality_instruction_injected=context_quality_instruction_injected,
            context_compensation_status=(
                "handled_by_template"
                if context_quality_handled_by_template
                else "injector_applied"
                if context_quality_instruction_injected
                else "not_needed"
            ),
            source_of_truth_status=source_of_truth_status,
            active_snapshot_id=str(active_snapshot.id) if active_snapshot else None,
            active_snapshot_version=active_snapshot.version if active_snapshot else None,
            manifest_entry_id=manifest_entry_id,
        ),
    )

    return data
