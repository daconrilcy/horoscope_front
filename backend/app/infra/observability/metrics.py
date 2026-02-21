from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import NamedTuple

_COUNTERS: defaultdict[str, float] = defaultdict(float)
_HISTOGRAMS: defaultdict[str, deque[float]] = defaultdict(deque)
_COUNTER_EVENTS: defaultdict[str, deque["CounterEvent"]] = defaultdict(deque)
_HISTOGRAM_EVENTS: defaultdict[str, deque["HistogramEvent"]] = defaultdict(deque)
_METRICS_RETENTION = timedelta(days=8)
_MAX_EVENTS_PER_METRIC = 200_000
_LOCK = Lock()


class CounterEvent(NamedTuple):
    timestamp: datetime
    value: float


class HistogramEvent(NamedTuple):
    timestamp: datetime
    value: float


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _prune_events(
    events: deque[CounterEvent] | deque[HistogramEvent],
    *,
    now: datetime,
) -> None:
    cutoff = now - _METRICS_RETENTION
    while events and events[0].timestamp < cutoff:
        events.popleft()
    while len(events) > _MAX_EVENTS_PER_METRIC:
        events.popleft()


def _prune_histogram_values(values: deque[float]) -> None:
    while len(values) > _MAX_EVENTS_PER_METRIC:
        values.popleft()


def _cleanup_stale_metric_names() -> None:
    for metric_name in list(_COUNTER_EVENTS.keys()):
        if _COUNTER_EVENTS[metric_name]:
            continue
        _COUNTER_EVENTS.pop(metric_name, None)
        _COUNTERS.pop(metric_name, None)

    for metric_name in list(_HISTOGRAM_EVENTS.keys()):
        if _HISTOGRAM_EVENTS[metric_name]:
            continue
        _HISTOGRAM_EVENTS.pop(metric_name, None)
        _HISTOGRAMS.pop(metric_name, None)


def increment_counter(name: str, value: float = 1.0) -> None:
    now = _utc_now()
    with _LOCK:
        _COUNTERS[name] += value
        metric_events = _COUNTER_EVENTS[name]
        metric_events.append(CounterEvent(timestamp=now, value=value))
        _prune_events(metric_events, now=now)
        _cleanup_stale_metric_names()


def observe_duration(name: str, duration_seconds: float) -> None:
    now = _utc_now()
    with _LOCK:
        histogram_values = _HISTOGRAMS[name]
        histogram_values.append(duration_seconds)
        _prune_histogram_values(histogram_values)
        metric_events = _HISTOGRAM_EVENTS[name]
        metric_events.append(HistogramEvent(timestamp=now, value=duration_seconds))
        _prune_events(metric_events, now=now)
        _cleanup_stale_metric_names()


def get_metrics_snapshot() -> dict[str, dict[str, float]]:
    with _LOCK:
        now = _utc_now()
        for events in _COUNTER_EVENTS.values():
            _prune_events(events, now=now)
        for events in _HISTOGRAM_EVENTS.values():
            _prune_events(events, now=now)
        _cleanup_stale_metric_names()

        counters = {key: float(value) for key, value in _COUNTERS.items()}
        durations = {
            key: (sum(values) / len(values) if values else 0.0)
            for key, values in _HISTOGRAMS.items()
        }
    return {"counters": counters, "durations_avg_seconds": durations}


def get_counter_sum_in_window(name: str, window: timedelta) -> float:
    now = _utc_now()
    cutoff = now - window
    with _LOCK:
        metric_events = _COUNTER_EVENTS[name]
        _prune_events(metric_events, now=now)
        _cleanup_stale_metric_names()
        return float(sum(item.value for item in metric_events if item.timestamp >= cutoff))


def get_duration_values_in_window(name: str, window: timedelta) -> list[float]:
    now = _utc_now()
    cutoff = now - window
    with _LOCK:
        metric_events = _HISTOGRAM_EVENTS[name]
        _prune_events(metric_events, now=now)
        _cleanup_stale_metric_names()
        return [item.value for item in metric_events if item.timestamp >= cutoff]


def get_counter_sums_by_prefix_in_window(prefix: str, window: timedelta) -> dict[str, float]:
    now = _utc_now()
    cutoff = now - window
    with _LOCK:
        result: dict[str, float] = {}
        for metric_name, metric_events in _COUNTER_EVENTS.items():
            if not metric_name.startswith(prefix):
                continue
            _prune_events(metric_events, now=now)
            result[metric_name] = float(
                sum(item.value for item in metric_events if item.timestamp >= cutoff)
            )
        _cleanup_stale_metric_names()
    return result


def get_duration_values_by_prefix_in_window(
    prefix: str, window: timedelta
) -> dict[str, list[float]]:
    now = _utc_now()
    cutoff = now - window
    with _LOCK:
        result: dict[str, list[float]] = {}
        for metric_name, metric_events in _HISTOGRAM_EVENTS.items():
            if not metric_name.startswith(prefix):
                continue
            _prune_events(metric_events, now=now)
            result[metric_name] = [item.value for item in metric_events if item.timestamp >= cutoff]
        _cleanup_stale_metric_names()
    return result


def reset_metrics() -> None:
    with _LOCK:
        _COUNTERS.clear()
        _HISTOGRAMS.clear()
        _COUNTER_EVENTS.clear()
        _HISTOGRAM_EVENTS.clear()
