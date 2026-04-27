from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
)
from app.api.v1.constants import (
    ADMIN_MANUAL_EXECUTE_ROUTE_PATH,
    ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
)
from app.api.v1.schemas.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.api.v1.schemas.routers.admin.llm.prompts import (
    AdminCatalogManualExecutePayload,
    AdminCatalogManualExecuteResponse,
    AdminInspectionMode,
    AdminLlmCatalogEntry,
    AdminLlmCatalogResponse,
    AdminResolvedAssemblyResponse,
    LlmCallLog,
    LlmCallLogListResponse,
    LlmDashboardMetrics,
    LlmDashboardResponse,
    LlmOutputSchemaApiResponse,
    LlmOutputSchemaListResponse,
    LlmPersonaApiResponse,
    LlmPersonaDetailResponse,
    LlmPersonaListResponse,
    LlmPromptApiResponse,
    LlmPromptHistoryResponse,
    LlmPromptPublishResponse,
    LlmUseCaseContract,
    LlmUseCaseContractResponse,
    LlmUseCaseListResponse,
    PersonaAssociationPayload,
    ReplayPayload,
    ResponseMeta,
    RollbackPromptPayload,
    SnapshotDiffResponse,
    SnapshotTimelineItem,
    SnapshotTimelineResponse,
    UseCaseUpdatePayload,
)
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.domain.llm.configuration.admin_models import (
    LlmOutputSchema,
    LlmPersona,
    LlmPersonaCreate,
    LlmPersonaUpdate,
    LlmPromptVersionCreate,
)
from app.domain.llm.configuration.canonical_use_case_registry import (
    get_canonical_output_schema_definition,
    get_canonical_use_case_contract,
    list_canonical_use_case_contracts,
)
from app.domain.llm.prompting.persona_boundary import (
    validate_persona_block,
)
from app.domain.llm.prompting.personas import compose_persona_block
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionUserInput,
    GatewayConfigError,
    GatewayError,
    InputValidationError,
    LLMExecutionRequest,
    OutputValidationError,
    PromptRenderError,
    UnknownUseCaseError,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.domain.llm.runtime.observability import purge_expired_logs
from app.infra.db.models.billing import UserSubscriptionModel
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_observability import (
    LlmCallLogModel,
    LlmCallLogOperationalMetadataModel,
)
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    PromptStatus,
)
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.llm.prompting_repository import (
    get_latest_active_release_snapshot,
    get_latest_prompt_version,
    get_release_snapshot,
    get_sample_payload,
    get_use_case_config,
    list_prompt_versions,
)
from app.infra.db.repositories.llm.prompting_repository import (
    list_release_snapshots_timeline as repo_list_release_snapshots_timeline,
)
from app.infra.db.session import get_db_session
from app.ops.llm.services import PromptLint, PromptRegistryV2, replay, run_eval
from app.services.llm_generation.admin_manual_execution import (
    _build_admin_manual_execute_response_payload,
    _record_admin_manual_execution_audit,
    _record_audit_event,
)
from app.services.llm_generation.admin_prompts import (
    _admin_catalog_runtime_preview_blocking_reasons,
    _build_admin_resolved_catalog_view,
    _build_canonical_admin_use_case_config,
    _call_log_scope_filter,
    _catalog_sort_value,
    _collect_catalog_facets,
    _ensure_admin_use_case_shadow_row,
    _is_removed_legacy_use_case_key,
    _legacy_removed_call_log_filter,
    _raise_error,
    _serialize_prompt_version,
    _to_manifest_entry,
    _to_none_if_literal_none,
)
from app.services.llm_generation.admin_release_snapshots import (
    _build_snapshot_timeline_events,
    _snapshot_diff_entries,
)

logger = logging.getLogger(__name__)

# Epic 69.3: marqueurs observabilité (logs, audit, en-tête HTTP).
router = APIRouter(prefix="/v1/admin/llm", tags=["admin-llm"])


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
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.PERSONA_NOT_FOUND.value,
            message=f"persona {id} not found",
            details={},
        )

    use_cases: list[str] = []
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
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.PERSONA_NOT_FOUND.value,
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
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.PERSONA_NOT_FOUND.value,
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
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.SCHEMA_NOT_FOUND.value,
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

    result_data = []
    for contract in list_canonical_use_case_contracts():
        if _is_removed_legacy_use_case_key(contract.key):
            continue
        payload = _build_canonical_admin_use_case_config(db, contract.key)
        if payload is not None:
            result_data.append(payload)

    return {"data": result_data, "meta": {"request_id": request_id}}


@router.get("/release-snapshots/timeline", response_model=SnapshotTimelineResponse)
def list_release_snapshots_timeline(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    snapshots = repo_list_release_snapshots_timeline(db)

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
    from_snapshot = get_release_snapshot(db, from_snapshot_id)
    to_snapshot = get_release_snapshot(db, to_snapshot_id)
    if from_snapshot is None or to_snapshot is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.SNAPSHOT_NOT_FOUND.value,
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

    active_snapshot = get_latest_active_release_snapshot(db)

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
            output_schema_id=str(assembly_data.get("output_schema_id"))
            if assembly_data.get("output_schema_id")
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
            output_schema_id=str(assembly.output_schema_id) if assembly.output_schema_id else None,
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
                LlmCallLogOperationalMetadataModel.manifest_entry_id.label("manifest_entry_id"),
                func.max(LlmCallLogModel.timestamp).label("latest_timestamp"),
            )
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .where(LlmCallLogOperationalMetadataModel.manifest_entry_id.in_(manifest_ids))
            .group_by(LlmCallLogOperationalMetadataModel.manifest_entry_id)
            .subquery()
        )

        latest_log_rows = db.execute(
            select(LlmCallLogModel, LlmCallLogOperationalMetadataModel.manifest_entry_id)
            .join(
                LlmCallLogOperationalMetadataModel,
                LlmCallLogOperationalMetadataModel.call_log_id == LlmCallLogModel.id,
            )
            .join(
                latest_timestamps_subquery,
                and_(
                    LlmCallLogOperationalMetadataModel.manifest_entry_id
                    == latest_timestamps_subquery.c.manifest_entry_id,
                    LlmCallLogModel.timestamp == latest_timestamps_subquery.c.latest_timestamp,
                ),
            )
        ).all()

        for log_row, manifest_entry_id in latest_log_rows:
            if manifest_entry_id and manifest_entry_id not in latest_logs:
                latest_logs[str(manifest_entry_id)] = log_row

    now_utc = datetime_provider.utcnow()
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
    sample_payload_id: uuid.UUID | None = Query(
        default=None,
        description=(
            "Identifiant optionnel d'un sample payload admin compatible avec la cible "
            "feature/locale; utilisé pour enrichir les variables runtime de preview."
        ),
    ),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    del current_user
    request_id = resolve_request_id(request)
    built = _build_admin_resolved_catalog_view(
        db=db,
        manifest_entry_id=manifest_entry_id,
        inspection_mode=inspection_mode,
        sample_payload_id=sample_payload_id,
        request_id=request_id,
    )
    if isinstance(built, JSONResponse):
        return built
    return {"data": built, "meta": {"request_id": request_id}}


@router.post(ADMIN_MANUAL_EXECUTE_ROUTE_PATH, response_model=AdminCatalogManualExecuteResponse)
async def execute_admin_catalog_sample_payload(
    manifest_entry_id: str,
    request: Request,
    payload: AdminCatalogManualExecutePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    trace_id = str(uuid.uuid4())
    logger.info(
        (
            "admin_manual_llm_execute_surface=%s event=admin_manual_llm_execute_start "
            "manifest_entry_id=%s sample_payload_id=%s request_id=%s trace_id=%s "
            "operator_user_id=%s"
        ),
        ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
        manifest_entry_id,
        str(payload.sample_payload_id),
        request_id,
        trace_id,
        current_user.id,
    )
    built = _build_admin_resolved_catalog_view(
        db=db,
        manifest_entry_id=manifest_entry_id,
        inspection_mode="runtime_preview",
        sample_payload_id=payload.sample_payload_id,
        request_id=request_id,
    )
    if isinstance(built, JSONResponse):
        return built
    blocking = _admin_catalog_runtime_preview_blocking_reasons(built)
    if blocking:
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={"blocking_reasons": blocking, "failure_kind": "runtime_preview_incomplete"},
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.RUNTIME_PREVIEW_INCOMPLETE_FOR_EXECUTION.value,
            message="runtime preview is incomplete; cannot execute provider call",
            details={
                "failure_kind": "runtime_preview_incomplete",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "blocking_reasons": blocking,
            },
        )
    sample_row = get_sample_payload(db, payload.sample_payload_id)
    if sample_row is None or not isinstance(sample_row.payload_json, dict):
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.SAMPLE_PAYLOAD_NOT_FOUND.value,
            message="sample payload not found",
            details={"sample_payload_id": str(payload.sample_payload_id)},
        )
    extra_ctx: dict[str, Any] = dict(sample_row.payload_json)
    extra_ctx["_manifest_entry_id"] = manifest_entry_id
    extra_ctx["_admin_manual_canonical_execution"] = True
    extra_ctx["_admin_manual_sample_payload_id"] = str(payload.sample_payload_id)

    user_in = ExecutionUserInput(
        use_case=built.use_case_key,
        locale=built.locale or "fr-FR",
        feature=built.feature,
        subfeature=built.subfeature,
        plan=built.plan,
        message=(
            extra_ctx.get("message")
            if isinstance(extra_ctx.get("message"), str)
            else extra_ctx.get("last_user_msg")
            if isinstance(extra_ctx.get("last_user_msg"), str)
            else None
        ),
        question=extra_ctx.get("question") if isinstance(extra_ctx.get("question"), str) else None,
        situation=extra_ctx.get("situation")
        if isinstance(extra_ctx.get("situation"), str)
        else None,
    )
    exec_ctx = ExecutionContext(extra_context=extra_ctx)
    gateway_request = LLMExecutionRequest(
        user_input=user_in,
        context=exec_ctx,
        user_id=current_user.id,
        request_id=request_id,
        trace_id=trace_id,
    )
    gateway = LLMGateway()
    try:
        result = await gateway.execute_request(gateway_request, db=db)
    except InputValidationError as exc:
        logger.warning(
            "admin_manual_llm_execute_failed manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "input_validation",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
            },
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "input_validation",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
            },
        )
    except GatewayConfigError as exc:
        logger.warning(
            "admin_manual_llm_execute_failed manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "gateway_config",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
            },
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "gateway_config",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
            },
        )
    except OutputValidationError as exc:
        logger.warning(
            "admin_manual_llm_execute_output_invalid manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "output_validation",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
            },
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "output_validation",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
                "validation_errors": (exc.details or {}).get("errors"),
            },
        )
    except PromptRenderError as exc:
        logger.warning(
            "admin_manual_llm_execute_prompt_render manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "prompt_render",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
            },
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "prompt_render",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
            },
        )
    except UnknownUseCaseError as exc:
        logger.warning(
            "admin_manual_llm_execute_unknown_use_case manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "unknown_use_case",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
            },
        )
        db.commit()
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "unknown_use_case",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
            },
        )
    except GatewayError as exc:
        logger.warning(
            "admin_manual_llm_execute_failed manifest_entry_id=%s error=%s",
            manifest_entry_id,
            exc.message,
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={
                "failure_kind": "provider_error",
                "error_message": exc.message,
                "error_code": getattr(exc, "error_code", None),
                "gateway_error_class": type(exc).__name__,
            },
        )
        db.commit()
        return _raise_error(
            status_code=502,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=exc.message,
            details={
                "failure_kind": "provider_error",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
                "error_code": getattr(exc, "error_code", None),
                "gateway_error_class": type(exc).__name__,
            },
        )
    except Exception as exc:
        logger.exception(
            "admin_manual_llm_execute_unexpected manifest_entry_id=%s", manifest_entry_id
        )
        _record_admin_manual_execution_audit(
            db,
            request_id=request_id,
            actor=current_user,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            status="failed",
            details={"failure_kind": "unexpected", "error_message": str(exc)},
        )
        db.commit()
        return _raise_error(
            status_code=502,
            request_id=request_id,
            code=AdminLlmErrorCode.ADMIN_MANUAL_EXECUTION_FAILED.value,
            message=str(exc),
            details={
                "failure_kind": "unexpected",
                "manifest_entry_id": manifest_entry_id,
                "sample_payload_id": str(payload.sample_payload_id),
            },
        )
    _record_admin_manual_execution_audit(
        db,
        request_id=request_id,
        actor=current_user,
        manifest_entry_id=manifest_entry_id,
        sample_payload_id=payload.sample_payload_id,
        status="success",
        details={
            "gateway_request_id": result.request_id,
            "provider": result.meta.provider or "openai",
            "model": result.meta.model,
            "validation_status": result.meta.validation_status,
            "latency_ms": result.meta.latency_ms,
        },
    )
    db.commit()
    logger.info(
        (
            "admin_manual_llm_execute_surface=%s event=admin_manual_llm_execute_success "
            "manifest_entry_id=%s sample_payload_id=%s request_id=%s trace_id=%s "
            "operator_user_id=%s gateway_request_id=%s"
        ),
        ADMIN_MANUAL_LLM_EXECUTE_SURFACE,
        manifest_entry_id,
        str(payload.sample_payload_id),
        request_id,
        trace_id,
        current_user.id,
        result.request_id,
    )
    return {
        "data": _build_admin_manual_execute_response_payload(
            built=built,
            result=result,
            manifest_entry_id=manifest_entry_id,
            sample_payload_id=payload.sample_payload_id,
            request_id=request_id,
            trace_id=trace_id,
            use_case_key=built.use_case_key,
        ),
        "meta": ResponseMeta(request_id=request_id),
    }


@router.patch("/use-cases/{key}", response_model=LlmUseCaseListResponse)
def update_use_case_config(
    key: str,
    request: Request,
    payload: UseCaseUpdatePayload,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    del payload, current_user
    if _build_canonical_admin_use_case_config(db, key) is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )
    return _raise_error(
        status_code=409,
        request_id=request_id,
        code=AdminLlmErrorCode.FORBIDDEN_FEATURE.value,
        message=(
            f"use case {key} is governed by the canonical registry. "
            "Legacy DB config writes are frozen."
        ),
        details={},
    )


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
    del payload, current_user
    if _build_canonical_admin_use_case_config(db, key) is None:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )
    return _raise_error(
        status_code=409,
        request_id=request_id,
        code=AdminLlmErrorCode.FORBIDDEN_FEATURE.value,
        message=(
            f"use case {key} persona assignment is derived from canonical governance. "
            "Legacy DB config writes are frozen."
        ),
        details={},
    )


@router.get("/use-cases/{key}/contract", response_model=LlmUseCaseContractResponse)
def get_use_case_contract(
    key: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    if _is_removed_legacy_use_case_key(key):
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )

    canonical_config = _build_canonical_admin_use_case_config(db, key)
    if canonical_config is None:
        uc = get_use_case_config(db, key)
        if not uc:
            return _raise_error(
                status_code=404,
                request_id=request_id,
                code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
                message=f"use case {key} not found",
                details={},
            )

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
            input_schema=None,
            output_schema=output_schema,
            output_schema_id=None,
            persona_strategy="optional",
            safety_profile="astrology",
            required_prompt_placeholders=uc.required_prompt_placeholders,
            active_prompt_version_id=active_prompt.id if active_prompt else None,
        )
    else:
        canonical_contract = get_canonical_use_case_contract(key)
        schema_definition = get_canonical_output_schema_definition(
            canonical_contract.output_schema_name if canonical_contract else None
        )
        contract = LlmUseCaseContract(
            key=canonical_config.key,
            display_name=canonical_config.display_name,
            description=canonical_config.description,
            input_schema=canonical_config.input_schema,
            output_schema=schema_definition.json_schema if schema_definition else None,
            output_schema_id=canonical_config.output_schema_id,
            persona_strategy=canonical_config.persona_strategy,
            safety_profile=canonical_config.safety_profile,
            required_prompt_placeholders=canonical_config.required_prompt_placeholders,
            active_prompt_version_id=canonical_config.active_prompt_version_id,
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

    if _is_removed_legacy_use_case_key(key):
        return {"data": [], "meta": {"request_id": request_id}}

    versions = list_prompt_versions(db, key)

    return {
        "data": [_serialize_prompt_version(db, v) for v in versions],
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

    if _is_removed_legacy_use_case_key(key):
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )

    canonical_uc = _build_canonical_admin_use_case_config(db, key)
    uc = canonical_uc or get_use_case_config(db, key)
    if not uc:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )

    # Story 66.28: Block resurrection of forbidden nominal features (AC5)
    from app.domain.llm.governance.feature_taxonomy import is_nominal_feature_allowed

    if not is_nominal_feature_allowed(key):
        return _raise_error(
            status_code=403,
            request_id=request_id,
            code=AdminLlmErrorCode.FORBIDDEN_FEATURE.value,
            message=f"use case {key} is legacy and frozen. No new drafts allowed.",
            details={},
        )

    if canonical_uc is not None:
        _ensure_admin_use_case_shadow_row(db, canonical_uc)

    previous_version = get_latest_prompt_version(db, key)

    lint_result = PromptLint.lint_prompt(
        payload.developer_prompt, use_case_required_placeholders=uc.required_prompt_placeholders
    )
    if not lint_result.passed:
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.LINT_FAILED.value,
            message="prompt lint validation failed",
            details={"errors": lint_result.errors, "warnings": lint_result.warnings},
        )

    version = LlmPromptVersionModel(
        use_case_key=key,
        status=PromptStatus.DRAFT,
        developer_prompt=payload.developer_prompt,
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
        details={
            "use_case_key": key,
            "from_version": str(previous_version.id) if previous_version else None,
            "to_version": str(version.id),
            "result_status": version.status.value,
        },
    )
    db.commit()

    return {"data": _serialize_prompt_version(db, version), "meta": {"request_id": request_id}}


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
    if _is_removed_legacy_use_case_key(key):
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )
    previous_published = PromptRegistryV2.get_active_prompt(db, key)

    canonical_uc = _build_canonical_admin_use_case_config(db, key)
    uc = canonical_uc or get_use_case_config(db, key)
    if not uc:
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
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
            return _raise_error(
                status_code=409,
                request_id=request_id,
                code=AdminLlmErrorCode.EVAL_FAILED.value,
                message=f"Evaluation failure rate ({eval_report.failure_rate:.2%}) exceeds threshold ({uc.eval_failure_threshold:.2%})",  # noqa: E501
                details=eval_report.model_dump(),
            )

    golden_report = None
    if uc.golden_set_path:
        from app.ops.llm.services import GoldenRegressionService

        golden_report = await GoldenRegressionService.run_campaign(
            use_case_key=key,
            prompt_version_id=str(version_id),
            golden_set_path=uc.golden_set_path,
            db=db,
        )
        # AC21: Block on 'fail' or 'invalid' (High fix)
        if golden_report.verdict in ("fail", "invalid"):
            return _raise_error(
                status_code=409,
                request_id=request_id,
                code=AdminLlmErrorCode.GOLDEN_REGRESSION_FAILED.value,
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
                "from_version": str(previous_published.id) if previous_published else None,
                "to_version": str(version.id),
                "result_status": version.status.value,
                "eval_run": eval_report is not None,
                "golden_campaign": golden_report is not None,
                "golden_verdict": golden_report.verdict if golden_report else None,
            },
        )
        db.commit()

        return {
            "data": _serialize_prompt_version(db, version),
            "meta": {
                "request_id": request_id,
                "warnings": warnings,
                "eval_report": eval_report.model_dump() if eval_report else None,
                "golden_report": golden_report.model_dump() if golden_report else None,
            },
        }

    except ValueError as err:
        from app.domain.llm.governance.feature_taxonomy import is_nominal_feature_allowed

        if not is_nominal_feature_allowed(key):
            return _raise_error(
                status_code=403,
                request_id=request_id,
                code=AdminLlmErrorCode.FORBIDDEN_FEATURE.value,
                message=str(err),
                details={},
            )
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.VALIDATION_ERROR.value,
            message=str(err),
            details={},
        )
    except Exception as err:
        logger.exception("admin_llm_publish_failed")
        return _raise_error(
            status_code=500,
            request_id=request_id,
            code=AdminLlmErrorCode.PUBLISH_FAILED.value,
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

    if _is_removed_legacy_use_case_key(key):
        return _raise_error(
            status_code=404,
            request_id=request_id,
            code=AdminLlmErrorCode.USE_CASE_NOT_FOUND.value,
            message=f"use case {key} not found",
            details={},
        )
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
                "result_status": version.status.value,
            },
        )
        db.commit()

        return {
            "data": _serialize_prompt_version(db, version).model_dump(mode="json"),
            "meta": {"request_id": request_id},
        }
    except ValueError as err:
        from app.domain.llm.governance.feature_taxonomy import is_nominal_feature_allowed

        if not is_nominal_feature_allowed(key):
            return _raise_error(
                status_code=403,
                request_id=request_id,
                code=AdminLlmErrorCode.FORBIDDEN_FEATURE.value,
                message=str(err),
                details={},
            )
        return _raise_error(
            status_code=422,
            request_id=request_id,
            code=AdminLlmErrorCode.ROLLBACK_FAILED.value,
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
        stmt = stmt.where(_call_log_scope_filter(use_case))
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
        "data": [LlmCallLog.model_validate(log, from_attributes=True) for log in logs],
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

    since = datetime_provider.utcnow() - timedelta(hours=period_hours)
    feature_stmt = (
        select(LlmCallLogModel.feature)
        .where(and_(LlmCallLogModel.timestamp >= since, LlmCallLogModel.feature.is_not(None)))
        .distinct()
    )
    use_cases = [value for value in db.execute(feature_stmt).scalars().all() if value]
    legacy_removed_count = (
        db.execute(
            select(func.count(LlmCallLogModel.id)).where(
                and_(LlmCallLogModel.timestamp >= since, _legacy_removed_call_log_filter())
            )
        ).scalar()
        or 0
    )
    if legacy_removed_count:
        use_cases.append("legacy_removed")

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
        ).where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))

        stats = db.execute(base_stmt).first()
        count = stats.count or 0
        if count == 0:
            continue

        dist_stmt = (
            select(LlmCallLogModel.validation_status, func.count(LlmCallLogModel.id))
            .where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
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
            ).where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
            p95 = db.execute(p95_stmt).scalar() or 0
        else:
            # SQLite fallback (in-memory)
            latencies_stmt = (
                select(LlmCallLogModel.latency_ms)
                .where(and_(LlmCallLogModel.timestamp >= since, _call_log_scope_filter(uc)))
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
        return _raise_error(
            status_code=403 if "disabled" in str(e) else 400,
            request_id=request_id,
            code=AdminLlmErrorCode.REPLAY_FAILED.value,
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
