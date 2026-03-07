import statistics
from dataclasses import dataclass, field

RAW_STEP_MAX = 3.0
RAW_DAY_MAX = 2.0
PEAK90_WINDOW = 6
CLOSE_WINDOW = 8


@dataclass
class CategoryAggregation:
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
