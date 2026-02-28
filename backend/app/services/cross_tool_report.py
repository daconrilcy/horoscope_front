from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Mapping

MetricValues = Mapping[str, float]

PLANET_METRICS = frozenset({"sun", "moon", "mercury"})
ANGLE_METRICS = frozenset({"asc", "mc", "cusp_1", "cusp_10"})


def ensure_dev_only_runtime(env: Mapping[str, str]) -> None:
    """Block execution in CI-like environments for dev-only tooling."""
    ci_markers = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILD_BUILDID")
    for marker in ci_markers:
        value = str(env.get(marker, "")).strip().lower()
        if value in {"1", "true", "yes"}:
            raise RuntimeError("cross-tool report is dev-only and forbidden in CI")


def _circular_diff_degrees(actual: float, expected: float) -> float:
    raw = abs(actual - expected) % 360.0
    return min(raw, 360.0 - raw)


def _tolerance_for_metric(metric: str, tolerances: Mapping[str, float]) -> float:
    if metric in PLANET_METRICS:
        return float(tolerances["planets_deg"])
    if metric in ANGLE_METRICS:
        return float(tolerances["angles_deg"])
    return float(tolerances.get("angles_deg", 0.05))


def build_run_report(
    *,
    dataset_id: str,
    tolerances: Mapping[str, float],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    case_reports: list[dict[str, object]] = []
    failed_metrics_total = 0
    max_delta_global = 0.0
    failed_by_metric: Counter[str] = Counter()

    for case in cases:
        case_id = str(case["case_id"])
        expected = case["expected"]
        actual = case["actual"]
        if not isinstance(expected, Mapping) or not isinstance(actual, Mapping):
            raise ValueError(f"invalid case payload for {case_id}")

        metric_reports: dict[str, dict[str, object]] = {}
        failures: list[dict[str, object]] = []
        case_max_delta = 0.0

        for metric in sorted(set(expected.keys()).intersection(actual.keys())):
            expected_value = float(expected[metric])
            actual_value = float(actual[metric])
            delta = _circular_diff_degrees(actual_value, expected_value)
            tolerance = _tolerance_for_metric(metric, tolerances)
            within_tolerance = delta <= tolerance
            case_max_delta = max(case_max_delta, delta)
            max_delta_global = max(max_delta_global, delta)

            metric_reports[metric] = {
                "expected": round(expected_value, 6),
                "actual": round(actual_value, 6),
                "delta_degrees": round(delta, 6),
                "tolerance_degrees": round(tolerance, 6),
                "within_tolerance": within_tolerance,
            }

            if not within_tolerance:
                failed_metrics_total += 1
                failed_by_metric[metric] += 1
                failures.append(
                    {
                        "metric": metric,
                        "delta_degrees": round(delta, 6),
                        "tolerance_degrees": round(tolerance, 6),
                    }
                )

        status = "failed" if failures else "passed"
        case_reports.append(
            {
                "case_id": case_id,
                "status": status,
                "max_delta_degrees": round(case_max_delta, 6),
                "metrics": metric_reports,
                "failures": failures,
            }
        )

    passed_cases = sum(1 for case in case_reports if case["status"] == "passed")
    failed_cases = len(case_reports) - passed_cases

    return {
        "dataset_id": dataset_id,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "dev_only": True,
        "summary": {
            "cases_count": len(case_reports),
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "failed_metrics": failed_metrics_total,
            "max_delta_degrees": round(max_delta_global, 6),
            "drift_by_metric": dict(sorted(failed_by_metric.items())),
        },
        "cases": case_reports,
    }


def render_markdown_report(report: Mapping[str, object]) -> str:
    dataset_id = str(report["dataset_id"])
    generated_at = str(report["generated_at"])
    summary = report["summary"]
    if not isinstance(summary, Mapping):
        raise ValueError("invalid report.summary")

    lines = [
        "# Cross-Tool Drift Report (dev-only)",
        "",
        f"Dataset: `{dataset_id}`",
        f"Generated at: `{generated_at}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Cases | {int(summary['cases_count'])} |",
        f"| Passed cases | {int(summary['passed_cases'])} |",
        f"| Failed cases | {int(summary['failed_cases'])} |",
        f"| Failed metrics | {int(summary['failed_metrics'])} |",
        f"| Max delta (deg) | {float(summary['max_delta_degrees']):.6f} |",
        "",
        "## Failing Cases",
        "",
    ]

    cases = report["cases"]
    if not isinstance(cases, list):
        raise ValueError("invalid report.cases")

    failing_cases = [
        case
        for case in cases
        if isinstance(case, Mapping) and case.get("status") == "failed"
    ]
    if not failing_cases:
        lines.append("No failures detected.")
        return "\n".join(lines) + "\n"

    for case in failing_cases:
        case_id = str(case["case_id"])
        max_delta = float(case["max_delta_degrees"])
        lines.append(f"### {case_id} (max delta: {max_delta:.6f}°)")
        lines.append("")
        lines.append("| Metric | Delta (deg) | Tolerance (deg) |")
        lines.append("| --- | ---: | ---: |")
        failures = case.get("failures", [])
        if isinstance(failures, list):
            for failure in failures:
                if not isinstance(failure, Mapping):
                    continue
                lines.append(
                    f"| {failure['metric']} | {float(failure['delta_degrees']):.6f} | "
                    f"{float(failure['tolerance_degrees']):.6f} |"
                )
        lines.append("")

    return "\n".join(lines) + "\n"
