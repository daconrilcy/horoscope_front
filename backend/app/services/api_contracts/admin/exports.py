"""Schemas Pydantic des endpoints admin d'exports."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DatePeriod(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    start: datetime | None = None
    end: datetime | None = None


class AdminExportRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    period: DatePeriod | None = None


class AdminGenerationExportRequest(AdminExportRequest):
    """Contrat Pydantic exposé par l'API."""

    format: Literal["csv", "json"] = "csv"
