#!/usr/bin/env python3
"""Collecte les preuves git d'une refactorisation CONDAMAD.

Le collecteur ne modifie pas le code applicatif. Il ecrit ou remplace une
section idempotente entre marqueurs dans un fichier Markdown de preuves.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

START_MARKER = "<!-- CONDAMAD:REFACTOR-EVIDENCE:START -->"
END_MARKER = "<!-- CONDAMAD:REFACTOR-EVIDENCE:END -->"

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
    """Execute une commande et capture code, sortie standard et erreur."""
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def fenced(command: list[str], code: int, stdout: str, stderr: str) -> str:
    """Formate la preuve d'une commande dans un bloc Markdown."""
    lines = [f"### `{' '.join(command)}`", "", f"Exit code: `{code}`", ""]
    lines.extend(["```text", stdout or "<empty>", "```", ""])
    if stderr:
        lines.extend(["stderr:", "", "```text", stderr, "```", ""])
    return "\n".join(lines)


def build_snapshot(root: Path) -> tuple[str, int]:
    """Construit l'instantane git et retourne le code maximal observe."""
    lines = [
        "## CONDAMAD Refactor Git Evidence",
        "",
        f"Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        f"Repository root: `{root}`",
        "",
    ]
    max_exit = 0
    for command in GIT_COMMANDS:
        code, stdout, stderr = run(command, root)
        max_exit = max(max_exit, 1 if code == 127 else code)
        lines.append(fenced(command, code, stdout, stderr))
    return "\n".join(lines).rstrip() + "\n", max_exit


def wrap_snapshot(snapshot: str) -> str:
    """Ajoute les marqueurs idempotents autour de l'instantane."""
    return f"{START_MARKER}\n{snapshot.rstrip()}\n{END_MARKER}\n"


def upsert_marked_section(existing: str, marked_snapshot: str) -> str:
    """Insere ou remplace la section marquee dans un document Markdown."""
    start = existing.find(START_MARKER)
    end = existing.find(END_MARKER)
    if start >= 0 and end > start:
        after = end + len(END_MARKER)
        prefix = existing[:start].rstrip()
        suffix = existing[after:].strip()
        parts = [part for part in [prefix, marked_snapshot.rstrip(), suffix] if part]
        return "\n\n".join(parts).rstrip() + "\n"
    base = existing.rstrip()
    if base:
        return f"{base}\n\n{marked_snapshot}"
    return marked_snapshot


def resolve_under_root(root: Path, output: Path) -> Path:
    """Resout un chemin relatif sous la racine fournie."""
    expanded = output.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (root / expanded).resolve()


def write_snapshot(output: Path, marked_snapshot: str) -> None:
    """Ecrit la preuve en preservant le contenu manuel hors marqueurs."""
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = output.read_text(encoding="utf-8") if output.exists() else ""
    output.write_text(
        upsert_marked_section(existing, marked_snapshot),
        encoding="utf-8",
    )


def main() -> int:
    """Execute la collecte depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Collect refactor git evidence.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    output = resolve_under_root(root, args.output)
    snapshot, max_exit = build_snapshot(root)
    write_snapshot(output, wrap_snapshot(snapshot))
    print(f"Refactor evidence snapshot written: {output}")
    return 0 if max_exit == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
