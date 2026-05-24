#!/usr/bin/env python3
"""Valide une capsule de story CONDAMAD.

Le validateur controle la structure et les preuves minimales. Il ne remplace
pas la revue humaine ou agentique de l'implementation.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

REQUIRED = [
    "00-story.md",
    "generated/01-execution-brief.md",
    "generated/03-acceptance-traceability.md",
    "generated/04-target-files.md",
    "generated/06-validation-plan.md",
    "generated/07-no-legacy-dry-guardrails.md",
    "generated/10-final-evidence.md",
]

FINAL_REQUIRED_SECTIONS = [
    "Story status",
    "Preflight",
    "Capsule validation",
    "AC validation",
    "Files changed",
    "Files deleted",
    "Tests added or updated",
    "Commands run",
    "Commands skipped or blocked",
    "DRY / No Legacy evidence",
    "Diff review",
    "Final worktree status",
    "Remaining risks",
    "Suggested reviewer focus",
]

COMPLETE_STATUS_PATTERNS = [
    re.compile(r"^pass(?:ed)?$", re.I),
    re.compile(r"^pass_with_limitations$", re.I),
    re.compile(r"^fail(?:ed)?$", re.I),
    re.compile(r"^blocked$", re.I),
    re.compile(r"^not applicable\b.+", re.I),
]

INCOMPLETE_STATUS_RE = re.compile(r"\b(?:pending|tbd|todo|in_progress)\b", re.I)
MARKER_RE = re.compile(
    r"\b(?:TBD|PENDING|not-started|not-run|not-recorded|none-recorded|not-validated)\b",
    re.I,
)


class MarkdownTable(NamedTuple):
    """Represente une table markdown avec entetes et lignes nettoyees."""

    headers: list[str]
    rows: list[list[str]]


def read_text(path: Path) -> str:
    """Lit un fichier texte en preservant la validation en cas d'octets invalides."""
    return path.read_text(encoding="utf-8", errors="replace")


def split_markdown_row(line: str) -> list[str]:
    """Decoupe une ligne de table markdown en cellules normalisees."""
    cells: list[str] = []
    current: list[str] = []
    content = line.strip().strip("|")
    index = 0
    while index < len(content):
        char = content[index]
        if char == "\\" and index + 1 < len(content) and content[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current.clear()
            index += 1
            continue
        current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def is_markdown_separator(line: str) -> bool:
    """Indique si une ligne est le separateur d'une table markdown."""
    cells = split_markdown_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_markdown_tables(text: str) -> list[MarkdownTable]:
    """Extrait les tables markdown simples avec leur ligne de separation."""
    lines = text.splitlines()
    tables: list[MarkdownTable] = []
    index = 0
    while index + 1 < len(lines):
        header_line = lines[index]
        separator_line = lines[index + 1]
        if "|" not in header_line or not is_markdown_separator(separator_line):
            index += 1
            continue

        headers = split_markdown_row(header_line)
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and "|" in lines[index]:
            rows.append(split_markdown_row(lines[index]))
            index += 1
        tables.append(MarkdownTable(headers=headers, rows=rows))
    return tables


def normalize_header(value: str) -> str:
    """Normalise un entete de table pour les comparaisons insensibles au style."""
    return re.sub(r"\s+", " ", value.strip()).casefold()


def find_table_with_columns(
    text: str, required_columns: list[str]
) -> MarkdownTable | None:
    """Retourne la premiere table contenant tous les entetes requis."""
    required = {normalize_header(column) for column in required_columns}
    for table in parse_markdown_tables(text):
        headers = {normalize_header(header) for header in table.headers}
        if required.issubset(headers):
            return table
    return None


def column_values(table: MarkdownTable, column: str) -> list[str]:
    """Extrait les valeurs non vides d'une colonne de table markdown."""
    header_map = {
        normalize_header(header): position
        for position, header in enumerate(table.headers)
    }
    column_index = header_map.get(normalize_header(column))
    if column_index is None:
        return []
    return [
        row[column_index].strip()
        for row in table.rows
        if len(row) > column_index and row[column_index].strip()
    ]


def status_column_values(table: MarkdownTable) -> list[str]:
    """Extrait les valeurs de la colonne Status d'une table markdown."""
    return column_values(table, "Status")


def duplicate_values(values: list[str]) -> list[str]:
    """Retourne les valeurs dupliquees dans l'ordre de detection."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        normalized = value.casefold()
        if normalized in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(normalized)
    return duplicates


def is_complete_status(value: str) -> bool:
    """Verifie qu'un statut final appartient aux valeurs de fin autorisees."""
    normalized = value.strip().strip("`")
    if not normalized or INCOMPLETE_STATUS_RE.search(normalized):
        return False
    return any(pattern.fullmatch(normalized) for pattern in COMPLETE_STATUS_PATTERNS)


def validate_capsule(capsule: Path, final: bool) -> list[str]:
    """Valide les fichiers requis et les preuves d'une capsule CONDAMAD."""
    errors: list[str] = []
    if not capsule.exists() or not capsule.is_dir():
        return [f"Capsule directory not found: {capsule}"]

    for rel in REQUIRED:
        path = capsule / rel
        if not path.exists():
            errors.append(f"Missing required file: {rel}")
        elif not path.is_file():
            errors.append(f"Required path is not a file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"Required file is empty: {rel}")

    traceability = capsule / "generated/03-acceptance-traceability.md"
    traceability_table: MarkdownTable | None = None
    if traceability.is_file() and traceability.stat().st_size > 0:
        text = read_text(traceability)
        traceability_table = find_table_with_columns(text, ["AC", "Requirement", "Status"])
        if traceability_table is None:
            errors.append(
                "Traceability table missing required columns: AC, Requirement, Status"
            )
        else:
            duplicate_acs = duplicate_values(column_values(traceability_table, "AC"))
            for ac in duplicate_acs:
                errors.append(f"Traceability has duplicate AC row: {ac}")
            if final:
                statuses = status_column_values(traceability_table)
                if not statuses:
                    errors.append("Traceability table has no status values in final mode")
                for status in statuses:
                    if not is_complete_status(status):
                        errors.append(
                            f"Traceability has invalid final status: {status or '<empty>'}"
                        )

    final_evidence = capsule / "generated/10-final-evidence.md"
    if final_evidence.is_file() and final_evidence.stat().st_size > 0:
        text = read_text(final_evidence)
        for section in FINAL_REQUIRED_SECTIONS:
            if not re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.I | re.M):
                errors.append(f"Final evidence missing section: {section}")
        final_ac_table = find_table_with_columns(
            text, ["AC", "Implementation evidence", "Validation evidence", "Status"]
        )
        if final_ac_table is None:
            errors.append("Final evidence missing AC validation table")
        else:
            duplicate_acs = duplicate_values(column_values(final_ac_table, "AC"))
            for ac in duplicate_acs:
                errors.append(f"Final evidence has duplicate AC row: {ac}")
        if final_ac_table is not None and final:
            if traceability_table is not None:
                traceability_acs = column_values(traceability_table, "AC")
                final_acs = column_values(final_ac_table, "AC")
                if traceability_acs != final_acs:
                    errors.append(
                        "Final evidence AC rows do not match traceability AC rows"
                    )
            statuses = status_column_values(final_ac_table)
            if not statuses:
                errors.append("Final evidence AC table has no status values in final mode")
            for status in statuses:
                if not is_complete_status(status):
                    errors.append(
                        f"Final evidence has invalid AC status: {status or '<empty>'}"
                    )
        if final and MARKER_RE.search(text):
            errors.append(
                "Final evidence still contains placeholder markers in final mode"
            )

    return errors


def main() -> int:
    """Execute la validation depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Validate a CONDAMAD story capsule.")
    parser.add_argument(
        "capsule", type=Path, help="Path to _condamad/stories/<story-key>."
    )
    parser.add_argument(
        "--final",
        action="store_true",
        help="Require final evidence to be complete, with no placeholder markers.",
    )
    args = parser.parse_args()

    errors = validate_capsule(args.capsule.expanduser().resolve(), args.final)
    if errors:
        print("CONDAMAD validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CONDAMAD validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
