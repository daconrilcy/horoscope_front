#!/usr/bin/env python3
"""Linte une story CONDAMAD au-dela du contrat bloquant.

Ce lint garde la story lisible pour Codex: pas de marqueurs de gabarit, pas de
lignes demesurees et pas de sections vides.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from condamad_story_validate import (
    REQUIRED_SECTIONS,
    get_section,
    read_text,
    validate_story,
)

MAX_LINE_LENGTH = 180
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\.\.\.")


def lint_story(path: Path) -> list[str]:
    """Retourne les erreurs de lint detectees dans la story."""
    errors = validate_story(path)
    if errors:
        return errors

    text = read_text(path)
    for index, line in enumerate(text.splitlines(), start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(f"Line {index} exceeds {MAX_LINE_LENGTH} characters")
    if PLACEHOLDER_RE.search(text):
        errors.append("Story still contains template placeholders")
    for section in REQUIRED_SECTIONS:
        if not get_section(text, section).strip():
            errors.append(f"Section is empty: {section}")
    return errors


def main() -> int:
    """Execute le lint depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Lint a CONDAMAD story file.")
    parser.add_argument(
        "story", type=Path, help="Path to a CONDAMAD story markdown file."
    )
    args = parser.parse_args()

    errors = lint_story(args.story.expanduser().resolve())
    if errors:
        print("CONDAMAD story lint: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONDAMAD story lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
