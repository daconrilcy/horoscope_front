from __future__ import annotations

import json
from pathlib import Path

def generate_markdown_report(results: list[dict]) -> str:
    """Generates a markdown table from evaluation results (Story 66.16 Low fix)."""
    header = "| Combination | Placeholders | CQ | Persona | Contract | Length | Status |\n"
    separator = "|---|---|---|---|---|---|---|\n"
    rows = []
    
    for r in results:
        # Check all dimensions
        dims = [
            r.get("placeholders", False),
            r.get("context_quality", False),
            r.get("persona", False),
            r.get("output_contract", True), # Optional dimension
            r.get("length_budget", True)    # Optional dimension
        ]
        status = "✅" if all(dims) else "❌"
        
        rows.append(
            f"| {r['case']} | "
            f"{'✅' if r.get('placeholders') else '❌'} | "
            f"{'✅' if r.get('context_quality') else '❌'} | "
            f"{'✅' if r.get('persona') else '❌'} | "
            f"{'✅' if r.get('output_contract', 'N/A') else '❌'} | "
            f"{'✅' if r.get('length_budget', 'N/A') else '❌'} | "
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
            "length_budget": True
        },
        {
            "case": "chat/free/synthetique/minimal", 
            "placeholders": True, 
            "context_quality": True, 
            "persona": True,
            "output_contract": "N/A",
            "length_budget": True
        }
    ]
    report = generate_markdown_report(dummy_results)
    print(report)
    
    report_path = Path(__file__).parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LLM Orchestration Evaluation Report (Story 66.16 Matrix)\n\n")
        f.write(report)
    print(f"Report generated at {report_path}")
