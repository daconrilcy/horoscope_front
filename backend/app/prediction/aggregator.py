import math
import statistics
from dataclasses import dataclass, field

from .schemas import V3DailyMetrics, V3ThemeSignal

RAW_STEP_MAX = 3.0
RAW_DAY_MAX = 2.0
PEAK90_WINDOW = 6
CLOSE_WINDOW = 8

# V3 Mapping Constants
SCORE_CENTER = 1.0
SCORE_SCALE = 5.0
INTENSITY_MAX_RAW = 1.5
RARITY_MAX_RAW = 2.5
BASELINE_TARGET = 0.5


@dataclass
class CategoryAggregation:
# ... (rest of CategoryAggregation remains same)
    category_code: str
    raw_steps: list[float] = field(default_factory=list)
    mean: float = 0.0
    peak90: float = 0.0
    close: float = 0.0
    raw_day: float = 0.0
    power: float = 0.0
    volatility: float = 0.0


@dataclass
class DayAggregation:
    categories: dict[str, CategoryAggregation] = field(default_factory=dict)


class V3ThemeAggregator:
    """
    Aggregator for V3 theme signals into four product dimensions (AC1, AC2, AC3, AC4).
    """

    def aggregate_theme(self, theme_signal: V3ThemeSignal) -> V3DailyMetrics:
        """Derives score, intensity, confidence and rarity from timeline."""
        layers = list(theme_signal.timeline.values())
        if not layers:
            return V3DailyMetrics(
                score_20=10.0, intensity_20=0.0, confidence_20=0.0, rarity_percentile=0.0,
                avg_score=0.0, max_score=0.0, min_score=0.0, volatility=0.0
            )

        composites = [L.composite for L in layers]
        
        # 1. Stats de base
        avg_val = statistics.mean(composites)
        max_val = max(composites)
        min_val = min(composites)
        vol_val = statistics.stdev(composites) if len(composites) > 1 else 0.0

        # 2. score_20 (AC2)
        # Baseline is around 1.0. T, A, E range typically [-2, 2]
        # Composite range [ -3, 5 ]. Map [ -1, 3 ] to [ 0, 20 ]
        # center 1.0 -> 10/20
        score = 10.0 + (avg_val - SCORE_CENTER) * SCORE_SCALE
        score = max(0.0, min(20.0, score))

        # 3. intensity_20 (AC1)
        # Mean absolute deviation of the "dynamic" part (T+A+E)
        dynamics = [abs(L.composite - L.baseline) for L in layers]
        avg_dynamic = statistics.mean(dynamics)
        intensity = (avg_dynamic / INTENSITY_MAX_RAW) * 20.0
        intensity = max(0.0, min(20.0, intensity))

        # 4. confidence_20 (AC3)
        # Stability: inverse of volatility
        stability_score = 1.0 / (1.0 + vol_val)
        
        # Baseline quality: is the natal structural signal strong enough?
        baseline_quality = min(1.0, abs(layers[0].baseline) / BASELINE_TARGET)
        
        # Coherence inter-drivers: do T, A, E point in the same direction?
        avg_t = statistics.mean([L.transit for L in layers])
        avg_a = statistics.mean([L.aspect for L in layers])
        avg_e = statistics.mean([L.event for L in layers])
        drivers = [avg_t, avg_a, avg_e]
        signs = [math.copysign(1, d) for d in drivers if abs(d) > 0.05]
        coherence = 1.0 if not signs or all(s == signs[0] for s in signs) else 0.6
        
        conf_raw = (stability_score * 0.7 + baseline_quality * 0.2 + coherence * 0.1) * 20.0
        confidence = max(0.0, min(20.0, conf_raw))

        # 5. rarity_percentile (AC4)
        # Measure of "how far from the norm (1.0)" is the peak relief
        # We use a non-linear mapping to simulate a percentile behavior
        peak_relief = max(abs(max_val - SCORE_CENTER), abs(min_val - SCORE_CENTER))
        
        # Sigmoid-like mapping to make it "distinguished from simple relative"
        # 0.0 -> 0.0, 1.0 -> 10.0, 2.5 -> 18.0, 4.0 -> 20.0
        rarity = 20.0 if peak_relief >= 3.0 else 20.0 * (1.0 - math.exp(-peak_relief / 1.1))
        rarity = max(0.0, min(20.0, rarity))

        return V3DailyMetrics(
            score_20=score,
            intensity_20=intensity,
            confidence_20=confidence,
            rarity_percentile=rarity,
            avg_score=avg_val,
            max_score=max_val,
            min_score=min_val,
            volatility=vol_val
        )


class TemporalAggregator:
    def aggregate(
        self, contributions_by_step: list[dict[str, float]], category_codes: list[str]
    ) -> DayAggregation:
        """
        Aggregates contributions into RawStep and then calculates RawDay metrics.

        contributions_by_step: list of dicts where each dict is
                               {category_code: total_contribution} for a step.
        category_codes: list of categories to aggregate.
        """
        day_agg = DayAggregation()

        for code in category_codes:
            # AC1: RawStep(c,t) clamped [-3, +3]
            # If a step is missing from contributions_by_step, it counts as 0.0
            steps = [
                max(-RAW_STEP_MAX, min(RAW_STEP_MAX, step_data.get(code, 0.0)))
                for step_data in contributions_by_step
            ]

            if not steps:
                # Handle empty case (AC6, AC7)
                day_agg.categories[code] = CategoryAggregation(category_code=code)
                continue

            # AC2: Mean(c)
            mean_val = statistics.mean(steps)

            # AC3: Peak90(c)
            peak90_val = self._peak90(steps)

            # AC4: Close(c) = mean of last CLOSE_WINDOW steps
            close_steps = steps[-CLOSE_WINDOW:]
            close_val = statistics.mean(close_steps)

            # AC5: RawDay(c) formula V1 clamped [-2.0, +2.0]
            raw_day_raw = (0.70 * mean_val) + (0.20 * peak90_val) + (0.10 * close_val)
            raw_day_val = max(-RAW_DAY_MAX, min(RAW_DAY_MAX, raw_day_raw))

            # AC6: Power(c) and Vol(c)
            power_val = max(abs(s) for s in steps)
            vol_val = statistics.stdev(steps) if len(steps) > 1 else 0.0

            day_agg.categories[code] = CategoryAggregation(
                category_code=code,
                raw_steps=steps,
                mean=mean_val,
                peak90=peak90_val,
                close=close_val,
                raw_day=raw_day_val,
                power=power_val,
                volatility=vol_val,
            )

        return day_agg

    def _peak90(self, steps: list[float]) -> float:
        """Calculates the maximum of the moving average over PEAK90_WINDOW steps."""
        if not steps:
            return 0.0
        if len(steps) < PEAK90_WINDOW:
            return statistics.mean(steps)

        return max(
            statistics.mean(steps[i : i + PEAK90_WINDOW])
            for i in range(len(steps) - PEAK90_WINDOW + 1)
        )
