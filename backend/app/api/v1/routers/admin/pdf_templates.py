from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
)
from app.api.v1.schemas.routers.admin.pdf_templates import (
    PdfTemplateCreate,
    PdfTemplateResponse,
    PdfTemplateUpdate,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.session import get_db_session
from app.services.natal.admin_pdf_templates import (
    _normalize_pdf_template_config,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/pdf-templates", tags=["admin-pdf-templates"])


@router.get("", response_model=list[PdfTemplateResponse])
def list_templates(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    stmt = select(PdfTemplateModel).order_by(PdfTemplateModel.key)
    items = db.execute(stmt).scalars().all()
    return items


@router.post("", response_model=PdfTemplateResponse)
def create_template(
    request: Request,
    body: PdfTemplateCreate,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    try:
        normalized_config = _normalize_pdf_template_config(body.config_json)
    except ValueError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_template_config",
                    "message": str(exc),
                    "request_id": request_id,
                    "details": {},
                }
            },
        )

    # Check if key already exists
    stmt = select(PdfTemplateModel).where(PdfTemplateModel.key == body.key)
    if db.execute(stmt).scalar_one_or_none():
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "template_already_exists",
                    "message": f"Template with key {body.key} already exists",
                    "request_id": request_id,
                    "details": {},
                }
            },
        )

    if body.is_default:
        # Reset other defaults
        from sqlalchemy import update

        db.execute(update(PdfTemplateModel).values(is_default=False))

    item = PdfTemplateModel(
        key=body.key,
        name=body.name,
        description=body.description,
        locale=body.locale,
        status=PdfTemplateStatus.DRAFT,
        config_json=normalized_config,
        is_default=body.is_default,
        created_by=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{template_id}", response_model=PdfTemplateResponse)
def update_template(
    template_id: int,
    request: Request,
    body: PdfTemplateUpdate,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    item = db.get(PdfTemplateModel, template_id)
    if not item:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "template_not_found",
                    "message": "Template not found",
                    "request_id": request_id,
                    "details": {},
                }
            },
        )

    if body.name is not None:
        item.name = body.name
    if body.description is not None:
        item.description = body.description
    if body.status is not None:
        item.status = body.status
    if body.config_json is not None:
        try:
            item.config_json = _normalize_pdf_template_config(body.config_json)
        except ValueError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "invalid_template_config",
                        "message": str(exc),
                        "request_id": request_id,
                        "details": {},
                    }
                },
            )
    if body.is_default is not None:
        if body.is_default:
            from sqlalchemy import update

            db.execute(update(PdfTemplateModel).values(is_default=False))
        item.is_default = body.is_default

    db.commit()
    db.refresh(item)
    return item


@router.post("/{template_id}/activate", response_model=PdfTemplateResponse)
def activate_template(
    template_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    item = db.get(PdfTemplateModel, template_id)
    if not item:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "template_not_found",
                    "message": "Template not found",
                    "request_id": request_id,
                    "details": {},
                }
            },
        )

    item.status = PdfTemplateStatus.ACTIVE
    db.commit()
    db.refresh(item)
    return item
