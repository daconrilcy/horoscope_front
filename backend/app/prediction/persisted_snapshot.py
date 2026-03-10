from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from types import SimpleNamespace
from typing import Any


@dataclass(frozen=True)
class PersistedCategoryScore:
    category_id: int
    category_code: str
    note_20: int
    raw_score: float
    power: float
    volatility: float
    rank: int
    is_provisional: bool
    summary: str | None
    contributors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def category(self) -> SimpleNamespace:
        return SimpleNamespace(code=self.category_code)

    @property
    def contributors_json(self) -> str:
        return json.dumps(self.contributors, ensure_ascii=True, separators=(",", ":"))

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class PersistedTurningPoint:
    occurred_at_local: datetime
    severity: float
    summary: str | None
    drivers: list[dict[str, Any]] = field(default_factory=list)

    @property
    def driver_json(self) -> str:
        return json.dumps(self.drivers, ensure_ascii=True, separators=(",", ":"))

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class PersistedTimeBlock:
    block_index: int
    start_at_local: datetime
    end_at_local: datetime
    tone_code: str
    dominant_categories: list[str]
    summary: str | None

    @property
    def dominant_categories_json(self) -> str:
        return json.dumps(
            self.dominant_categories,
            ensure_ascii=True,
            separators=(",", ":"),
        )

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class PersistedPredictionSnapshot:
    """
    Typed snapshot of a prediction run as retrieved from persistence.
    Decouples domain logic from SQLAlchemy models and dict-based storage.
    """

    run_id: int
    user_id: int
    local_date: date
    timezone: str
    computed_at: datetime
    input_hash: str | None
    reference_version_id: int
    ruleset_id: int
    house_system_effective: str | None
    is_provisional_calibration: bool
    calibration_label: str | None
    overall_summary: str | None
    overall_tone: str | None

    category_scores: list[PersistedCategoryScore] = field(default_factory=list)
    turning_points: list[PersistedTurningPoint] = field(default_factory=list)
    time_blocks: list[PersistedTimeBlock] = field(default_factory=list)

    @property
    def id(self) -> int:
        return self.run_id

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get_category_note(self, code: str) -> int | None:
        for s in self.category_scores:
            if s.category_code == code:
                return s.note_20
        return None
