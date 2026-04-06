from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DatePeriod(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class AdminExportRequest(BaseModel):
    period: DatePeriod | None = None


class AdminGenerationExportRequest(AdminExportRequest):
    format: Literal["csv", "json"] = "csv"
