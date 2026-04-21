import pytest

from app.ops.llm.performance_qualification_service import (
    PerformanceQualificationService,
)


def test_evaluate_run_nominal_success():
    report = PerformanceQualificationService.evaluate_run(
        family="chat",
        profile="nominal",
        total_requests=100,
        success_count=100,
        protection_count=0,
        error_count=0,
        latency_p50_ms=500.0,
        latency_p95_ms=1000.0,
        latency_p99_ms=1500.0,
        throughput_rps=10.0,
    )
    assert report.verdict == "go"
    assert report.budget_remaining == 1.0
    assert len(report.constraints) == 0


def test_evaluate_run_sla_violation_latency():
    # SLA for chat is p95_latency_max_ms=5000.0
    report = PerformanceQualificationService.evaluate_run(
        family="chat",
        profile="stress",
        total_requests=100,
        success_count=90,
        protection_count=10,
        error_count=0,
        latency_p50_ms=1000.0,
        latency_p95_ms=6000.0,
        latency_p99_ms=8000.0,
        throughput_rps=5.0,
    )
    assert report.verdict == "no-go"
    assert "SLA Violation: p95 latency" in report.constraints[0]


def test_evaluate_run_slo_warning_protection():
    # SLO for chat is max_protection_rate=0.05
    report = PerformanceQualificationService.evaluate_run(
        family="chat",
        profile="nominal",
        total_requests=100,
        success_count=90,
        protection_count=10,
        error_count=0,
        latency_p50_ms=500.0,
        latency_p95_ms=1000.0,
        latency_p99_ms=1500.0,
        throughput_rps=10.0,
    )
    assert report.verdict == "go-with-constraints"
    assert "SLO Warning: protection rate" in report.constraints[0]


def test_evaluate_run_budget_consumption():
    # SLO for chat is max_error_rate=0.01
    # total=100, error=1 -> error_rate = 0.01 (limit reached but not exceeded)
    report = PerformanceQualificationService.evaluate_run(
        family="chat",
        profile="nominal",
        total_requests=100,
        success_count=99,
        protection_count=0,
        error_count=1,
        latency_p50_ms=500.0,
        latency_p95_ms=1000.0,
        latency_p99_ms=1500.0,
        throughput_rps=10.0,
    )
    assert report.verdict == "go"
    assert report.budget_remaining == 0.0

    # total=100, error=2 -> error_rate = 0.02 (> 0.01)
    report = PerformanceQualificationService.evaluate_run(
        family="chat",
        profile="nominal",
        total_requests=100,
        success_count=98,
        protection_count=0,
        error_count=2,
        latency_p50_ms=500.0,
        latency_p95_ms=1000.0,
        latency_p99_ms=1500.0,
        throughput_rps=10.0,
    )
    assert report.verdict == "go-with-constraints"
    assert report.budget_remaining == 0.0
    assert "SLO Warning: error rate" in report.constraints[0]


def test_resolve_manifest_entry_id_accepts_explicit_value():
    manifest_entry_id = PerformanceQualificationService._resolve_manifest_entry_id(
        {"targets": {"chat:None:free:fr-FR": {}}},
        "chat:None:free:fr-FR",
    )
    assert manifest_entry_id == "chat:None:free:fr-FR"


def test_resolve_manifest_entry_id_derives_single_target():
    manifest_entry_id = PerformanceQualificationService._resolve_manifest_entry_id(
        {"targets": {"chat:None:free:fr-FR": {}}},
        None,
    )
    assert manifest_entry_id == "chat:None:free:fr-FR"


def test_resolve_manifest_entry_id_rejects_multi_target_manifest_without_id():
    with pytest.raises(ValueError, match="manifest_entry_id is required"):
        PerformanceQualificationService._resolve_manifest_entry_id(
            {
                "targets": {
                    "chat:None:free:fr-FR": {},
                    "guidance:None:premium:fr-FR": {},
                }
            },
            None,
        )


def test_resolve_manifest_entry_id_rejects_invalid_manifest_shape():
    with pytest.raises(ValueError, match="manifest is invalid"):
        PerformanceQualificationService._resolve_manifest_entry_id(["not-a-dict"], None)
