from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.routers.admin_llm_error_codes import AdminLlmErrorCode
from app.domain.llm.configuration.admin_models import (
    DraftPublishResponse,
    PromptAssemblyConfig,
    PromptAssemblyPreview,
)
from app.domain.llm.configuration.assembly_admin_service import AssemblyAdminService
from app.domain.llm.configuration.coherence import CoherenceError
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/admin/llm/assembly", tags=["admin-llm-assembly"])


class ResponseMeta(BaseModel):
    request_id: str
    warnings: List[str] = Field(default_factory=list)


class AssemblyConfigListResponse(BaseModel):
    data: List[PromptAssemblyConfig]
    meta: ResponseMeta


class AssemblyConfigResponse(BaseModel):
    data: PromptAssemblyConfig
    meta: ResponseMeta


class AssemblyPreviewResponse(BaseModel):
    data: PromptAssemblyPreview
    meta: ResponseMeta


class AssemblyPublishApiResponse(BaseModel):
    data: DraftPublishResponse
    meta: ResponseMeta


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


@router.get("/configs", response_model=AssemblyConfigListResponse)
async def list_assembly_configs(
    request: Request,
    feature: Optional[str] = None,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """List all assembly configurations."""
    service = AssemblyAdminService(db)
    configs = await service.list_configs(feature=feature)

    return {
        "data": [PromptAssemblyConfig.model_validate(c) for c in configs],
        "meta": {"request_id": request.state.request_id},
    }


@router.post("/configs", response_model=AssemblyConfigResponse)
async def create_assembly_config(
    request: Request,
    config_in: PromptAssemblyConfig,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """Create a new assembly configuration draft."""
    service = AssemblyAdminService(db)
    new_config = await service.create_draft(config_in, created_by=admin.email)

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        admin.id,
        AuditEventCreatePayload(
            event_type="llm_assembly_config_created",
            target_type="llm_assembly_config",
            target_id=str(new_config.id),
            details={
                "feature": new_config.feature,
                "subfeature": new_config.subfeature,
                "plan": new_config.plan,
            },
        ),
    )

    return {
        "data": PromptAssemblyConfig.model_validate(new_config),
        "meta": {"request_id": request.state.request_id},
    }


@router.get("/configs/{config_id}", response_model=AssemblyConfigResponse)
async def get_assembly_config(
    request: Request,
    config_id: uuid.UUID,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """Get a specific assembly configuration."""
    service = AssemblyAdminService(db)
    config = await service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    return {
        "data": PromptAssemblyConfig.model_validate(config),
        "meta": {"request_id": request.state.request_id},
    }


@router.post("/configs/{config_id}/publish", response_model=AssemblyPublishApiResponse)
async def publish_assembly_config(
    request: Request,
    config_id: uuid.UUID,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """Publish an assembly configuration."""
    service = AssemblyAdminService(db)
    try:
        config, archived_count = await service.publish_config(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if isinstance(e, CoherenceError):
            return _error_response(
                status_code=400,
                request_id=request.state.request_id,
                code=AdminLlmErrorCode.COHERENCE_VALIDATION_FAILED.value,
                message="assembly coherence validation failed",
                details={"errors": [err.model_dump() for err in e.result.errors]},
            )
        raise e
    audit_service = AuditService(db)
    await audit_service.log_event(
        admin.id,
        AuditEventCreatePayload(
            event_type="llm_assembly_config_published",
            target_type="llm_assembly_config",
            target_id=str(config.id),
            details={
                "feature": config.feature,
                "subfeature": config.subfeature,
                "plan": config.plan,
                "archived_count": archived_count,
            },
        ),
    )

    return {
        "data": DraftPublishResponse(
            assembly_id=config.id,
            status=str(config.status),
            published_at=config.published_at,
            archived_count=archived_count,
        ),
        "meta": {"request_id": request.state.request_id},
    }


@router.post("/configs/{config_id}/rollback", response_model=AssemblyConfigResponse)
async def rollback_assembly_config(
    request: Request,
    config_id: uuid.UUID,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """Rollback to an archived assembly configuration."""
    service = AssemblyAdminService(db)
    try:
        # We need to fetch the archived config first to get target params
        target_config = await service.get_config(config_id)
        if not target_config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        config = await service.rollback_config(
            feature=target_config.feature,
            subfeature=target_config.subfeature,
            plan=target_config.plan,
            locale=target_config.locale,
            target_id=config_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        admin.id,
        AuditEventCreatePayload(
            event_type="llm_assembly_config_rollbacked",
            target_type="llm_assembly_config",
            target_id=str(config.id),
            details={
                "feature": config.feature,
                "subfeature": config.subfeature,
                "plan": config.plan,
            },
        ),
    )

    return {
        "data": PromptAssemblyConfig.model_validate(config),
        "meta": {"request_id": request.state.request_id},
    }


@router.get("/configs/{config_id}/preview", response_model=AssemblyPreviewResponse)
async def preview_assembly_config(
    request: Request,
    config_id: uuid.UUID,
    db=Depends(get_db_session),
    admin: AuthenticatedUser = Depends(require_admin_user),
):
    """Get a full preview of the assembly rendering."""
    service = AssemblyAdminService(db)
    try:
        preview = await service.get_assembly_preview(config_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"data": preview, "meta": {"request_id": request.state.request_id}}
