#!/usr/bin/env python3
"""Extrait les criteres d'acceptation d'une story CONDAMAD.

Le script aide les autres outils a reutiliser la table AC sans parser toute la
story a la main.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    """Lit un fichier markdown en UTF-8."""
    return path.read_text(encoding="utf-8", errors="replace")


def split_row(line: str) -> list[str]:
    """Decoupe une ligne de table markdown en cellules."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    """Indique si une ligne est un separateur de table markdown."""
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in split_row(line))


def extract_acceptance_criteria(text: str) -> list[dict[str, str]]:
    """Retourne les criteres d'acceptation trouves dans la premiere table AC."""
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        headers = split_row(line)
        normalized = [header.casefold() for header in headers]
        if "ac" not in normalized or "requirement" not in normalized:
            continue
        if not is_separator(lines[index + 1]):
            continue

        ac_index = normalized.index("ac")
        requirement_index = normalized.index("requirement")
        evidence_index = next(
            (
                position
                for position, header in enumerate(normalized)
                if header
                in {"validation evidence required", "verification", "evidence"}
            ),
            None,
        )
        result: list[dict[str, str]] = []
        row_index = index + 2
        while row_index < len(lines) and "|" in lines[row_index]:
            cells = split_row(lines[row_index])
            if len(cells) > max(ac_index, requirement_index):
                result.append(
                    {
                        "ac": cells[ac_index],
                        "requirement": cells[requirement_index],
                        "evidence": cells[evidence_index]
                        if evidence_index is not None and len(cells) > evidence_index
                        else "",
                    }
                )
            row_index += 1
        return result
    return []


def main() -> int:
    """Execute l'extraction depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Extract CONDAMAD story ACs.")
    parser.add_argument("story", type=Path, help="Path to 00-story.md.")
    args = parser.parse_args()

    story = args.story.expanduser().resolve()
    if not story.is_file():
        print(f"Story not found: {story}", file=sys.stderr)
        return 1

    print(json.dumps(extract_acceptance_criteria(read_text(story)), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
