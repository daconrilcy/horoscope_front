from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
)
from app.core.request_id import resolve_request_id
from app.core.sensitive_data import Sink, sanitize_payload
from app.infra.db.models.billing import UserSubscriptionModel
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
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
from app.llm_orchestration.persona_boundary import (
    PersonaBoundaryViolation,
    validate_persona_block,
)
from app.llm_orchestration.policies.hard_policy import get_hard_policy
from app.llm_orchestration.services.eval_harness import run_eval
from app.llm_orchestration.services.observability_service import purge_expired_logs
from app.llm_orchestration.services.persona_composer import compose_persona_block
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2
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
    details: dict[str, object],
) -> None:
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
            details=details,
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
                active_prompt_version_id=active_prompt.id if active_prompt else None,
            )
        )

    return {"data": result_data, "meta": {"request_id": request_id}}


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

    try:
        version = PromptRegistryV2.publish_prompt(db, version_id)

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_prompt_publish",
            target_type="llm_prompt",
            target_id=str(version.id),
            status="success",
            details={"use_case_key": key, "eval_run": eval_report is not None},
        )
        db.commit()

        return {
            "data": LlmPromptVersion.model_validate(version),
            "meta": {
                "request_id": request_id,
                "eval_report": eval_report.model_dump() if eval_report else None,
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
            status_code=404,
            request_id=request_id,
            code="prompt_not_found",
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

        from app.schemas.audit_details import LlmPromptAuditDetails

        _record_audit_event(
            db,
            request_id=request_id,
            actor=current_user,
            action="llm_prompt_rollback",
            target_type="llm_prompt",
            target_id=str(version.id),
            status="success",
            details=LlmPromptAuditDetails(
                use_case_key=key,
                from_version=str(previous_version.id) if previous_version else None,
                to_version=str(version.id),
            ),
        )
        db.commit()

        return {
            "data": LlmPromptVersion.model_validate(version),
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
