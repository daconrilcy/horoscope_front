#!/usr/bin/env python3
"""Linte les rapports CONDAMAD Domain Auditor avec des avertissements anti-flou."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from condamad_domain_audit_validate import (
    FINDING_COLUMNS,
    cell,
    parse_first_table,
    read_text,
    validate_audit_folder,
)

VAGUE_ACTION_RE = re.compile(
    r"^\s*(?:"
    r"(?:review|fix|improve|handle|clarify|investigate)\s*(?:later|everything|broadly|if needed)?"
    r"|review broadly"
    r"|investigate everything"
    r"|clarify if needed"
    r"|fix later"
    r")\s*\.?\s*$",
    re.I,
)
VAGUE_EVIDENCE_RE = re.compile(
    r"^(code|repo|scan|manual|see above|various|multiple)$", re.I
)
PRIORITY_RE = re.compile(r"^P\d+$")


def lint_audit_folder(audit_folder: Path) -> list[str]:
    """Retourne les avertissements non bloquants du rapport."""
    warnings: list[str] = []
    errors = validate_audit_folder(audit_folder)
    if errors:
        return [f"Validation must pass before lint: {error}" for error in errors]

    finding_text = read_text(audit_folder / "02-finding-register.md")
    finding_table = parse_first_table(finding_text, FINDING_COLUMNS)
    if finding_table:
        high_findings: set[str] = set()
        for row in finding_table.rows:
            finding_id = cell(row, finding_table, "ID")
            evidence = cell(row, finding_table, "Evidence")
            action = cell(row, finding_table, "Recommended action")
            severity = cell(row, finding_table, "Severity")
            if VAGUE_EVIDENCE_RE.match(evidence.strip()):
                warnings.append(f"{finding_id} evidence is too vague")
            if VAGUE_ACTION_RE.match(action.strip()):
                warnings.append(f"{finding_id} recommended action is too vague")
            if severity == "High":
                high_findings.add(finding_id)
        risk_text = read_text(audit_folder / "04-risk-matrix.md")
        risk_table = parse_first_table(risk_text, ["Finding", "Priority"])
        priorities = {}
        if risk_table:
            priorities = {
                cell(row, risk_table, "Finding"): cell(row, risk_table, "Priority")
                for row in risk_table.rows
            }
        for finding_id in sorted(high_findings):
            priority = priorities.get(finding_id, "")
            if not PRIORITY_RE.fullmatch(priority):
                warnings.append(
                    f"{finding_id} is High without normalized priority (P0, P1, P2)"
                )

    story_text = read_text(audit_folder / "03-story-candidates.md")
    for match in re.finditer(
        r"^##\s+(SC-\d{3,}).*?(?=^##\s+SC-|\Z)", story_text, re.S | re.M
    ):
        block = match.group(0)
        if not re.search(r"Suggested archetype:\s*\S", block):
            warnings.append(f"{match.group(1)} missing suggested archetype")

    evidence_text = read_text(audit_folder / "01-evidence-log.md")
    command_lines = [
        line for line in evidence_text.splitlines() if "|" in line and "`" in line
    ]
    if command_lines and all("rg " in line for line in command_lines):
        report_text = read_text(audit_folder / "00-audit-report.md").casefold()
        if "runtime" in report_text:
            warnings.append("Evidence only uses rg for runtime domain")
        if (
            "api" in report_text
            and "openapi" not in evidence_text.casefold()
            and "route table" not in evidence_text.casefold()
        ):
            warnings.append("No runtime evidence for API audit")
    if "legacy" in finding_text.casefold() and not re.search(
        r"negative|absence|no hit|0 hit|PASS", evidence_text, re.I
    ):
        warnings.append("No negative scan for No Legacy audit")

    executive_words = read_text(audit_folder / "05-executive-summary.md").split()
    if len(executive_words) > 450:
        warnings.append("Executive summary too long")

    return warnings


def main() -> int:
    """Execute le lint depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Lint a CONDAMAD domain audit folder.")
    parser.add_argument("audit_folder", type=Path)
    parser.add_argument(
        "--strict", action="store_true", help="Fail when warnings are detected."
    )
    args = parser.parse_args()

    warnings = lint_audit_folder(args.audit_folder.expanduser().resolve())
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if warnings and args.strict:
        return 1
    print(
        "CONDAMAD domain audit lint passed."
        if not warnings
        else "CONDAMAD domain audit lint completed with warnings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
