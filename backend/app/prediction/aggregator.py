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
INTENSITY_MAX_RAW = 1.25
RARITY_SATURATION_RELIEF = 3.0
SMOOTHING_WINDOW = 3
MIN_SIGNAL_THRESHOLD = 0.05
BASELINE_EXPECTED = 1.0
BASELINE_TOLERANCE = 1.2


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

        composites = [layer.composite for layer in layers]
        baselines = [layer.baseline for layer in layers]
        dynamic_values = [layer.composite - layer.baseline for layer in layers]
        driver_energy = [
            abs(layer.transit) + abs(layer.aspect) + abs(layer.event) for layer in layers
        ]

        smoothed_composites = self._smooth_series(composites)
        smoothed_dynamics = self._smooth_series(dynamic_values)

        avg_val = statistics.mean(smoothed_composites)
        max_val = max(smoothed_composites)
        min_val = min(smoothed_composites)
        vol_val = statistics.stdev(smoothed_composites) if len(smoothed_composites) > 1 else 0.0

        score = 10.0 + (avg_val - SCORE_CENTER) * SCORE_SCALE
        score = max(0.0, min(20.0, score))

        avg_dynamic = statistics.mean(abs(value) for value in smoothed_dynamics)
        peak_dynamic = max(abs(value) for value in smoothed_dynamics)
        intensity_raw = (avg_dynamic * 0.65) + (peak_dynamic * 0.35)
        intensity = (intensity_raw / INTENSITY_MAX_RAW) * 20.0
        intensity = max(0.0, min(20.0, intensity))

        explained_signal = self._explained_signal_share(
            raw_dynamic_values=dynamic_values,
            smoothed_dynamic_values=smoothed_dynamics,
            driver_energy=driver_energy,
        )
        stability_score = self._stability_score(composites, smoothed_composites)
        baseline_quality = self._baseline_quality(baselines)

        avg_t = statistics.mean(layer.transit for layer in layers)
        avg_a = statistics.mean(layer.aspect for layer in layers)
        avg_e = statistics.mean(layer.event for layer in layers)
        drivers = [avg_t, avg_a, avg_e]
        signs = [
            math.copysign(1, driver)
            for driver in drivers
            if abs(driver) > MIN_SIGNAL_THRESHOLD
        ]
        if not signs:
            coherence = 0.75
        elif all(s == signs[0] for s in signs):
            coherence = 1.0
        else:
            coherence = 0.55

        conf_raw = (
            explained_signal * 0.40
            + stability_score * 0.40
            + baseline_quality * 0.10
            + coherence * 0.10
        ) * 20.0
        confidence = max(0.0, min(20.0, conf_raw))

        peak_relief = max(abs(max_val - SCORE_CENTER), abs(min_val - SCORE_CENTER))
        rarity = self._rarity_score(peak_relief, avg_dynamic)
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

    def _smooth_series(self, values: list[float]) -> list[float]:
        if len(values) <= 2:
            return list(values)

        radius = max(1, SMOOTHING_WINDOW // 2)
        smoothed: list[float] = []
        for index in range(len(values)):
            start = max(0, index - radius)
            end = min(len(values), index + radius + 1)
            smoothed.append(statistics.mean(values[start:end]))
        return smoothed

    def _explained_signal_share(
        self,
        *,
        raw_dynamic_values: list[float],
        smoothed_dynamic_values: list[float],
        driver_energy: list[float],
    ) -> float:
        smoothed_energy = statistics.mean(abs(value) for value in smoothed_dynamic_values)
        raw_energy = statistics.mean(abs(value) for value in raw_dynamic_values)
        available_energy = statistics.mean(driver_energy)

        if raw_energy <= MIN_SIGNAL_THRESHOLD and available_energy <= MIN_SIGNAL_THRESHOLD:
            return 1.0
        if available_energy <= MIN_SIGNAL_THRESHOLD:
            return 0.0

        structured_share = smoothed_energy / max(raw_energy, MIN_SIGNAL_THRESHOLD)
        attributed_share = raw_energy / max(available_energy, MIN_SIGNAL_THRESHOLD)
        return max(0.0, min(1.0, (structured_share * 0.7) + (attributed_share * 0.3)))

    def _stability_score(
        self,
        raw_values: list[float],
        smoothed_values: list[float],
    ) -> float:
        smoothed_volatility = statistics.stdev(smoothed_values) if len(smoothed_values) > 1 else 0.0
        residual_noise = statistics.mean(
            abs(raw_value - smooth_value)
            for raw_value, smooth_value in zip(raw_values, smoothed_values, strict=False)
        )
        return 1.0 / (1.0 + smoothed_volatility + residual_noise)

    def _baseline_quality(self, baselines: list[float]) -> float:
        if not baselines:
            return 0.0

        present_samples = sum(1 for baseline in baselines if abs(baseline) > MIN_SIGNAL_THRESHOLD)
        presence = present_samples / len(baselines)
        consistency = 1.0 / (1.0 + (statistics.stdev(baselines) if len(baselines) > 1 else 0.0))
        centeredness = max(
            0.0,
            1.0 - (abs(statistics.mean(baselines) - BASELINE_EXPECTED) / BASELINE_TOLERANCE),
        )
        return max(
            0.0,
            min(1.0, presence * ((centeredness * 0.7) + (consistency * 0.3))),
        )

    def _rarity_score(self, peak_relief: float, avg_dynamic: float) -> float:
        rarity_driver = peak_relief + max(0.0, peak_relief - avg_dynamic) * 0.75
        if rarity_driver >= RARITY_SATURATION_RELIEF:
            return 20.0
        return 20.0 * (1.0 - math.exp(-rarity_driver / 1.1))


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
