from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .editorial_builder import EditorialOutput
    from .editorial_template_engine import EditorialTextOutput


@dataclass(frozen=True)
class NatalChart:
    """Internal representation of a natal chart for sensitivity calculations."""

    planet_positions: dict[str, float]
    planet_houses: dict[str, int]
    house_sign_rulers: dict[int, str]
    natal_aspects: list[AstroEvent] = field(default_factory=list)


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
    local_date: date | None = None


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
class V3SignalLayer:
    """A continuous signal layer for a specific category and time step (AC1)."""

    baseline: float  # B(c): natal structural susceptibility
    transit: float   # T(c,t): transit climate
    aspect: float    # A(c,t): aspect dynamics
    event: float     # E(c,t): event triggers
    composite: float # Final combined signal for this step


@dataclass(frozen=True)
class V3ThemeSignal:
    """Time-series of signal layers for a specific theme (AC1)."""

    theme_code: str
    timeline: dict[datetime, V3SignalLayer]


@dataclass(frozen=True)
class V3DailyMetrics:
    """Daily derived metrics for a theme in v3 (AC1).
    
    All _20 metrics are normalized on a [0, 20] scale.
    """

    score_20: float       # Final calibrated score
    level_day: float      # AC1: Average signal relative to neutral
    intensity_day: float  # AC1: Total energy/relief of the day
    dominance_day: float  # AC1: Asymmetry of peaks
    stability_day: float  # AC1: Signal clarity/reliability
    
    rarity_percentile: float # rarity index on 0-20, not a statistical percentile
    
    # Raw stats (retained for traceability)
    avg_score: float
    max_score: float
    min_score: float
    volatility: float


@dataclass(frozen=True)
class V3TimeBlock:
    """A coherent regime block in V3 (Story 42.9)."""

    block_index: int
    start_local: datetime
    end_local: datetime
    orientation: str  # "rising" | "falling" | "stable" | "volatile"
    intensity: float  # 0-20
    confidence: float # 0-1
    dominant_themes: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass(frozen=True)
class V3TurningPoint:
    """A turning point in V3 (Story 42.10)."""

    local_time: datetime
    reason: str  # "regime_change" | "intensity_jump" | "high_priority_event"
    amplitude: float
    duration_following: float  # minutes
    confidence: float
    categories_impacted: list[str] = field(default_factory=list)
    drivers: list[AstroEvent] = field(default_factory=list)
    summary: str = ""


@dataclass(frozen=True)
class V3EngineOutput:
    """Engine v3 calculation results (AC1).
    
    Attributes:
        engine_version: Explicit version of the calculation logic (AC4)
        snapshot_version: Version of the internal data structure (AC4)
        evidence_pack_version: Version of the traceability format (AC4)
    """

    engine_version: str
    snapshot_version: str
    evidence_pack_version: str
    
    theme_signals: dict[str, V3ThemeSignal] = field(default_factory=dict)
    daily_metrics: dict[str, V3DailyMetrics] = field(default_factory=dict)
    time_blocks: list[V3TimeBlock] = field(default_factory=list)
    turning_points: list[V3TurningPoint] = field(default_factory=list)
    
    run_metadata: dict[str, Any] = field(default_factory=dict)
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class DecisionWindow:
    """A decisional window produced by the prediction engine."""

    start_local: datetime
    end_local: datetime
    window_type: str  # "favorable" | "prudence" | "pivot"
    score: float  # avg note of dominant categories, 0-20
    confidence: float  # 0-1, inverse of volatility
    dominant_categories: list[str]
@dataclass(frozen=True)
class BestWindow:
    start_local: datetime
    end_local: datetime
    dominant_category: str


@dataclass(frozen=True)
class CategorySummary:
    code: str
    note_20: int
    power: float
    volatility: float


@dataclass(frozen=True)
class EditorialOutput:
    local_date: date
    top3_categories: list[CategorySummary]
    bottom2_categories: list[CategorySummary]
    main_pivot: Any | None  # TurningPoint
    best_window: BestWindow | None
    caution_flags: dict[str, bool]
    overall_tone: str
    top3_contributors_per_category: dict[str, list[Any]] # ContributorEntry


@dataclass(frozen=True)
class EditorialTextOutput:
    """Final rendered editorial texts."""

    intro: str
    category_summaries: dict[str, str]
    pivot_phrase: str | None
    window_phrase: str | None
    caution_sante: str | None
    caution_argent: str | None
    time_block_summaries: list[str] = field(default_factory=list)
    turning_point_summaries: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoreEngineOutput:
    """Raw calculation results from the engine, without editorial text."""

    effective_context: EffectiveContext
    run_metadata: dict[str, Any]
    category_scores: dict[str, Any]
    time_blocks: list[Any]
    turning_points: list[Any]
    decision_windows: list[DecisionWindow]
    detected_events: list[AstroEvent] = field(default_factory=list)
    sampling_timeline: list[SamplePoint] = field(default_factory=list)
    explainability: Any | None = None # ExplainabilityReport


@dataclass(frozen=True)
class EditorialOutputBundle:
    """Data and rendered texts for editorial presentation."""

    data: EditorialOutput
    text: EditorialTextOutput

    def __getattr__(self, name: str) -> Any:
        if hasattr(self.data, name):
            return getattr(self.data, name)
        if hasattr(self.text, name):
            return getattr(self.text, name)
        raise AttributeError(name)


@dataclass(frozen=True)
class PersistablePredictionBundle:
    """Complete bundle ready for persistence."""

    core: CoreEngineOutput
    editorial: EditorialOutputBundle | None = None
    v3_core: V3EngineOutput | None = None  # AC1

    @property
    def editorial_text(self) -> "EditorialTextOutput | None":
        if self.editorial is None:
            return None
        return self.editorial.text

    def to_engine_output(self) -> "EngineOutput":
        """Build a legacy aggregate view for callers not yet migrated to the bundle API."""
        run_metadata = dict(self.core.run_metadata)
        if self.editorial is not None:
            run_metadata.setdefault("overall_tone", self.editorial.data.overall_tone)
            run_metadata.setdefault("overall_summary", self.editorial.text.intro)

        return EngineOutput(
            run_metadata=run_metadata,
            effective_context=self.core.effective_context,
            sampling_timeline=list(self.core.sampling_timeline),
            detected_events=list(self.core.detected_events),
            category_scores=dict(self.core.category_scores),
            time_blocks=list(self.core.time_blocks),
            turning_points=list(self.core.turning_points),
            explainability=self.core.explainability,
            editorial=self.editorial.data if self.editorial is not None else None,
            editorial_text=self.editorial.text if self.editorial is not None else None,
            decision_windows=list(self.core.decision_windows),
        )

    def __getattr__(self, name: str) -> Any:
        if name == "run_metadata":
            return self.to_engine_output().run_metadata
        if name == "editorial_text":
            return self.editorial_text
        if hasattr(self.core, name):
            return getattr(self.core, name)
        raise AttributeError(name)


@dataclass(frozen=True)
class EngineOutput:
    """Final output of the prediction engine run. (Aggregator for backward compatibility)"""

    run_metadata: dict[str, Any]
    effective_context: EffectiveContext
    sampling_timeline: list[SamplePoint] = field(default_factory=list)
    detected_events: list[AstroEvent] = field(default_factory=list)
    category_scores: dict[str, Any] = field(default_factory=dict)
    time_blocks: list[Any] = field(default_factory=list)
    turning_points: list[Any] = field(default_factory=list)
    explainability: Any | None = None # ExplainabilityReport
    editorial: EditorialOutput | None = None
    editorial_text: EditorialTextOutput | None = None
    decision_windows: list[Any] = field(default_factory=list)
