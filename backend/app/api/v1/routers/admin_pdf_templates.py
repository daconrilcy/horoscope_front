from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/pdf-templates", tags=["admin-pdf-templates"])

PDF_TEMPLATE_CONFIG_DOC = (
    "Optional runtime config for PDF export. "
    "Supported keys: "
    "'max_paragraph_chars' (int, 200..5000) and "
    "'split_paragraphs_enabled' (bool), "
    "'page_budget_lines' (int, 24..60), "
    "'section_head_extra_lines' (int, 0..6), "
    "'paragraph_spacing_lines' (int, 0..3), "
    "'section_tail_spacing_lines' (int, 0..4), "
    "'sections_start_new_page_min_remaining_lines' (int, 0..30), "
    "'sections_start_new_page' (bool), "
    "'pagination_debug' (bool). "
    "Note: sections_start_new_page is best-effort and is applied only when "
    "remaining lines after intro are below sections_start_new_page_min_remaining_lines. "
    "Warning: when split_paragraphs_enabled=false, long text may be cut across pages more often."
)


class PdfTemplateCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    locale: str = "fr"
    config_json: dict[str, Any] = Field(default_factory=dict, description=PDF_TEMPLATE_CONFIG_DOC)
    is_default: bool = False


class PdfTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PdfTemplateStatus] = None
    config_json: Optional[dict[str, Any]] = Field(default=None, description=PDF_TEMPLATE_CONFIG_DOC)
    is_default: Optional[bool] = None


class PdfTemplateResponse(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str] = None
    locale: str
    status: PdfTemplateStatus
    version: str
    config_json: dict[str, Any]
    is_default: bool
    created_at: Any
    updated_at: Any


def _ensure_admin_role(user: AuthenticatedUser, request_id: str) -> Optional[JSONResponse]:
    if user.role not in {"admin", "ops"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "Admin or Ops role required",
                    "request_id": request_id,
                    "details": {},
                }
            },
        )
    return None


def _normalize_pdf_template_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(config)

    int_specs = {
        "max_paragraph_chars": (200, 5000),
        "page_budget_lines": (24, 60),
        "section_head_extra_lines": (0, 6),
        "paragraph_spacing_lines": (0, 3),
        "section_tail_spacing_lines": (0, 4),
        "sections_start_new_page_min_remaining_lines": (0, 30),
    }
    for key_name, (min_value, max_value) in int_specs.items():
        if key_name not in normalized:
            continue
        raw_value = normalized[key_name]
        try:
            parsed_value = int(raw_value)
        except (TypeError, ValueError):
            raise ValueError(f"config_json.{key_name} must be an integer")
        if parsed_value < min_value:
            parsed_value = min_value
        if parsed_value > max_value:
            parsed_value = max_value
        normalized[key_name] = parsed_value

    bool_keys = {
        "split_paragraphs_enabled",
        "sections_start_new_page",
        "pagination_debug",
    }
    for key in bool_keys:
        if key not in normalized:
            continue
        raw = normalized[key]
        if isinstance(raw, bool):
            continue
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                normalized[key] = True
                continue
            if lowered in {"0", "false", "no", "off"}:
                normalized[key] = False
                continue
        if isinstance(raw, (int, float)) and raw in {0, 1}:
            normalized[key] = bool(raw)
            continue
        raise ValueError(
            f"config_json.{key} must be a boolean (accepted: true/false, 1/0, yes/no, on/off)"
        )

    return normalized


@router.get("", response_model=list[PdfTemplateResponse])
def list_templates(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_admin_role(current_user, request_id)
    if role_error:
        return role_error

    stmt = select(PdfTemplateModel).order_by(PdfTemplateModel.key)
    items = db.execute(stmt).scalars().all()
    return items


@router.post("", response_model=PdfTemplateResponse)
def create_template(
    request: Request,
    body: PdfTemplateCreate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_admin_role(current_user, request_id)
    if role_error:
        return role_error

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
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_admin_role(current_user, request_id)
    if role_error:
        return role_error

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
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_admin_role(current_user, request_id)
    if role_error:
        return role_error

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
