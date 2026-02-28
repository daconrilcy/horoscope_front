from __future__ import annotations

import pytest

from app.services.cross_tool_report import (
    build_run_report,
    ensure_dev_only_runtime,
    render_markdown_report,
)


def test_build_run_report_computes_deltas_and_summary() -> None:
    report = build_run_report(
        dataset_id="golden-pro-v1",
        tolerances={"planets_deg": 0.01, "angles_deg": 0.05},
        cases=[
            {
                "case_id": "case-1",
                "expected": {
                    "sun": 100.0,
                    "moon": 200.0,
                    "mercury": 300.0,
                    "asc": 10.0,
                    "mc": 20.0,
                    "cusp_1": 10.0,
                    "cusp_10": 280.0,
                },
                "actual": {
                    "sun": 100.005,
                    "moon": 200.02,
                    "mercury": 299.995,
                    "asc": 10.03,
                    "mc": 20.01,
                    "cusp_1": 10.06,
                    "cusp_10": 280.02,
                },
            }
        ],
    )

    assert report["dataset_id"] == "golden-pro-v1"
    assert report["summary"]["cases_count"] == 1
    assert report["summary"]["failed_cases"] == 1
    assert report["summary"]["failed_metrics"] >= 1

    case = report["cases"][0]
    assert case["case_id"] == "case-1"
    assert case["status"] == "failed"
    assert case["metrics"]["sun"]["within_tolerance"] is True
    assert case["metrics"]["moon"]["within_tolerance"] is False
    assert case["metrics"]["cusp_1"]["within_tolerance"] is False


def test_render_markdown_report_contains_summary_and_failures() -> None:
    report = {
        "dataset_id": "golden-pro-v1",
        "generated_at": "2026-02-28T12:00:00Z",
        "summary": {
            "cases_count": 2,
            "passed_cases": 1,
            "failed_cases": 1,
            "failed_metrics": 2,
            "max_delta_degrees": 0.12,
        },
        "cases": [
            {"case_id": "case-pass", "status": "passed", "max_delta_degrees": 0.01, "failures": []},
            {
                "case_id": "case-fail",
                "status": "failed",
                "max_delta_degrees": 0.12,
                "failures": [
                    {"metric": "moon", "delta_degrees": 0.08, "tolerance_degrees": 0.01},
                    {"metric": "asc", "delta_degrees": 0.12, "tolerance_degrees": 0.05},
                ],
            },
        ],
    }

    markdown = render_markdown_report(report)

    assert "# Cross-Tool Drift Report (dev-only)" in markdown
    assert "Dataset: `golden-pro-v1`" in markdown
    assert "| Cases | 2 |" in markdown
    assert "case-fail" in markdown
    assert "moon" in markdown


def test_ensure_dev_only_runtime_blocks_ci() -> None:
    with pytest.raises(RuntimeError, match="dev-only"):
        ensure_dev_only_runtime({"CI": "true"})

    ensure_dev_only_runtime({"CI": "false"})
    ensure_dev_only_runtime({})
