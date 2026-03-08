from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .explainability import ExplainabilityReport


@dataclass(frozen=True)
class NatalChart:
    """Internal representation of a natal chart for sensitivity calculations."""

    planet_positions: dict[str, float]
    planet_houses: dict[str, int]
    house_sign_rulers: dict[int, str]


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
class PlanetState:
    """State of a planet at a specific time."""

    code: str
    longitude: float
    speed_lon: float
    is_retrograde: bool
    sign_code: int
    natal_house_transited: int


@dataclass(frozen=True)
class StepAstroState:
    """Complete astrological state at a specific time."""

    ut_jd: float
    local_time: datetime
    ascendant_deg: float
    mc_deg: float
    house_cusps: list[float]
    house_system_effective: str
    planets: dict[str, PlanetState]


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
    metadata: dict[str, Any] = field(default_factory=dict)


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
    explainability: ExplainabilityReport | None = None
