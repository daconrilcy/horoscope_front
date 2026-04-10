from __future__ import annotations

from pathlib import Path


def generate_markdown_report(results: list[dict]) -> str:
    """Generates a markdown table and gating status (Story 66.24 AC8)."""
    header = (
        "| Combination | Pipeline | Placeholders | CQ | Persona | Contract | Length | Diff. Plan | Status |\n"
    )
    separator = "|---|---|---|---|---|---|---|---|---|\n"
    rows = []

    # Gating counters
    total_cases = len(results)
    passed_cases = 0
    nominal_failures = 0
    transitional_failures = 0

    # Coverage checklist (AC8 Requirement: all daily active paths must be present)
    required_features = {"chat", "guidance", "natal", "horoscope_daily", "daily_prediction"}
    found_features = {r["case"].split("/")[0] for r in results}
    missing_features = required_features - found_features

    def get_status_icon(val):
        if val == "N/A":
            return "➖"
        return "✅" if val else "❌"

    def get_pipeline_label(val):
        if val == "nominal_canonical":
            return "🏛️ nominal"
        if val == "transitional_governance":
            return "🚧 trans."
        return f"❓ {val}"

    for r in results:
        # Status logic: all must be true or N/A
        all_metrics = [
            r.get("placeholders"),
            r.get("context_quality"),
            r.get("persona"),
            r.get("output_contract"),
            r.get("length_budget"),
            r.get("differentiation_plan", True),
            r.get("pipeline_ok", True),
        ]

        passed = all(m is True or m == "N/A" for m in all_metrics)
        if passed:
            passed_cases += 1
        else:
            if r.get("pipeline_kind") == "nominal_canonical":
                nominal_failures += 1
            else:
                transitional_failures += 1

        status = "✅" if passed else "❌"

        rows.append(
            f"| {r['case']} | "
            f"{get_pipeline_label(r.get('pipeline_kind'))} | "
            f"{get_status_icon(r.get('placeholders'))} | "
            f"{get_status_icon(r.get('context_quality'))} | "
            f"{get_status_icon(r.get('persona'))} | "
            f"{get_status_icon(r.get('output_contract'))} | "
            f"{get_status_icon(r.get('length_budget'))} | "
            f"{get_status_icon(r.get('differentiation_plan'))} | "
            f"{status} |"
        )

    # Gating Summary
    campaign_ok = (passed_cases == total_cases) and not missing_features
    gating_status = "🟢 PASSED" if campaign_ok else "🔴 FAILED"
    if not campaign_ok and passed_cases > 0:
        if nominal_failures == 0:
            gating_status = "🟠 WARNING (Transitional issues)"
        else:
            gating_status = "🔴 BLOCKED (Nominal failures)"

    if missing_features:
        gating_status = "🔴 INCOMPLETE (Missing paths)"

    summary = (
        f"## Gating Status: {gating_status}\n\n"
        f"- **Total Combinations**: {total_cases}\n"
        f"- **Passed**: {passed_cases}/{total_cases}\n"
        f"- **Nominal Failures**: {nominal_failures} (BLOCQUANT)\n"
        f"- **Transitional Failures**: {transitional_failures} (ALERTE)\n"
    )

    if missing_features:
        summary += f"- **Missing Mandatory Features**: {', '.join(missing_features)} (BLOCQUANT)\n"

    summary += "\n"

    return summary + header + separator + "\n".join(rows)


if __name__ == "__main__":
    # Example usage / standalone generator
    dummy_results = [
        {
            "case": "natal/premium/ample/full",
            "pipeline_kind": "nominal_canonical",
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
            "pipeline_ok": True,
        },
        {
            "case": "daily_prediction/free/synthetique/minimal",
            "pipeline_kind": "transitional_governance",
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": "N/A",
            "length_budget": True,
            "differentiation_plan": True,
            "pipeline_ok": True,
        },
    ]
    report = generate_markdown_report(dummy_results)
    print(report)

    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Orchestration Evaluation Report (Story 66.24 Matrix)\n\n")
        f.write(report)
    print(f"Report generated at {report_path}")
