from datetime import timedelta

from fastapi.testclient import TestClient

from app.infra.observability.metrics import (
    get_counter_sums_by_prefix_in_window,
    get_metrics_snapshot,
    reset_metrics,
)
from app.main import app


def test_healthcheck() -> None:
    reset_metrics()
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-Id")
    counters = get_counter_sums_by_prefix_in_window("http_requests_total|", timedelta(hours=1))
    assert sum(counters.values()) >= 1.0


def test_unmatched_routes_use_low_cardinality_metric_label() -> None:
    reset_metrics()
    client = TestClient(app)

    first = client.get("/unknown-a")
    second = client.get("/unknown-b")

    assert first.status_code == 404
    assert second.status_code == 404
    snapshot = get_metrics_snapshot()
    keys = list(snapshot["counters"].keys())
    assert any("route=__unmatched__" in key for key in keys)
    assert not any("route=/unknown-a" in key or "route=/unknown-b" in key for key in keys)
