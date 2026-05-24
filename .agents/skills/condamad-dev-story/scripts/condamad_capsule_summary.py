#!/usr/bin/env python3
"""Produit un résumé compact d'une capsule CONDAMAD.

Le résumé reste volontairement borné pour charger le contexte utile sans
imprimer tous les fichiers générés.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

MAX_LINES = 120
SECTION_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
SUMMARY_INPUTS = [
    "00-story.md",
    "generated/03-acceptance-traceability.md",
    "generated/04-target-files.md",
    "generated/06-validation-plan.md",
    "generated/07-no-legacy-dry-guardrails.md",
]


def read_text(path: Path) -> str:
    """Lit le texte en tolérant les caractères invalides."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def section_lines(text: str, names: tuple[str, ...], limit: int = 18) -> list[str]:
    """Extrait quelques lignes depuis des sections markdown nommées."""
    wanted = tuple(name.casefold() for name in names)
    lines: list[str] = []
    in_section = False
    for line in text.splitlines():
        heading = SECTION_RE.match(line)
        if heading:
            in_section = any(name in heading.group(1).casefold() for name in wanted)
            if in_section:
                lines.append(line)
            continue
        if in_section and line.strip():
            lines.append(line)
            if len(lines) >= limit:
                break
    return lines


def table_rows(text: str, headers: tuple[str, ...], limit: int = 12) -> list[str]:
    """Extrait une table dont l'en-tête contient les libellés demandés."""
    result: list[str] = []
    capture = False
    for line in text.splitlines():
        if not TABLE_ROW_RE.match(line):
            if capture and result:
                break
            continue
        lower = line.casefold()
        if all(header.casefold() in lower for header in headers):
            capture = True
            result.append(line)
            continue
        if capture:
            result.append(line)
            if len(result) >= limit:
                break
    return result


def bullets(text: str, limit: int = 12) -> list[str]:
    """Retourne des lignes de liste compactes."""
    result: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")) or re.match(r"^\d+[.)]\s+", stripped):
            result.append(stripped)
            if len(result) >= limit:
                break
    return result


def append_block(output: list[str], title: str, lines: list[str]) -> None:
    """Ajoute un bloc titré quand le contenu existe."""
    if not lines:
        return
    output.append(f"## {title}")
    output.extend(lines)
    output.append("")


def build_summary(capsule: Path) -> list[str]:
    """Construit un résumé borné pour une capsule."""
    generated = capsule / "generated"
    story = read_text(capsule / "00-story.md")
    traceability = read_text(generated / "03-acceptance-traceability.md")
    target_files = read_text(generated / "04-target-files.md")
    validation = read_text(generated / "06-validation-plan.md")
    guardrails = read_text(generated / "07-no-legacy-dry-guardrails.md")
    final = read_text(generated / "10-final-evidence.md")

    output = [
        f"# Capsule Summary - {capsule.name}",
        f"- Capsule: `{capsule}`",
        f"- Story file: `{capsule / '00-story.md'}`",
        "",
    ]

    append_block(
        output,
        "Story Scope",
        section_lines(story, ("goal", "scope", "non-goal", "acceptance"), 20)
        or bullets(story, 10),
    )
    append_block(
        output,
        "Acceptance Criteria",
        table_rows(traceability, ("AC", "Requirement"), 18),
    )
    append_block(
        output,
        "Target Paths",
        section_lines(
            target_files,
            ("must inspect", "likely modified", "forbidden"),
            18,
        ),
    )
    append_block(
        output,
        "Validation",
        section_lines(
            validation,
            ("targeted", "early guard", "architecture", "lint", "full regression"),
            22,
        ),
    )
    append_block(
        output,
        "Guardrails",
        section_lines(guardrails, ("forbidden", "required", "reviewer"), 22),
    )
    append_block(
        output,
        "Final Evidence Skeleton",
        section_lines(final, ("story status", "remaining risks", "reviewer"), 12),
    )

    if len(output) > MAX_LINES:
        output = output[: MAX_LINES - 1] + ["... summary truncated at 120 lines"]
    return output


def main() -> int:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description="Print compact CONDAMAD capsule summary."
    )
    parser.add_argument("capsule", type=Path, help="Path to _condamad/stories/<story-key>.")
    args = parser.parse_args()

    capsule = args.capsule.expanduser().resolve()
    if not capsule.is_dir():
        raise SystemExit(f"Capsule directory not found: {capsule}")
    missing = [rel for rel in SUMMARY_INPUTS if not (capsule / rel).is_file()]
    if missing:
        formatted = ", ".join(missing)
        raise SystemExit(f"Capsule summary inputs missing: {formatted}")
    print("\n".join(build_summary(capsule)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
