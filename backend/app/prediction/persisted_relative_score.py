from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PersistedRelativeScore:
    """
    Relative scoring metrics for a specific category, calculated against a user's baseline.
    AC1 Compliance: Robust, typed relative metrics.
    V3: granular baselines (day, slot, season).
    """

    category_code: str
    
    # V2 Fields (keeping for compatibility)
    relative_z_score: float | None  # (raw - mean) / std. None if std == 0 or baseline missing
    relative_percentile: float | None  # 0.0 - 1.0. Based on percentiles in baseline
    relative_rank: int | None  # 1 to N, 1 being the highest relative score of the day

    # V3 Granular Fields
    z_abs: float | None    # Z-score vs Day baseline
    z_slot: float | None   # Z-score vs Slot baseline
    z_season: float | None # Z-score vs Season baseline
    pct_abs: float | None  # Percentile vs Day baseline
    pct_rel: float | None  # Percentile vs Slot baseline
    pct_season: float | None # Percentile vs Season baseline
    rarity: float | None   # Frequency/Rarity indicator (e.g. 1 - abs(percentile - 0.5) * 2 or similar)
    
    # Metadata for fallback/audit
    is_available: bool
    # e.g. "baseline_missing", "variance_null", "sample_too_small"
    fallback_reason: str | None = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
