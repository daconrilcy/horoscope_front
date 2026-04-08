from __future__ import annotations

import json
from pathlib import Path

def generate_markdown_report(results: list[dict]) -> str:
    """Generates a markdown table from evaluation results."""
    header = "| Combination | Placeholders | Context Quality | Persona | Status |\n"
    separator = "|---|---|---|---|---|\n"
    rows = []
    
    for r in results:
        status = "✅" if all([r["placeholders"], r["context_quality"], r["persona"]]) else "❌"
        rows.append(
            f"| {r['case']} | {'✅' if r['placeholders'] else '❌'} | "
            f"{'✅' if r['context_quality'] else '❌'} | "
            f"{'✅' if r['persona'] else '❌'} | {status} |"
        )
        
    return header + separator + "\n".join(rows)

if __name__ == "__main__":
    # Example usage / standalone generator
    dummy_results = [
        {"case": "natal/premium/ample/full", "placeholders": True, "context_quality": True, "persona": True},
        {"case": "chat/free/synthetique/minimal", "placeholders": True, "context_quality": True, "persona": True}
    ]
    report = generate_markdown_report(dummy_results)
    print(report)
    
    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Orchestration Evaluation Report\n\n")
        f.write(report)
    print(f"Report generated at {report_path}")
