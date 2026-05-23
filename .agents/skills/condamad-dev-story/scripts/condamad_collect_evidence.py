#!/usr/bin/env python3
"""Collecte des preuves CONDAMAD finales depuis git.

Ce helper insere un instantane horodate et idempotent dans la preuve finale.
Il distingue les changements non stages, stages, totaux depuis HEAD et les
fichiers non suivis pour rendre la revue CONDAMAD explicite.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

START_MARKER = "<!-- CONDAMAD:EVIDENCE-SNAPSHOT:START -->"
END_MARKER = "<!-- CONDAMAD:EVIDENCE-SNAPSHOT:END -->"

GIT_COMMANDS = [
    ["git", "status", "--short"],
    ["git", "diff", "--stat"],
    ["git", "diff", "--name-status"],
    ["git", "diff", "--cached", "--stat"],
    ["git", "diff", "--cached", "--name-status"],
    ["git", "diff", "HEAD", "--stat"],
    ["git", "diff", "HEAD", "--name-status"],
    ["git", "ls-files", "--others", "--exclude-standard"],
    ["git", "diff", "--check"],
]


def run(command: list[str], cwd: Path) -> tuple[int, str, str]:
    """Execute une commande et retourne son code de sortie et ses flux texte."""
    try:
        proc = subprocess.run(
            command, cwd=cwd, text=True, capture_output=True, check=False
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def fenced(command: str, code: int, stdout: str, stderr: str) -> str:
    """Formate la sortie d'une commande dans une section Markdown lisible."""
    body = [f"### `{command}`", "", f"Exit code: `{code}`", ""]
    body.extend(["```text", stdout or "<empty>", "```", ""])
    if stderr:
        body.extend(["stderr:", "", "```text", stderr, "```", ""])
    return "\n".join(body)


def resolve_output_path(output: Path, root: Path) -> Path:
    """Resout un chemin de sortie relatif depuis la racine du depot cible."""
    expanded = output.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (root / expanded).resolve()


def resolve_capsule_path(capsule: Path, root: Path) -> Path:
    """Resout une capsule relative depuis la racine du depot cible."""
    expanded = capsule.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (root / expanded).resolve()


def build_snapshot(root: Path) -> tuple[str, int]:
    """Construit la section de preuve git et retourne le code maximal observe."""
    sections = [
        "## CONDAMAD Evidence Snapshot",
        "",
        f"Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"Repository root: `{root}`",
        "",
    ]
    max_exit = 0
    for command in GIT_COMMANDS:
        code, stdout, stderr = run(command, root)
        max_exit = max(max_exit, code if code != 127 else 1)
        sections.append(fenced(" ".join(command), code, stdout, stderr))
    return "\n".join(sections).rstrip() + "\n", max_exit


def wrap_snapshot(snapshot: str) -> str:
    """Encadre le snapshot avec les marqueurs CONDAMAD idempotents."""
    return f"{START_MARKER}\n{snapshot.rstrip()}\n{END_MARKER}\n"


def upsert_marked_section(existing: str, marked_snapshot: str) -> str:
    """Insere ou remplace la section marquee dans un document Markdown."""
    start_index = existing.find(START_MARKER)
    end_index = existing.find(END_MARKER)
    if start_index != -1 and end_index != -1 and end_index > start_index:
        after_end = end_index + len(END_MARKER)
        updated = existing[:start_index].rstrip()
        if updated:
            updated += "\n\n"
        updated += marked_snapshot.rstrip()
        tail = existing[after_end:].strip()
        if tail:
            updated += f"\n\n{tail}"
        return updated.rstrip() + "\n"

    base = existing.rstrip()
    if base:
        return f"{base}\n\n{marked_snapshot}"
    return marked_snapshot


def write_snapshot(output: Path, marked_snapshot: str) -> None:
    """Ecrit la section de preuve sans supprimer le contenu manuel existant."""
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = output.read_text(encoding="utf-8") if output.exists() else ""
    output.write_text(
        upsert_marked_section(existing, marked_snapshot), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect CONDAMAD git evidence.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--capsule",
        type=Path,
        help="Capsule path. If provided, default output is generated/10-final-evidence.md.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output markdown path. Defaults to stdout unless --capsule is given.",
    )
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    snapshot, max_exit = build_snapshot(root)
    content = wrap_snapshot(snapshot)
    output = resolve_output_path(args.output, root) if args.output else None
    if output is None and args.capsule:
        output = (
            resolve_capsule_path(args.capsule, root)
            / "generated"
            / "10-final-evidence.md"
        )
    if output:
        write_snapshot(output, content)
        print(f"Evidence snapshot written: {output}")
    else:
        print(content)
    return 0 if max_exit == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
