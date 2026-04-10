from __future__ import annotations

from pathlib import Path


def generate_markdown_report(results: list[dict]) -> str:
    """Generates a markdown table from evaluation results (Story 66.16 Matrix fix)."""
    header = (
        "| Combination | Placeholders | CQ | Persona | Contract | Length | Diff. Plan | Status |\n"
    )
    separator = "|---|---|---|---|---|---|---|---|\n"
    rows = []

    def get_status_icon(val):
        if val == "N/A":
            return "➖"
        return "✅" if val else "❌"

    for r in results:
        # Status logic: all must be true or N/A
        all_metrics = [
            r.get("placeholders"),
            r.get("context_quality"),
            r.get("persona"),
            r.get("output_contract"),
            r.get("length_budget"),
            r.get("differentiation_plan", True),
        ]

        passed = all(m is True or m == "N/A" for m in all_metrics)
        status = "✅" if passed else "❌"

        rows.append(
            f"| {r['case']} | "
            f"{get_status_icon(r.get('placeholders'))} | "
            f"{get_status_icon(r.get('context_quality'))} | "
            f"{get_status_icon(r.get('persona'))} | "
            f"{get_status_icon(r.get('output_contract'))} | "
            f"{get_status_icon(r.get('length_budget'))} | "
            f"{get_status_icon(r.get('differentiation_plan'))} | "
            f"{status} |"
        )

    return header + separator + "\n".join(rows)


if __name__ == "__main__":
    # Example usage / standalone generator
    dummy_results = [
        {
            "case": "natal/premium/ample/full",
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": True,
            "length_budget": True,
            "differentiation_plan": True,
        },
        {
            "case": "chat/free/synthetique/minimal",
            "placeholders": True,
            "context_quality": True,
            "persona": True,
            "output_contract": "N/A",
            "length_budget": True,
            "differentiation_plan": True,
        },
    ]
    report = generate_markdown_report(dummy_results)
    print(report)

    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Orchestration Evaluation Report (Story 66.16 Matrix)\n\n")
        f.write(report)
    print(f"Report generated at {report_path}")
