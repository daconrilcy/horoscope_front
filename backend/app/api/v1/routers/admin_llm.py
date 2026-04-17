from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Literal, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
)
from app.core.request_id import resolve_request_id
from app.core.sensitive_data import Sink, classify_field, get_policy_action, sanitize_payload
from app.infra.db.models.billing import UserSubscriptionModel
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.models.llm_release import LlmActiveReleaseModel, LlmReleaseSnapshotModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.llm_orchestration.admin_models import (
    LlmOutputSchema,
    LlmPersona,
    LlmPersonaCreate,
    LlmPersonaUpdate,
    LlmPromptVersion,
    LlmPromptVersionCreate,
    LlmUseCaseConfig,
)
from app.llm_orchestration.models import PromptRenderError
from app.llm_orchestration.persona_boundary import (
    PersonaBoundaryViolation,
    validate_persona_block,
)
from app.llm_orchestration.policies.hard_policy import get_hard_policy
from app.llm_orchestration.prompt_governance_registry import get_prompt_governance_registry
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import (
    assemble_developer_prompt,
    resolve_assembly,
)
from app.llm_orchestration.services.context_quality_injector import ContextQualityInjector
from app.llm_orchestration.services.eval_harness import run_eval
from app.llm_orchestration.services.observability_service import purge_expired_logs
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
from app.llm_orchestration.services.prompt_renderer import PromptRenderer
from app.llm_orchestration.services.provider_parameter_mapper import ProviderParameterMapper
from app.llm_orchestration.services.replay_service import replay
from app.services.audit_service import AuditEventCreatePayload, AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/llm", tags=["admin-llm"])


class ResponseMeta(BaseModel):
    request_id: str
    warnings: List[str] = Field(default_factory=list)
    boundary_violations: List[PersonaBoundaryViolation] = Field(default_factory=list)


class LlmUseCaseListResponse(BaseModel):
    data: List[LlmUseCaseConfig]
    meta: ResponseMeta


class LlmUseCaseContract(LlmUseCaseConfig):
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)


class LlmUseCaseContractResponse(BaseModel):
    data: LlmUseCaseContract
    meta: ResponseMeta


class LlmPersonaListResponse(BaseModel):
    data: List[LlmPersona]
    meta: ResponseMeta


class LlmPersonaApiResponse(BaseModel):
    data: LlmPersona
    meta: ResponseMeta


class LlmPersonaDetail(BaseModel):
    persona: LlmPersona
    use_cases: list[str]
    affected_users_count: int


class LlmPersonaDetailResponse(BaseModel):
    data: LlmPersonaDetail
    meta: ResponseMeta


class LlmOutputSchemaListResponse(BaseModel):
    data: List[LlmOutputSchema]
    meta: ResponseMeta


class LlmOutputSchemaApiResponse(BaseModel):
    data: LlmOutputSchema
    meta: ResponseMeta


class UseCaseUpdatePayload(BaseModel):
    persona_id: Optional[str] = None
    allowed_persona_ids: Optional[List[str]] = None
    persona_strategy: Optional[str] = None
    safety_profile: Optional[str] = None
    output_schema_id: Optional[str] = None
    fallback_use_case_key: Optional[str] = None
    eval_fixtures_path: Optional[str] = None
    eval_failure_threshold: Optional[float] = None
    golden_set_path: Optional[str] = None


class PersonaAssociationPayload(BaseModel):
    persona_id: Optional[str] = None


class LlmPromptHistoryResponse(BaseModel):
    data: List[LlmPromptVersion]
    meta: ResponseMeta


class LlmPromptApiResponse(BaseModel):
    data: LlmPromptVersion
    meta: ResponseMeta


class LlmPromptPublishResponse(BaseModel):
    data: LlmPromptVersion
    meta: dict  # includes eval_report


class RollbackPromptPayload(BaseModel):
    target_version_id: uuid.UUID | None = None


class LlmCallLog(BaseModel):
    id: uuid.UUID
    use_case: str
    prompt_version_id: Optional[uuid.UUID]
    persona_id: Optional[uuid.UUID]
    model: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd_estimated: float
    validation_status: str
    repair_attempted: bool
    fallback_triggered: bool
    request_id: str
    trace_id: str
    environment: str
    timestamp: datetime
    evidence_warnings_count: int


class LlmCallLogListResponse(BaseModel):
    data: List[LlmCallLog]
    meta: dict


class ReplayPayload(BaseModel):
    request_id: str
    prompt_version_id: str


class LlmDashboardMetrics(BaseModel):
    use_case: str
    request_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    validation_status_distribution: dict[str, float]  # % valid, repair, etc.
    repair_rate: float
    fallback_rate: float
    avg_tokens_per_request: float
    evidence_warning_rate: float


class LlmDashboardResponse(BaseModel):
    data: List[LlmDashboardMetrics]
    meta: ResponseMeta


class AdminLlmCatalogEntry(BaseModel):
    manifest_entry_id: str
    feature: str
    subfeature: str | None = None
    plan: str | None = None
    locale: str | None = None
    assembly_id: str | None = None
    assembly_status: str
    execution_profile_id: str | None = None
    execution_profile_ref: str | None = None
    output_contract_ref: str | None = None
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    provider: str | None = None
    model: str | None = None
    source_of_truth_status: str
    release_health_status: str
    catalog_visibility_status: str
    runtime_signal_status: str
    execution_path_kind: str | None = None
    context_compensation_status: str | None = None
    max_output_tokens_source: str | None = None


class AdminLlmCatalogResponse(BaseModel):
    data: List[AdminLlmCatalogEntry]
    meta: dict[str, Any]


class ResolvedCompositionSources(BaseModel):
    feature_template: dict[str, Any]
    subfeature_template: dict[str, Any] | None = None
    plan_rules: dict[str, Any] | None = None
    persona_block: dict[str, Any] | None = None
    hard_policy: dict[str, Any]
    execution_profile: dict[str, Any]


class ResolvedTransformationPipeline(BaseModel):
    assembled_prompt: str
    post_injectors_prompt: str
    rendered_prompt: str


class ResolvedPlaceholderView(BaseModel):
    name: str
    status: Literal[
        "resolved",
        "optional_missing",
        "fallback_used",
        "blocking_missing",
        "expected_missing_in_preview",
        "unknown",
    ]
    classification: str | None = None
    resolution_source: str | None = None
    reason: str | None = None
    safe_to_display: bool = False
    value_preview: str | None = None


class ResolvedResultView(BaseModel):
    provider_messages: dict[str, Any]
    placeholders: list[ResolvedPlaceholderView]
    context_quality_handled_by_template: bool
    context_quality_instruction_injected: bool
    context_compensation_status: str
    source_of_truth_status: str
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    manifest_entry_id: str


AdminInspectionMode = Literal["assembly_preview", "runtime_preview", "live_execution"]


class AdminResolvedAssemblyView(BaseModel):
    manifest_entry_id: str
    feature: str
    subfeature: str | None = None
    plan: str | None = None
    locale: str | None = None
    assembly_id: str | None = None
    inspection_mode: AdminInspectionMode
    source_of_truth_status: str
    active_snapshot_id: str | None = None
    active_snapshot_version: str | None = None
    composition_sources: ResolvedCompositionSources
    transformation_pipeline: ResolvedTransformationPipeline
    resolved_result: ResolvedResultView


class AdminResolvedAssemblyResponse(BaseModel):
    data: AdminResolvedAssemblyView
    meta: ResponseMeta


class ProofSummary(BaseModel):
    proof_type: Literal["qualification", "golden", "smoke", "readiness"]
    status: str
    verdict: str | None = None
    generated_at: str | None = None
    manifest_entry_id: str | None = None
    correlated: bool = False


class SnapshotTimelineItem(BaseModel):
    event_type: Literal[
        "created",
        "validated",
        "activated",
        "monitoring",
        "degraded",
        "rollback_recommended",
        "rolled_back",
        "backend_unmapped",
    ]
    snapshot_id: str
    snapshot_version: str
    occurred_at: str
    current_status: str
    release_health_status: str
    status_history: list[dict[str, Any]] = Field(default_factory=list)
    reason: str | None = None
    from_snapshot_id: str | None = None
    to_snapshot_id: str | None = None
    manifest_entry_count: int = 0
    proof_summaries: list[ProofSummary] = Field(default_factory=list)


class SnapshotTimelineResponse(BaseModel):
    data: list[SnapshotTimelineItem]
    meta: ResponseMeta


class SnapshotDiffEntry(BaseModel):
    manifest_entry_id: str
    category: Literal["added", "removed", "changed", "unchanged"]
    assembly_changed: bool
    execution_profile_changed: bool
    output_contract_changed: bool
    from_snapshot_id: str
    to_snapshot_id: str


class SnapshotDiffResponsePayload(BaseModel):
    from_snapshot_id: str
    to_snapshot_id: str
    entries: list[SnapshotDiffEntry]


class SnapshotDiffResponse(BaseModel):
    data: SnapshotDiffResponsePayload
    meta: ResponseMeta


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
        "unauthorized" in msg_l
        or "missing required legacy" in msg_l
        or "legacy variables" in msg_l
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
            from_assembly.get("output_contract_ref") if isinstance(from_assembly, dict) else None
        )
        to_output_contract = (
            to_assembly.get("output_contract_ref") if isinstance(to_assembly, dict) else None
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
    from app.schemas.audit_details import to_safe_details

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


@router.get("/personas", response_model=LlmPersonaListResponse)
def list_personas(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = select(LlmPersonaModel).order_by(LlmPersonaModel.name)
    personas = db.execute(stmt).scalars().all()

    # Map to API model with legacy tone support
    data = []
    for p in personas:
        model = LlmPersona.model_validate(p)
        # AC: Support legacy 'calm' tone by mapping it to 'warm'
        if model.tone == "calm":
            # We copy and update if frozen, or just set if not.
            # LlmPersona is likely frozen.
            model = model.model_copy(update={"tone": "warm"})
        data.append(model)

    return {
        "data": data,
        "meta": {"request_id": request_id},
    }


@router.post("/personas", response_model=LlmPersonaApiResponse)
def create_persona(
    request: Request,
    payload: LlmPersonaCreate,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    persona = LlmPersonaModel(
        name=payload.name,
        description=payload.description,
        tone=payload.tone,
        verbosity=payload.verbosity,
        style_markers=payload.style_markers,
        boundaries=payload.boundaries,
        allowed_topics=payload.allowed_topics,
        disallowed_topics=payload.disallowed_topics,
        formatting=payload.formatting,
        enabled=payload.enabled,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)

    # Boundary validation (Story 66.10 AC5)
    boundary_violations = []
    try:
        block = compose_persona_block(persona)
        boundary_violations = validate_persona_block(block, str(persona.id))
    except Exception as e:
        logger.debug("admin_persona_validation_error: %s", e)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_persona_create",
        target_type="llm_persona",
        target_id=str(persona.id),
        status="success",
        details={"name": persona.name},
    )
    db.commit()

    return {
        "data": LlmPersona.model_validate(persona),
        "meta": {"request_id": request_id, "boundary_violations": boundary_violations},
    }


@router.get("/personas/{id}", response_model=LlmPersonaDetailResponse)
def get_persona_detail(
    id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    persona = db.get(LlmPersonaModel, id)
    if not persona:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="persona_not_found",
            message=f"persona {id} not found",
            details={},
        )

    use_case_models = db.scalars(select(LlmUseCaseConfigModel)).all()
    use_cases = [
        item.key for item in use_case_models if str(id) in (item.allowed_persona_ids or [])
    ]
    affected_users_count = int(
        db.scalar(
            select(func.count(func.distinct(UserModel.id)))
            .select_from(UserModel)
            .join(UserSubscriptionModel, UserSubscriptionModel.user_id == UserModel.id)
            .where(UserModel.default_astrologer_id == str(id))
            .where(UserSubscriptionModel.status.in_(["active", "trialing"]))
        )
        or 0
    )

    return {
        "data": {
            "persona": LlmPersona.model_validate(persona),
            "use_cases": list(use_cases),
            "affected_users_count": affected_users_count,
        },
        "meta": {"request_id": request_id},
    }


@router.patch("/personas/{id}", response_model=LlmPersonaApiResponse)
def update_persona(
    id: uuid.UUID,
    request: Request,
    payload: LlmPersonaUpdate,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    persona = db.get(LlmPersonaModel, id)
    if not persona:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="persona_not_found",
            message=f"persona {id} not found",
            details={},
        )

    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)

    db.commit()
    db.refresh(persona)

    # Boundary validation (Story 66.10 AC5)
    boundary_violations = []
    try:
        block = compose_persona_block(persona)
        boundary_violations = validate_persona_block(block, str(persona.id))
    except Exception as e:
        logger.debug("admin_persona_validation_error: %s", e)

    action = "llm_persona_update"
    if "enabled" in update_data:
        action = "persona_activated" if persona.enabled else "persona_deactivated"

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action=action,
        target_type="llm_persona",
        target_id=str(persona.id),
        status="success",
        details={"persona_id": str(persona.id), "persona_name": persona.name, **update_data},
    )
    db.commit()

    return {
        "data": LlmPersona.model_validate(persona),
        "meta": {"request_id": request_id, "boundary_violations": boundary_violations},
    }


@router.delete("/personas/{id}", response_model=LlmPersonaApiResponse)
def disable_persona(
    id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    persona = db.get(LlmPersonaModel, id)
    if not persona:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="persona_not_found",
            message=f"persona {id} not found",
            details={},
        )

    persona.enabled = False
    db.commit()
    db.refresh(persona)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_persona_disable",
        target_type="llm_persona",
        target_id=str(persona.id),
        status="success",
        details={},
    )
    db.commit()

    return {"data": LlmPersona.model_validate(persona), "meta": {"request_id": request_id}}


@router.get("/output-schemas", response_model=LlmOutputSchemaListResponse)
def list_output_schemas(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = select(LlmOutputSchemaModel).order_by(LlmOutputSchemaModel.name)
    schemas = db.execute(stmt).scalars().all()

    return {
        "data": [LlmOutputSchema.model_validate(s) for s in schemas],
        "meta": {"request_id": request_id},
    }


@router.get("/output-schemas/{id}", response_model=LlmOutputSchemaApiResponse)
def get_output_schema(
    id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    schema = db.get(LlmOutputSchemaModel, id)
    if not schema:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="schema_not_found",
            message=f"schema {id} not found",
            details={},
        )

    return {"data": LlmOutputSchema.model_validate(schema), "meta": {"request_id": request_id}}


@router.get("/use-cases", response_model=LlmUseCaseListResponse)
def list_use_cases(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = select(LlmUseCaseConfigModel)
    use_cases = db.execute(stmt).scalars().all()

    result_data = []
    for uc in use_cases:
        active_prompt = PromptRegistryV2.get_active_prompt(db, uc.key)
        result_data.append(
            LlmUseCaseConfig(
                key=uc.key,
                display_name=uc.display_name,
                description=uc.description,
                output_schema_id=uc.output_schema_id,
                persona_strategy=uc.persona_strategy,
                safety_profile=uc.safety_profile,
                fallback_use_case_key=uc.fallback_use_case_key,
                allowed_persona_ids=uc.allowed_persona_ids,
                eval_fixtures_path=uc.eval_fixtures_path,
                eval_failure_threshold=uc.eval_failure_threshold,
                golden_set_path=uc.golden_set_path,
                active_prompt_version_id=active_prompt.id if active_prompt else None,
            )
        )

    return {"data": result_data, "meta": {"request_id": request_id}}


@router.get("/release-snapshots/timeline", response_model=SnapshotTimelineResponse)
def list_release_snapshots_timeline(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    snapshots = (
        db.execute(
            select(LlmReleaseSnapshotModel).order_by(
                desc(LlmReleaseSnapshotModel.activated_at), desc(LlmReleaseSnapshotModel.created_at)
            )
        )
        .scalars()
        .all()
    )

    timeline: list[SnapshotTimelineItem] = []
    for snapshot in snapshots:
        timeline.extend(_build_snapshot_timeline_events(snapshot))

    timeline.sort(key=lambda item: item.occurred_at, reverse=True)

    return {"data": timeline, "meta": {"request_id": request_id}}


@router.get("/release-snapshots/diff", response_model=SnapshotDiffResponse)
def get_release_snapshot_diff(
    request: Request,
    from_snapshot_id: uuid.UUID,
    to_snapshot_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    from_snapshot = db.get(LlmReleaseSnapshotModel, from_snapshot_id)
    to_snapshot = db.get(LlmReleaseSnapshotModel, to_snapshot_id)
    if from_snapshot is None or to_snapshot is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="snapshot_not_found",
            message="from_snapshot_id or to_snapshot_id does not exist",
            details={
                "from_snapshot_id": str(from_snapshot_id),
                "to_snapshot_id": str(to_snapshot_id),
            },
        )

    return {
        "data": {
            "from_snapshot_id": str(from_snapshot.id),
            "to_snapshot_id": str(to_snapshot.id),
            "entries": _snapshot_diff_entries(from_snapshot=from_snapshot, to_snapshot=to_snapshot),
        },
        "meta": {"request_id": request_id},
    }


@router.get("/catalog", response_model=AdminLlmCatalogResponse)
def list_llm_catalog(
    request: Request,
    feature: Optional[str] = None,
    subfeature: Optional[str] = None,
    plan: Optional[str] = None,
    locale: Optional[str] = None,
    provider: Optional[str] = None,
    source_of_truth_status: Optional[str] = None,
    assembly_status: Optional[str] = None,
    release_health_status: Optional[str] = None,
    catalog_visibility_status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "feature",
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = 25,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    freshness_window_minutes = 120

    latest_active = db.execute(
        select(LlmActiveReleaseModel).order_by(desc(LlmActiveReleaseModel.activated_at)).limit(1)
    ).scalar_one_or_none()
    active_snapshot = None
    if latest_active:
        active_snapshot = db.get(LlmReleaseSnapshotModel, latest_active.release_snapshot_id)

    release_health = (
        ((active_snapshot.manifest or {}).get("release_health") or {}) if active_snapshot else {}
    )
    active_release_health = str(release_health.get("status") or "n/a")

    entries_by_id: dict[str, AdminLlmCatalogEntry] = {}
    manifest_targets = (
        ((active_snapshot.manifest or {}).get("targets") or {}) if active_snapshot else {}
    )

    for manifest_entry_id, bundle in manifest_targets.items():
        assembly_data = bundle.get("assembly") or {}
        profile_data = bundle.get("profile") or {}

        feature_value = _to_none_if_literal_none(assembly_data.get("feature"))
        if not feature_value:
            split_values = str(manifest_entry_id).split(":")
            feature_value = split_values[0] if split_values else "unknown"
        subfeature_value = _to_none_if_literal_none(assembly_data.get("subfeature"))
        plan_value = _to_none_if_literal_none(assembly_data.get("plan"))
        locale_value = _to_none_if_literal_none(assembly_data.get("locale")) or "fr-FR"

        catalog_visibility = "visible"
        if not assembly_data:
            catalog_visibility = "orphaned"
        elif not profile_data:
            catalog_visibility = "stale"

        entries_by_id[str(manifest_entry_id)] = AdminLlmCatalogEntry(
            manifest_entry_id=str(manifest_entry_id),
            feature=feature_value,
            subfeature=subfeature_value,
            plan=plan_value,
            locale=locale_value,
            assembly_id=str(assembly_data.get("id")) if assembly_data.get("id") else None,
            assembly_status=str(assembly_data.get("status") or "unknown"),
            execution_profile_id=str(profile_data.get("id")) if profile_data.get("id") else None,
            execution_profile_ref=str(profile_data.get("id")) if profile_data.get("id") else None,
            output_contract_ref=str(assembly_data.get("output_contract_ref"))
            if assembly_data.get("output_contract_ref")
            else None,
            active_snapshot_id=str(active_snapshot.id) if active_snapshot else None,
            active_snapshot_version=active_snapshot.version if active_snapshot else None,
            provider=str(profile_data.get("provider")) if profile_data.get("provider") else None,
            model=str(profile_data.get("model")) if profile_data.get("model") else None,
            source_of_truth_status="active_snapshot",
            release_health_status=active_release_health,
            catalog_visibility_status=catalog_visibility,
            runtime_signal_status="n/a",
        )

    live_assemblies = (
        db.execute(
            select(PromptAssemblyConfigModel).where(
                PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED
            )
        )
        .scalars()
        .all()
    )
    for assembly in live_assemblies:
        manifest_entry_id = _to_manifest_entry(
            assembly.feature, assembly.subfeature, assembly.plan, assembly.locale
        )
        if manifest_entry_id in entries_by_id:
            continue
        profile = None
        if assembly.execution_profile_ref:
            profile = db.get(LlmExecutionProfileModel, assembly.execution_profile_ref)
        entries_by_id[manifest_entry_id] = AdminLlmCatalogEntry(
            manifest_entry_id=manifest_entry_id,
            feature=assembly.feature,
            subfeature=assembly.subfeature,
            plan=assembly.plan,
            locale=assembly.locale,
            assembly_id=str(assembly.id),
            assembly_status=str(assembly.status),
            execution_profile_id=str(profile.id) if profile else None,
            execution_profile_ref=str(profile.id) if profile else None,
            output_contract_ref=assembly.output_contract_ref,
            active_snapshot_id=None,
            active_snapshot_version=None,
            provider=profile.provider if profile else None,
            model=profile.model if profile else None,
            source_of_truth_status="live_table_fallback",
            release_health_status="n/a",
            catalog_visibility_status="orphaned",
            runtime_signal_status="n/a",
        )

    manifest_ids = list(entries_by_id.keys())
    latest_logs: dict[str, LlmCallLogModel] = {}
    if manifest_ids:
        latest_timestamps_subquery = (
            select(
                LlmCallLogModel.manifest_entry_id.label("manifest_entry_id"),
                func.max(LlmCallLogModel.timestamp).label("latest_timestamp"),
            )
            .where(LlmCallLogModel.manifest_entry_id.in_(manifest_ids))
            .group_by(LlmCallLogModel.manifest_entry_id)
            .subquery()
        )

        latest_log_rows = (
            db.execute(
                select(LlmCallLogModel).join(
                    latest_timestamps_subquery,
                    and_(
                        LlmCallLogModel.manifest_entry_id
                        == latest_timestamps_subquery.c.manifest_entry_id,
                        LlmCallLogModel.timestamp == latest_timestamps_subquery.c.latest_timestamp,
                    ),
                )
            )
            .scalars()
            .all()
        )

        for row in latest_log_rows:
            if row.manifest_entry_id and row.manifest_entry_id not in latest_logs:
                latest_logs[row.manifest_entry_id] = row

    now_utc = datetime.now(timezone.utc)
    for manifest_entry_id, entry in entries_by_id.items():
        log_row = latest_logs.get(manifest_entry_id)
        if log_row is None:
            entry.runtime_signal_status = "n/a"
            continue
        observed_at = log_row.timestamp
        if observed_at.tzinfo is None or observed_at.utcoffset() is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        age_minutes = (now_utc - observed_at).total_seconds() / 60
        entry.runtime_signal_status = (
            "fresh" if age_minutes <= freshness_window_minutes else "stale"
        )
        entry.execution_path_kind = log_row.execution_path_kind
        entry.context_compensation_status = log_row.context_compensation_status
        entry.max_output_tokens_source = log_row.max_output_tokens_source

    entries = list(entries_by_id.values())
    if feature:
        entries = [entry for entry in entries if entry.feature == feature]
    if subfeature:
        entries = [entry for entry in entries if entry.subfeature == subfeature]
    if plan:
        entries = [entry for entry in entries if entry.plan == plan]
    if locale:
        entries = [entry for entry in entries if entry.locale == locale]
    if provider:
        entries = [entry for entry in entries if entry.provider == provider]
    if source_of_truth_status:
        entries = [
            entry for entry in entries if entry.source_of_truth_status == source_of_truth_status
        ]
    if assembly_status:
        entries = [entry for entry in entries if entry.assembly_status == assembly_status]
    if release_health_status:
        entries = [
            entry for entry in entries if entry.release_health_status == release_health_status
        ]
    if catalog_visibility_status:
        entries = [
            entry
            for entry in entries
            if entry.catalog_visibility_status == catalog_visibility_status
        ]
    if search:
        lowered = search.lower()
        entries = [
            entry
            for entry in entries
            if lowered in entry.manifest_entry_id.lower()
            or lowered in entry.feature.lower()
            or lowered in (entry.subfeature or "").lower()
            or lowered in (entry.plan or "").lower()
            or lowered in (entry.locale or "").lower()
        ]

    catalog_facets = _collect_catalog_facets(entries)

    allowed_sort_fields = {
        "feature",
        "subfeature",
        "plan",
        "locale",
        "manifest_entry_id",
        "provider",
        "source_of_truth_status",
        "assembly_status",
        "release_health_status",
        "catalog_visibility_status",
    }
    resolved_sort_by = sort_by if sort_by in allowed_sort_fields else "feature"
    reverse_sort = sort_order.lower() == "desc"
    entries.sort(
        key=lambda entry: (
            _catalog_sort_value(entry, resolved_sort_by),
            _catalog_sort_value(entry, "feature"),
            _catalog_sort_value(entry, "subfeature"),
            _catalog_sort_value(entry, "plan"),
            _catalog_sort_value(entry, "locale"),
            _catalog_sort_value(entry, "manifest_entry_id"),
        ),
        reverse=reverse_sort,
    )

    safe_page = max(page, 1)
    safe_page_size = max(min(page_size, 100), 1)
    start = (safe_page - 1) * safe_page_size
    paged_entries = entries[start : start + safe_page_size]

    return {
        "data": paged_entries,
        "meta": {
            "request_id": request_id,
            "total": len(entries),
            "page": safe_page,
            "page_size": safe_page_size,
            "sort_by": resolved_sort_by,
            "sort_order": "desc" if reverse_sort else "asc",
            "freshness_window_minutes": freshness_window_minutes,
            "facets": catalog_facets,
        },
    }


@router.get("/catalog/{manifest_entry_id}/resolved", response_model=AdminResolvedAssemblyResponse)
def get_resolved_catalog_entry(
    manifest_entry_id: str,
    request: Request,
    inspection_mode: AdminInspectionMode = Query(
        "assembly_preview",
        description=(
            "Mode d'inspection admin: prévisualisation assembly (variables statiques), "
            "prévisualisation runtime (manques traités comme bloquants), "
            "ou exécution live (même sémantique runtime que runtime_preview pour l'instant)."
        ),
    ),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)

    latest_active = db.execute(
        select(LlmActiveReleaseModel).order_by(desc(LlmActiveReleaseModel.activated_at)).limit(1)
    ).scalar_one_or_none()
    active_snapshot = None
    manifest_bundle: dict[str, Any] | None = None
    if latest_active:
        active_snapshot = db.get(LlmReleaseSnapshotModel, latest_active.release_snapshot_id)
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
            code="snapshot_bundle_unusable",
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
                code="invalid_manifest_entry_id",
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
            code="manifest_entry_not_found",
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
        else str(profile_data.get("model") or resolved.execution_config.model)
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
            placeholders.append(
                ResolvedPlaceholderView(
                    name=placeholder_name,
                    status="resolved",
                    classification=classification,
                    resolution_source="runtime_context",
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
            placeholders.append(
                ResolvedPlaceholderView(
                    name=placeholder_name,
                    status="unknown",
                    classification=classification,
                    resolution_source="unknown",
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
        final_max_output_tokens = resolved.execution_config.max_output_tokens
        max_output_tokens_source = "assembly_execution_config"
    final_timeout_seconds = (
        effective_profile_timeout
        if effective_profile_timeout is not None
        else resolved.execution_config.timeout_seconds
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
        "reasoning": effective_reasoning_profile or resolved.execution_config.reasoning_effort,
        "verbosity": effective_verbosity_profile or resolved.execution_config.verbosity,
        "provider_params": sanitize_payload(
            {
                "temperature": (
                    translated_provider_params.get("temperature")
                    if "temperature" in translated_provider_params
                    else resolved.execution_config.temperature
                ),
                "max_output_tokens_final": final_max_output_tokens,
                "timeout_seconds": final_timeout_seconds,
                "max_output_tokens_source": max_output_tokens_source,
                **translated_provider_params,
            },
            Sink.ADMIN_API,
        ),
    }

    data = AdminResolvedAssemblyView(
        manifest_entry_id=manifest_entry_id,
        feature=assembly_model.feature,
        subfeature=assembly_model.subfeature,
        plan=assembly_model.plan,
        locale=assembly_model.locale,
        assembly_id=str(assembly_model.id),
        inspection_mode=inspection_mode,
        source_of_truth_status=source_of_truth_status,
        active_snapshot_id=str(active_snapshot.id) if active_snapshot else None,
        active_snapshot_version=active_snapshot.version if active_snapshot else None,
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
                "persona_block": resolved.persona_block,
                "execution_parameters": execution_profile_view["provider_params"],
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

    return {"data": data, "meta": {"request_id": request_id}}


@router.patch("/use-cases/{key}", response_model=LlmUseCaseListResponse)
def update_use_case_config(
    key: str,
    request: Request,
    payload: UseCaseUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    uc = db.get(LlmUseCaseConfigModel, key)
    if not uc:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="use_case_not_found",
            message=f"use case {key} not found",
            details={},
        )

    # Story 66.28: Block modification of forbidden nominal features (AC5)
    from app.llm_orchestration.feature_taxonomy import is_nominal_feature_allowed

    if not is_nominal_feature_allowed(key):
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="forbidden_feature",
            message=f"use case {key} is legacy and frozen. No modifications allowed.",
            details={},
        )

    update_details = {}

    if payload.persona_id is not None:
        if payload.persona_id:
            persona_uuid = uuid.UUID(payload.persona_id)
            if not db.get(LlmPersonaModel, persona_uuid):
                return _error_response(
                    status_code=404,
                    request_id=request_id,
                    code="persona_not_found",
                    message=f"persona {payload.persona_id} not found",
                    details={},
                )
            uc.allowed_persona_ids = [payload.persona_id]
        else:
            uc.allowed_persona_ids = []
        update_details["allowed_persona_ids"] = uc.allowed_persona_ids

    if payload.allowed_persona_ids is not None:
        valid_ids = []
        for pid in payload.allowed_persona_ids:
            try:
                persona_uuid = uuid.UUID(pid)
                if db.get(LlmPersonaModel, persona_uuid):
                    valid_ids.append(pid)
                else:
                    return _error_response(
                        status_code=404,
                        request_id=request_id,
                        code="persona_not_found",
                        message=f"persona {pid} not found",
                        details={},
                    )
            except (ValueError, TypeError):
                return _error_response(
                    status_code=422,
                    request_id=request_id,
                    code="invalid_persona_id",
                    message=f"persona_id {pid} is not a valid UUID",
                    details={},
                )
        uc.allowed_persona_ids = valid_ids
        update_details["allowed_persona_ids"] = uc.allowed_persona_ids

    if payload.persona_strategy:
        uc.persona_strategy = payload.persona_strategy
        update_details["persona_strategy"] = uc.persona_strategy

    if payload.safety_profile:
        try:
            get_hard_policy(payload.safety_profile)
            uc.safety_profile = payload.safety_profile
            update_details["safety_profile"] = uc.safety_profile
        except ValueError as e:
            return _error_response(
                status_code=422,
                request_id=request_id,
                code="invalid_safety_profile",
                message=str(e),
                details={},
            )

    if payload.output_schema_id is not None:
        if payload.output_schema_id:
            schema_uuid = uuid.UUID(payload.output_schema_id)
            if not db.get(LlmOutputSchemaModel, schema_uuid):
                return _error_response(
                    status_code=404,
                    request_id=request_id,
                    code="schema_not_found",
                    message=f"schema {payload.output_schema_id} not found",
                    details={},
                )
            uc.output_schema_id = payload.output_schema_id
        else:
            uc.output_schema_id = None
        update_details["output_schema_id"] = uc.output_schema_id

    if payload.fallback_use_case_key is not None:
        uc.fallback_use_case_key = payload.fallback_use_case_key
        update_details["fallback_use_case_key"] = uc.fallback_use_case_key

    if payload.eval_fixtures_path is not None:
        uc.eval_fixtures_path = payload.eval_fixtures_path
        update_details["eval_fixtures_path"] = uc.eval_fixtures_path

    if payload.eval_failure_threshold is not None:
        uc.eval_failure_threshold = payload.eval_failure_threshold
        update_details["eval_failure_threshold"] = uc.eval_failure_threshold

    if payload.golden_set_path is not None:
        uc.golden_set_path = payload.golden_set_path
        update_details["golden_set_path"] = uc.golden_set_path

    db.commit()
    db.refresh(uc)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_use_case_update_config",
        target_type="llm_use_case",
        target_id=key,
        status="success",
        details=update_details,
    )
    db.commit()

    # H2: Check for coverage warning
    warnings = []
    if uc.persona_strategy == "required":
        has_active = False
        if uc.allowed_persona_ids:
            p_uuids = [uuid.UUID(pid) for pid in uc.allowed_persona_ids]
            active_stmt = select(func.count(LlmPersonaModel.id)).where(
                and_(LlmPersonaModel.id.in_(p_uuids), LlmPersonaModel.enabled)
            )
            count = db.execute(active_stmt).scalar() or 0
            has_active = count > 0

        if not has_active:
            warnings.append("use_case_persona_coverage_broken")

    active_prompt = PromptRegistryV2.get_active_prompt(db, uc.key)
    uc_data = LlmUseCaseConfig(
        key=uc.key,
        display_name=uc.display_name,
        description=uc.description,
        output_schema_id=uc.output_schema_id,
        persona_strategy=uc.persona_strategy,
        safety_profile=uc.safety_profile,
        fallback_use_case_key=uc.fallback_use_case_key,
        allowed_persona_ids=uc.allowed_persona_ids,
        eval_fixtures_path=uc.eval_fixtures_path,
        eval_failure_threshold=uc.eval_failure_threshold,
        golden_set_path=uc.golden_set_path,
        active_prompt_version_id=active_prompt.id if active_prompt else None,
    )

    return {"data": [uc_data], "meta": {"request_id": request_id, "warnings": warnings}}


@router.patch("/use-cases/{key}/persona", response_model=LlmUseCaseListResponse)
def associate_persona(
    key: str,
    request: Request,
    payload: PersonaAssociationPayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Spec 28.3 Task 4: Separate endpoint for persona association.
    """
    request_id = resolve_request_id(request)

    uc = db.get(LlmUseCaseConfigModel, key)
    if not uc:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="use_case_not_found",
            message=f"use case {key} not found",
            details={},
        )

    if payload.persona_id:
        persona_uuid = uuid.UUID(payload.persona_id)
        if not db.get(LlmPersonaModel, persona_uuid):
            return _error_response(
                status_code=404,
                request_id=request_id,
                code="persona_not_found",
                message=f"persona {payload.persona_id} not found",
                details={},
            )
        uc.allowed_persona_ids = [payload.persona_id]
    else:
        uc.allowed_persona_ids = []

    db.commit()
    db.refresh(uc)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_use_case_associate_persona",
        target_type="llm_use_case",
        target_id=key,
        status="success",
        details={"persona_id": payload.persona_id},
    )
    db.commit()

    # H2: Check for coverage warning
    warnings = []
    if uc.persona_strategy == "required":
        # Check if any allowed persona is actually enabled
        has_active = False
        if uc.allowed_persona_ids:
            p_uuids = [uuid.UUID(pid) for pid in uc.allowed_persona_ids]
            active_stmt = select(func.count(LlmPersonaModel.id)).where(
                and_(LlmPersonaModel.id.in_(p_uuids), LlmPersonaModel.enabled)
            )
            count = db.execute(active_stmt).scalar() or 0
            has_active = count > 0

        if not has_active:
            warnings.append("use_case_persona_coverage_broken")

    active_prompt = PromptRegistryV2.get_active_prompt(db, uc.key)
    uc_data = LlmUseCaseConfig(
        key=uc.key,
        display_name=uc.display_name,
        description=uc.description,
        output_schema_id=uc.output_schema_id,
        persona_strategy=uc.persona_strategy,
        safety_profile=uc.safety_profile,
        fallback_use_case_key=uc.fallback_use_case_key,
        allowed_persona_ids=uc.allowed_persona_ids,
        eval_fixtures_path=uc.eval_fixtures_path,
        eval_failure_threshold=uc.eval_failure_threshold,
        golden_set_path=uc.golden_set_path,
        active_prompt_version_id=active_prompt.id if active_prompt else None,
    )

    return {"data": [uc_data], "meta": {"request_id": request_id, "warnings": warnings}}


@router.get("/use-cases/{key}/contract", response_model=LlmUseCaseContractResponse)
def get_use_case_contract(
    key: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    uc = db.get(LlmUseCaseConfigModel, key)
    if not uc:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="use_case_not_found",
            message=f"use case {key} not found",
            details={},
        )

    # Resolve output schema if any
    output_schema = None
    if uc.output_schema_id:
        schema_model = db.get(LlmOutputSchemaModel, uuid.UUID(uc.output_schema_id))
        if schema_model:
            output_schema = schema_model.json_schema

    active_prompt = PromptRegistryV2.get_active_prompt(db, uc.key)

    contract = LlmUseCaseContract(
        key=uc.key,
        display_name=uc.display_name,
        description=uc.description,
        input_schema=uc.input_schema,
        output_schema=output_schema,
        output_schema_id=uc.output_schema_id,
        persona_strategy=uc.persona_strategy,
        safety_profile=uc.safety_profile,
        fallback_use_case_key=uc.fallback_use_case_key,
        required_prompt_placeholders=uc.required_prompt_placeholders,
        allowed_persona_ids=uc.allowed_persona_ids,
        active_prompt_version_id=active_prompt.id if active_prompt else None,
    )

    return {"data": contract, "meta": {"request_id": request_id}}


@router.get("/use-cases/{key}/prompts", response_model=LlmPromptHistoryResponse)
def list_prompt_history(
    key: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = (
        select(LlmPromptVersionModel)
        .where(LlmPromptVersionModel.use_case_key == key)
        .order_by(LlmPromptVersionModel.created_at.desc())
    )
    versions = db.execute(stmt).scalars().all()

    return {
        "data": [LlmPromptVersion.model_validate(v) for v in versions],
        "meta": {"request_id": request_id},
    }


@router.post("/use-cases/{key}/prompts", response_model=LlmPromptApiResponse)
def create_prompt_draft(
    key: str,
    request: Request,
    payload: LlmPromptVersionCreate,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    uc = db.get(LlmUseCaseConfigModel, key)
    if not uc:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="use_case_not_found",
            message=f"use case {key} not found",
            details={},
        )

    # Story 66.28: Block resurrection of forbidden nominal features (AC5)
    from app.llm_orchestration.feature_taxonomy import is_nominal_feature_allowed

    if not is_nominal_feature_allowed(key):
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="forbidden_feature",
            message=f"use case {key} is legacy and frozen. No new drafts allowed.",
            details={},
        )

    lint_result = PromptLint.lint_prompt(
        payload.developer_prompt, use_case_required_placeholders=uc.required_prompt_placeholders
    )
    if not lint_result.passed:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="lint_failed",
            message="prompt lint validation failed",
            details={"errors": lint_result.errors, "warnings": lint_result.warnings},
        )

    version = LlmPromptVersionModel(
        use_case_key=key,
        status=PromptStatus.DRAFT,
        developer_prompt=payload.developer_prompt,
        model=payload.model,
        temperature=payload.temperature,
        max_output_tokens=payload.max_output_tokens,
        fallback_use_case_key=payload.fallback_use_case_key,
        created_by=str(current_user.id),
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_prompt_create_draft",
        target_type="llm_prompt",
        target_id=str(version.id),
        status="success",
        details={"use_case_key": key, "model": version.model},
    )
    db.commit()

    return {"data": LlmPromptVersion.model_validate(version), "meta": {"request_id": request_id}}


@router.patch(
    "/use-cases/{key}/prompts/{version_id}/publish", response_model=LlmPromptPublishResponse
)
async def publish_prompt(
    key: str,
    version_id: uuid.UUID,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    uc = db.get(LlmUseCaseConfigModel, key)
    if not uc:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="use_case_not_found",
            message=f"use case {key} not found",
            details={},
        )

    eval_report = None
    if uc.eval_fixtures_path:
        eval_report = await run_eval(
            use_case_key=key,
            prompt_version_id=str(version_id),
            fixtures_path=uc.eval_fixtures_path,
            db=db,
        )

        if eval_report.failure_rate > uc.eval_failure_threshold:
            eval_report.blocked_publication = True
            return _error_response(
                status_code=409,
                request_id=request_id,
                code="eval_failed",
                message=f"Evaluation failure rate ({eval_report.failure_rate:.2%}) exceeds threshold ({uc.eval_failure_threshold:.2%})",  # noqa: E501
                details=eval_report.model_dump(),
            )

    golden_report = None
    if uc.golden_set_path:
        from app.llm_orchestration.services.golden_regression_service import (
            GoldenRegressionService,
        )

        golden_report = await GoldenRegressionService.run_campaign(
            use_case_key=key,
            prompt_version_id=str(version_id),
            golden_set_path=uc.golden_set_path,
            db=db,
        )
        # AC21: Block on 'fail' or 'invalid' (High fix)
        if golden_report.verdict in ("fail", "invalid"):
            return _error_response(
                status_code=409,
                request_id=request_id,
                code="golden_regression_failed",
                message=(
                    f"Golden regression campaign {golden_report.verdict} "
                    "(Blocking drift or invalid context detected)"
                ),
                details=golden_report.model_dump(),
            )

    try:
        version = PromptRegistryV2.publish_prompt(db, version_id)

        # Operational Policy for 'constrained' (Medium fix)
        warnings = []
        if golden_report and golden_report.verdict == "constrained":
            warnings.append("golden_regression_constrained_drift")

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_prompt_publish",
            target_type="llm_prompt",
            target_id=str(version.id),
            status="success",
            details={
                "use_case_key": key,
                "eval_run": eval_report is not None,
                "golden_campaign": golden_report is not None,
                "golden_verdict": golden_report.verdict if golden_report else None,
            },
        )
        db.commit()

        return {
            "data": LlmPromptVersion.model_validate(version),
            "meta": {
                "request_id": request_id,
                "warnings": warnings,
                "eval_report": eval_report.model_dump() if eval_report else None,
                "golden_report": golden_report.model_dump() if golden_report else None,
            },
        }

    except ValueError as err:
        from app.llm_orchestration.feature_taxonomy import is_nominal_feature_allowed

        if not is_nominal_feature_allowed(key):
            return _error_response(
                status_code=403,
                request_id=request_id,
                code="forbidden_feature",
                message=str(err),
                details={},
            )
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="validation_error",
            message=str(err),
            details={},
        )
    except Exception as err:
        logger.exception("admin_llm_publish_failed")
        return _error_response(
            status_code=500,
            request_id=request_id,
            code="publish_failed",
            message=str(err),
            details={},
        )


@router.post("/use-cases/{key}/rollback", response_model=LlmPromptApiResponse)
def rollback_prompt(
    key: str,
    request: Request,
    payload: RollbackPromptPayload | None = None,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    previous_version = PromptRegistryV2.get_active_prompt(db, key)

    try:
        version = PromptRegistryV2.rollback_prompt(
            db,
            key,
            target_version_id=payload.target_version_id if payload else None,
        )

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_prompt_rollback",
            target_type="llm_prompt",
            target_id=str(version.id),
            status="success",
            details={
                "use_case_key": key,
                "from_version": str(previous_version.id) if previous_version else None,
                "to_version": str(version.id),
            },
        )
        db.commit()

        return {
            "data": LlmPromptVersion.model_validate(version).model_dump(mode="json"),
            "meta": {"request_id": request_id},
        }
    except ValueError as err:
        from app.llm_orchestration.feature_taxonomy import is_nominal_feature_allowed

        if not is_nominal_feature_allowed(key):
            return _error_response(
                status_code=403,
                request_id=request_id,
                code="forbidden_feature",
                message=str(err),
                details={},
            )
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="rollback_failed",
            message=str(err),
            details={},
        )


@router.get("/call-logs", response_model=LlmCallLogListResponse)
def list_call_logs(
    request: Request,
    use_case: Optional[str] = None,
    status: Optional[str] = None,
    prompt_version_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = select(LlmCallLogModel)
    if use_case:
        stmt = stmt.where(LlmCallLogModel.use_case == use_case)
    if status:
        stmt = stmt.where(LlmCallLogModel.validation_status == status)
    if prompt_version_id:
        stmt = stmt.where(LlmCallLogModel.prompt_version_id == prompt_version_id)
    if from_date:
        stmt = stmt.where(LlmCallLogModel.timestamp >= from_date)
    if to_date:
        stmt = stmt.where(LlmCallLogModel.timestamp <= to_date)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    stmt = (
        stmt.order_by(desc(LlmCallLogModel.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = db.execute(stmt).scalars().all()

    return {
        "data": [LlmCallLog.model_validate(log) for log in logs],
        "meta": {
            "request_id": request_id,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/dashboard", response_model=LlmDashboardResponse)
def get_dashboard(
    request: Request,
    period_hours: int = 24,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    since = datetime.now(timezone.utc) - timedelta(hours=period_hours)
    use_cases_stmt = (
        select(LlmCallLogModel.use_case).where(LlmCallLogModel.timestamp >= since).distinct()
    )
    use_cases = db.execute(use_cases_stmt).scalars().all()

    metrics_list = []
    for uc in use_cases:
        base_stmt = select(
            func.count(LlmCallLogModel.id).label("count"),
            func.avg(LlmCallLogModel.latency_ms).label("avg_lat"),
            func.sum(LlmCallLogModel.tokens_in + LlmCallLogModel.tokens_out).label("total_tokens"),
            func.sum(LlmCallLogModel.cost_usd_estimated).label("total_cost"),
            func.sum(sa.case((LlmCallLogModel.repair_attempted, 1), else_=0)).label("repair_count"),
            func.sum(sa.case((LlmCallLogModel.fallback_triggered, 1), else_=0)).label(
                "fallback_count"
            ),
            func.sum(sa.case((LlmCallLogModel.evidence_warnings_count > 0, 1), else_=0)).label(
                "warning_count"
            ),
        ).where(and_(LlmCallLogModel.use_case == uc, LlmCallLogModel.timestamp >= since))

        stats = db.execute(base_stmt).first()
        count = stats.count or 0
        if count == 0:
            continue

        dist_stmt = (
            select(LlmCallLogModel.validation_status, func.count(LlmCallLogModel.id))
            .where(and_(LlmCallLogModel.use_case == uc, LlmCallLogModel.timestamp >= since))
            .group_by(LlmCallLogModel.validation_status)
        )

        dist_res = db.execute(dist_stmt).all()
        distribution = {status: (c / count) * 100 for status, c in dist_res}

        # M2: Use SQL percentile if supported (PostgreSQL)
        is_sqlite = db.bind.dialect.name == "sqlite"
        if not is_sqlite:
            # PostgreSQL implementation
            p95_stmt = select(
                func.percentile_cont(0.95).within_group(LlmCallLogModel.latency_ms)
            ).where(and_(LlmCallLogModel.use_case == uc, LlmCallLogModel.timestamp >= since))
            p95 = db.execute(p95_stmt).scalar() or 0
        else:
            # SQLite fallback (in-memory)
            latencies_stmt = (
                select(LlmCallLogModel.latency_ms)
                .where(and_(LlmCallLogModel.use_case == uc, LlmCallLogModel.timestamp >= since))
                .order_by(LlmCallLogModel.latency_ms)
            )
            latencies = db.execute(latencies_stmt).scalars().all()
            p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

        metrics_list.append(
            LlmDashboardMetrics(
                use_case=uc,
                request_count=count,
                avg_latency_ms=float(stats.avg_lat or 0),
                p95_latency_ms=float(p95),
                total_tokens=int(stats.total_tokens or 0),
                total_cost_usd=float(stats.total_cost or 0),
                validation_status_distribution=distribution,
                repair_rate=(stats.repair_count / count) * 100 if stats.repair_count else 0,
                fallback_rate=(stats.fallback_count / count) * 100 if stats.fallback_count else 0,
                avg_tokens_per_request=(stats.total_tokens / count) if stats.total_tokens else 0,
                evidence_warning_rate=(stats.warning_count / count) * 100
                if stats.warning_count
                else 0,
            )
        )

    return {"data": metrics_list, "meta": {"request_id": request_id}}


@router.post("/replay", response_model=dict)
async def replay_request(
    request: Request,
    payload: ReplayPayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    try:
        result = await replay(
            db=db, request_id=payload.request_id, prompt_version_id=payload.prompt_version_id
        )

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_call_replayed",
            target_type="llm_call_log",
            target_id=payload.request_id,
            status="success",
            details={"new_prompt_version_id": payload.prompt_version_id},
        )
        db.commit()

        return {"data": result, "meta": {"request_id": request_id}}
    except Exception as e:
        return _error_response(
            status_code=403 if "disabled" in str(e) else 400,
            request_id=request_id,
            code="replay_failed",
            message=str(e),
            details={},
        )


@router.post("/call-logs/purge", response_model=dict)
async def purge_logs(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    deleted_count = await purge_expired_logs(db)

    _record_audit_event(
        db,
        request_id=request_id,
        actor=current_user,
        action="llm_logs_purge",
        target_type="llm_call_log",
        target_id=None,
        status="success",
        details={"deleted_count": deleted_count},
    )
    db.commit()

    return {"data": {"deleted_count": deleted_count}, "meta": {"request_id": request_id}}
