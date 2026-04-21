from typing import Dict

from app.domain.llm.runtime.contracts import PerformanceSLA, PerformanceSLO

# Story 66.35 AC6: SLO internes versionnés par famille
PERFORMANCE_SLO_REGISTRY: Dict[str, PerformanceSLO] = {
    "chat": PerformanceSLO(
        p95_latency_ms=2000.0,
        p99_latency_ms=3500.0,
        min_success_rate=0.98,
        max_protection_rate=0.05,
        max_error_rate=0.01,
    ),
    "guidance": PerformanceSLO(
        p95_latency_ms=3000.0,
        p99_latency_ms=5000.0,
        min_success_rate=0.95,
        max_protection_rate=0.10,
        max_error_rate=0.02,
    ),
    "natal": PerformanceSLO(
        p95_latency_ms=8000.0,
        p99_latency_ms=12000.0,
        min_success_rate=0.90,
        max_protection_rate=0.15,
        max_error_rate=0.05,
    ),
    "horoscope_daily": PerformanceSLO(
        p95_latency_ms=5000.0,
        p99_latency_ms=8000.0,
        min_success_rate=0.95,
        max_protection_rate=0.05,
        max_error_rate=0.02,
    ),
}

# Story 66.35 AC7: SLA interne d'exploitation (Seuils critiques)
PERFORMANCE_SLA_REGISTRY: Dict[str, PerformanceSLA] = {
    "chat": PerformanceSLA(p95_latency_max_ms=5000.0, max_error_rate_threshold=0.05),
    "guidance": PerformanceSLA(p95_latency_max_ms=8000.0, max_error_rate_threshold=0.10),
    "natal": PerformanceSLA(p95_latency_max_ms=20000.0, max_error_rate_threshold=0.20),
    "horoscope_daily": PerformanceSLA(p95_latency_max_ms=15000.0, max_error_rate_threshold=0.10),
}
