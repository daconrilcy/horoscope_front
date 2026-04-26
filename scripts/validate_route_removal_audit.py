"""Valide l'audit de suppression des routes historiques CONDAMAD."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ALLOWED_CLASSIFICATIONS = {
    "canonical-active",
    "external-active",
    "historical-facade",
    "dead",
    "needs-user-decision",
}
ALLOWED_DECISIONS = {"keep", "delete", "replace-consumer", "needs-user-decision"}


@dataclass(frozen=True)
class AuditRow:
    """Ligne normalisee de la table d'audit."""

    item: str
    classification: str
    decision: str
    proof: str
    risk: str


def _parse_table_rows(markdown: str) -> list[AuditRow]:
    """Extrait les lignes de la table principale sans parser le Markdown complet."""
    rows: list[AuditRow] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[:3] == ["Item", "Type", "Classification"]:
            continue
        if len(cells) != 8:
            raise ValueError(f"Audit row must contain 8 columns: {raw_line}")
        rows.append(
            AuditRow(
                item=cells[0],
                classification=cells[2],
                decision=cells[5],
                proof=cells[6],
                risk=cells[7],
            )
        )
    return rows


def validate_audit(path: Path) -> list[str]:
    """Retourne les erreurs structurelles de l'audit."""
    markdown = path.read_text(encoding="utf-8")
    errors: list[str] = []
    try:
        rows = _parse_table_rows(markdown)
    except ValueError as error:
        return [str(error)]
    if not rows:
        return ["audit table is empty"]
    for row in rows:
        if row.classification not in ALLOWED_CLASSIFICATIONS:
            errors.append(f"{row.item}: invalid classification {row.classification!r}")
        if row.decision not in ALLOWED_DECISIONS:
            errors.append(f"{row.item}: invalid decision {row.decision!r}")
        if row.classification == "external-active" and row.decision == "delete":
            errors.append(f"{row.item}: external-active items cannot be deleted")
        if row.decision in {"delete", "needs-user-decision"} and not row.risk:
            errors.append(f"{row.item}: risk is required for decision {row.decision}")
        if not row.proof:
            errors.append(f"{row.item}: proof is required")
    return errors


def main() -> int:
    """Point d'entree CLI du validateur d'audit."""
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_path", type=Path)
    args = parser.parse_args()
    errors = validate_audit(args.audit_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Audit OK: {args.audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
