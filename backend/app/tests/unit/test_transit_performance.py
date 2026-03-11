import time
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

from app.prediction.aggregator import V3ThemeAggregator
from app.prediction.intraday_activation_builder import IntradayActivationBuilder
from app.prediction.schemas import (
    NatalChart,
    PlanetState,
    StepAstroState,
    V3SignalLayer,
    V3ThemeSignal,
)
from app.prediction.transit_signal_builder import TransitSignalBuilder


def test_v3_layers_performance_benchmark():
    # 96 steps
    planets_list = [
        "Sun", "Moon", "Mercury", "Venus", "Mars", 
        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
    ]
    targets_list = planets_list + ["Asc", "MC"]

    # Mock context
    ctx = MagicMock()
    ctx.prediction_context.categories = [MagicMock(code="work", is_enabled=True)]
    ctx.prediction_context.planet_category_weights = []
    ctx.prediction_context.house_category_weights = []
    ctx.prediction_context.planet_profiles = {
        p: MagicMock(weight_intraday=1.0, typical_polarity="positive") 
        for p in planets_list
    }
    ctx.prediction_context.aspect_profiles = {
        a: MagicMock(intensity_weight=1.0, default_valence="positive") 
        for a in ["conjunction", "sextile", "square", "trine", "opposition"]
    }

    natal = NatalChart(
        planet_positions={p: 10.0 * i for i, p in enumerate(targets_list)},
        planet_houses={p: (i % 12) + 1 for i, p in enumerate(targets_list)},
        house_sign_rulers={},
        natal_aspects=[]
    )

    steps = []
    base_time = datetime(2026, 3, 11, 0, 0, tzinfo=UTC)
    for i in range(96):
        steps.append(StepAstroState(
            ut_jd=0.0,
            local_time=base_time + timedelta(minutes=15 * i),
            ascendant_deg=1.0 * i, mc_deg=0.0, house_cusps=[], house_system_effective="",
            planets={p: PlanetState(p, 1.0 * i, 1.0, False, 0, 1) for p in planets_list}
        ))

    # Benchmark T(c,t)
    t_builder = TransitSignalBuilder()
    start_t = time.perf_counter()
    t_builder.build_timeline(steps, natal, ctx)
    dur_t = (time.perf_counter() - start_t) * 1000

    # Benchmark A(c,t)
    a_builder = IntradayActivationBuilder()
    start_a = time.perf_counter()
    a_builder.build_timeline(steps, natal, ctx)
    dur_a = (time.perf_counter() - start_a) * 1000

    # Benchmark Aggregation (10 themes)
    aggregator = V3ThemeAggregator()

    # Mock theme signals
    theme_signals = {}
    for tc in [f"cat_{i}" for i in range(10)]:
        theme_signals[tc] = V3ThemeSignal(
            theme_code=tc,
            timeline={
                s.local_time: V3SignalLayer(1.0, 0.0, 0.0, 0.0, 1.0)
                for s in steps
            }
        )

    start_agg = time.perf_counter()
    for ts in theme_signals.values():
        aggregator.aggregate_theme(ts)
    dur_agg = (time.perf_counter() - start_agg) * 1000

    print("\nBenchmark V3 Layers (96 steps):")
    print(f"  T(c,t) Transit: {dur_t:.2f}ms (Budget < 100ms)")
    print(f"  A(c,t) Activation: {dur_a:.2f}ms (Budget < 50ms)")
    print(f"  Aggregation (10 themes): {dur_agg:.2f}ms")

    assert dur_t < 100.0
    assert dur_a < 50.0

