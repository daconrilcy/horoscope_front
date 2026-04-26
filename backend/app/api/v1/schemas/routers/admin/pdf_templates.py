"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
from typing import Any, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_admin_user,
)
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
