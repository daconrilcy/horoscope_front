from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PersistedRelativeScore:
    """
    Relative scoring metrics for a specific category, calculated against a user's baseline.
    AC1 Compliance: Robust, typed relative metrics.
    """

    category_code: str
    
    # Statistics
    relative_z_score: float | None  # (raw - mean) / std. None if std == 0 or baseline missing
    relative_percentile: float | None  # 0.0 - 1.0. Based on percentiles in baseline
    relative_rank: int | None  # 1 to N, 1 being the highest relative score of the day
    
    # Metadata for fallback/audit
    is_available: bool
    # e.g. "baseline_missing", "variance_null", "sample_too_small"
    fallback_reason: str | None = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
