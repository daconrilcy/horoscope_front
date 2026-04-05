from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class DatePeriod(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class AdminExportRequest(BaseModel):
    period: DatePeriod | None = None


class AdminGenerationExportRequest(AdminExportRequest):
    format: str = "csv" # csv, json
