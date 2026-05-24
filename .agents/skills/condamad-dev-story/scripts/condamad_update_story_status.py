#!/usr/bin/env python3
"""Met à jour une ligne story-status.md par identifiant CS-xxx exact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def split_markdown_row(line: str) -> list[str]:
    """Découpe une ligne de table markdown en préservant les pipes échappés."""
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


def replace_row(path: Path, story_id: str, new_row: str) -> tuple[str, str]:
    """Remplace exactement une ligne markdown pour story_id."""
    text = path.read_text(encoding="utf-8")
    row_re = re.compile(rf"^\|\s*{re.escape(story_id)}\s*\|.*$", re.I | re.M)
    matches = list(row_re.finditer(text))
    if not matches:
        raise SystemExit(f"No exact story-status row found for {story_id}")
    if len(matches) > 1:
        raise SystemExit(f"Multiple story-status rows found for {story_id}")

    before = matches[0].group(0)
    normalized = new_row.strip()
    if not normalized.startswith("|") or not normalized.endswith("|"):
        raise SystemExit(
            "New row must be a complete markdown table row starting and ending with '|'."
        )
    cells = split_markdown_row(normalized)
    if not cells or cells[0].upper() != story_id:
        raise SystemExit(
            f"New row must keep {story_id} as the first markdown table cell."
        )
    before_cells = split_markdown_row(before)
    if len(cells) != len(before_cells):
        raise SystemExit(
            f"New row must keep {len(before_cells)} markdown table cells; got {len(cells)}."
        )
    updated = text[: matches[0].start()] + normalized + text[matches[0].end() :]
    path.write_text(updated, encoding="utf-8")
    return before, normalized


def main() -> int:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(description="Update one CONDAMAD story status row.")
    parser.add_argument("story_id", help="Exact story id, for example CS-246.")
    parser.add_argument("new_row", help="Complete replacement markdown table row.")
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path("_condamad/stories/story-status.md"),
        help="Path to story-status.md.",
    )
    args = parser.parse_args()

    status_file = args.status_file.expanduser().resolve()
    if not status_file.is_file():
        raise SystemExit(f"story-status.md not found: {status_file}")

    before, after = replace_row(status_file, args.story_id.upper(), args.new_row)
    print("Before:")
    print(before)
    print("After:")
    print(after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
