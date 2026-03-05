from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class PdfTemplateStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PdfTemplateModel(Base):
    """
    Stores PDF templates for natal interpretations and other exports.
    """

    __tablename__ = "pdf_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="fr", index=True)
    
    status: Mapped[PdfTemplateStatus] = mapped_column(
        SqlEnum(PdfTemplateStatus), default=PdfTemplateStatus.DRAFT, index=True
    )
    
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    
    # JSON configuration for the template (e.g., fonts, colors, layout options)
    config_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
