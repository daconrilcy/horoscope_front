from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


class V3Granularity(str, Enum):
    DAY = "day"
    SLOT = "slot"
    SEASON = "season"
    MONTH = "month"


@dataclass(frozen=True)
class PersistedUserBaseline:
    id: int
    user_id: int
    category_id: int
    category_code: str
    reference_version_id: int
    ruleset_id: int
    house_system_effective: str
    window_days: int
    window_start_date: date
    window_end_date: date

    mean_raw_score: float
    std_raw_score: float
    mean_note_20: float
    std_note_20: float

    p10: float
    p50: float
    p90: float

    sample_size_days: int
    computed_at: datetime
    
    granularity_type: str = "day"
    granularity_value: str = "all"

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
