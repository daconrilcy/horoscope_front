#!/usr/bin/env python3
"""Scanne des chemins choisis pour reperer les marqueurs de legacy.

Le script reste volontairement conservateur: par defaut, il affiche les
resultats mais sort avec le code 0. Utiliser `--fail-on-hit` dans les contextes
de validation stricts.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterator
from pathlib import Path

DEFAULT_PATTERNS = [
    r"\blegacy\b",
    r"\bcompat(?:ibility)?\b",
    r"\bshim\b",
    r"\bfallback\b",
    r"\bdeprecated\b",
    r"\balias\b",
]

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
}

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".scss",
    ".html",
    ".sql",
}


def iter_files(paths: list[Path]) -> Iterator[Path]:
    """Enumere les fichiers texte candidats en ignorant les dossiers generes."""
    for root in paths:
        if root.is_file():
            yield root
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_SUFFIXES or not path.suffix:
                yield path


def compile_patterns(patterns: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    """Compile les motifs de recherche en conservant leur texte d'origine."""
    return [(pattern, re.compile(pattern, re.I)) for pattern in patterns]


def scan(paths: list[Path], patterns: list[str]) -> list[tuple[Path, int, str, str]]:
    """Retourne les lignes qui contiennent au moins un marqueur interdit."""
    compiled = compile_patterns(patterns)
    findings: list[tuple[Path, int, str, str]] = []
    for path in iter_files(paths):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            for pattern, regex in compiled:
                if regex.search(line):
                    findings.append((path, lineno, pattern, line.strip()))
                    break
    return findings


def main() -> int:
    """Execute le scan depuis la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Scan for legacy/compatibility markers."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path(".")],
        help="Paths to scan. Defaults to current directory.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Additional or replacement regex pattern. May be repeated.",
    )
    parser.add_argument(
        "--only-custom-patterns",
        action="store_true",
        help="Use only --pattern values, not default legacy patterns.",
    )
    parser.add_argument(
        "--fail-on-hit", action="store_true", help="Exit 1 when findings exist."
    )
    args = parser.parse_args()

    if args.only_custom_patterns and not args.patterns:
        parser.error("--only-custom-patterns requires at least one --pattern value")

    patterns = (
        args.patterns
        if args.only_custom_patterns
        else DEFAULT_PATTERNS + (args.patterns or [])
    )
    try:
        compile_patterns(patterns)
    except re.error as exc:
        parser.error(f"invalid regex pattern: {exc}")

    findings = scan([p.expanduser().resolve() for p in args.paths], patterns)

    if not findings:
        print("CONDAMAD legacy scan: no findings")
        return 0

    print(f"CONDAMAD legacy scan: {len(findings)} finding(s)")
    for path, lineno, pattern, line in findings[:500]:
        print(f"{path}:{lineno}: /{pattern}/ {line}")
    if len(findings) > 500:
        print(f"... truncated {len(findings) - 500} additional finding(s)")
    return 1 if args.fail_on_hit else 0


if __name__ == "__main__":
    sys.exit(main())
