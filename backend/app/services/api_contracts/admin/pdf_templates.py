"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.api_constants import PDF_TEMPLATE_CONFIG_DOC
from app.infra.db.models.pdf_template import PdfTemplateStatus


class PdfTemplateCreate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    name: str
    description: Optional[str] = None
    locale: str = "fr"
    config_json: dict[str, Any] = Field(default_factory=dict, description=PDF_TEMPLATE_CONFIG_DOC)
    is_default: bool = False


class PdfTemplateUpdate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PdfTemplateStatus] = None
    config_json: Optional[dict[str, Any]] = Field(default=None, description=PDF_TEMPLATE_CONFIG_DOC)
    is_default: Optional[bool] = None


class PdfTemplateResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
