from __future__ import annotations

from datetime import timedelta
from time import sleep

import app.infra.observability.metrics as metrics


def test_observe_duration_keeps_bounded_metric_storage(monkeypatch: object) -> None:
    metrics.reset_metrics()
    monkeypatch.setattr(metrics, "_MAX_EVENTS_PER_METRIC", 3)

    metrics.observe_duration("http_request_duration_seconds|route=/x", 0.1)
    metrics.observe_duration("http_request_duration_seconds|route=/x", 0.2)
    metrics.observe_duration("http_request_duration_seconds|route=/x", 0.3)
    metrics.observe_duration("http_request_duration_seconds|route=/x", 0.4)

    values = metrics.get_duration_values_in_window(
        "http_request_duration_seconds|route=/x", timedelta(days=1)
    )
    assert values == [0.2, 0.3, 0.4]


def test_stale_metrics_are_cleaned_from_snapshot(monkeypatch: object) -> None:
    metrics.reset_metrics()
    monkeypatch.setattr(metrics, "_METRICS_RETENTION", timedelta(milliseconds=1))

    metrics.increment_counter("test_counter", 1.0)
    metrics.observe_duration("test_duration", 0.1)

    sleep(0.01)
    metrics.get_counter_sums_by_prefix_in_window("test", timedelta(seconds=1))
    metrics.get_duration_values_by_prefix_in_window("test", timedelta(seconds=1))

    snapshot = metrics.get_metrics_snapshot()
    assert "test_counter" not in snapshot["counters"]
    assert "test_duration" not in snapshot["durations_avg_seconds"]
