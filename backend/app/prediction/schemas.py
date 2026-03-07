from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class EngineInput:
    """Canonical input for the prediction engine."""

    natal_chart: dict[str, Any]
    local_date: date
    timezone: str
    latitude: float
    longitude: float
    reference_version: str
    ruleset_version: str
    debug_mode: bool = False


@dataclass(frozen=True)
class EffectiveContext:
    """Context derived from input during run."""

    house_system_requested: str
    house_system_effective: str
    timezone: str
    input_hash: str


@dataclass(frozen=True)
class SamplePoint:
    """A point in time during the daily sampling process."""

    ut_time: float
    local_time: datetime


@dataclass(frozen=True)
class AstroEvent:
    """A detected astrological event."""

    event_type: str
    ut_time: float
    local_time: datetime
    body: str | None
    target: str | None
    aspect: str | None
    orb_deg: float | None
    priority: int
    base_weight: float


@dataclass(frozen=True)
class EngineOutput:
    """Final output of the prediction engine run."""

    run_metadata: dict[str, Any]
    effective_context: EffectiveContext
    sampling_timeline: list[SamplePoint] = field(default_factory=list)
    detected_events: list[AstroEvent] = field(default_factory=list)
    category_scores: dict[str, Any] = field(default_factory=dict)
    time_blocks: list[Any] = field(default_factory=list)
    turning_points: list[Any] = field(default_factory=list)
