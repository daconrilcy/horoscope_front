#!/usr/bin/env python3
"""Scanne des chemins cibles pour reperer les marqueurs No Legacy interdits.

Le script est conservateur: il signale les correspondances et ne renvoie un
code non nul que lorsque `--fail-on-hit` est demande.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterator
from pathlib import Path

DEFAULT_PATTERNS = [
    r"\blegacy\b",
    r"\bcompat\b",
    r"\bcompatibility\b",
    r"\bshim\b",
    r"\bfallback\b",
    r"\bdeprecated\b",
    r"\balias\b",
    r"\bre-export\b",
]

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "coverage",
}

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".scss",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def should_ignore(path: Path) -> bool:
    """Indique si un chemin appartient a un dossier genere ou volumineux."""
    return any(part in IGNORED_DIRS for part in path.parts)


def iter_files(paths: list[Path]) -> Iterator[Path]:
    """Enumere les fichiers texte candidats dans les chemins fournis."""
    for root in paths:
        if not root.exists():
            continue
        if root.is_file():
            if not should_ignore(root):
                yield root
            continue
        for path in root.rglob("*"):
            if path.is_file() and not should_ignore(path):
                if path.suffix.lower() in TEXT_SUFFIXES or not path.suffix:
                    yield path


def iter_artifact_paths(paths: list[Path]) -> Iterator[Path]:
    """Enumere les chemins eux-memes sans ignorer les dossiers generes."""
    for root in paths:
        if not root.exists():
            continue
        yield root
        if root.is_dir():
            yield from root.rglob("*")


def compile_patterns(patterns: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    """Compile les motifs tout en conservant leur texte source."""
    return [(pattern, re.compile(pattern, re.IGNORECASE)) for pattern in patterns]


def display_path(path: Path, base: Path) -> str:
    """Retourne un chemin relatif quand cela est possible."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path)


def scan(
    paths: list[Path], patterns: list[str], base: Path, path_only: bool = False
) -> list[tuple[str, int, str, str]]:
    """Retourne les lignes qui correspondent aux motifs interdits."""
    compiled = compile_patterns(patterns)
    findings: list[tuple[str, int, str, str]] = []
    candidates = iter_artifact_paths(paths) if path_only else iter_files(paths)
    for path in candidates:
        shown = display_path(path, base)
        if path_only:
            for pattern, regex in compiled:
                if regex.search(shown):
                    findings.append((shown, 0, pattern, shown))
                    break
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            for pattern, regex in compiled:
                if regex.search(line):
                    findings.append(
                        (shown, lineno, pattern, line.strip())
                    )
                    break
    return findings


def is_artifact_only_scan(patterns: list[str]) -> bool:
    """Detecte le scan final dedie aux artefacts packages Python."""
    joined = "|".join(patterns)
    return all(token in joined for token in ["__pycache__", ".pyc", ".pyo"])


def main() -> int:
    """Execute le scan depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Scan refactor targets.")
    parser.add_argument("paths", nargs="*", type=Path, default=[Path(".")])
    parser.add_argument("--pattern", action="append", dest="patterns")
    parser.add_argument("--only-custom-patterns", action="store_true")
    parser.add_argument("--fail-on-hit", action="store_true")
    args = parser.parse_args()

    if args.only_custom_patterns and not args.patterns:
        parser.error("--only-custom-patterns requires at least one --pattern")

    artifact_only = bool(args.patterns) and is_artifact_only_scan(args.patterns)
    patterns = (
        args.patterns
        if args.only_custom_patterns or artifact_only
        else DEFAULT_PATTERNS + (args.patterns or [])
    )
    try:
        compile_patterns(patterns)
    except re.error as exc:
        parser.error(f"invalid regex pattern: {exc}")

    base = Path.cwd()
    findings = scan(
        [path.expanduser().resolve() for path in args.paths],
        patterns,
        base,
        path_only=artifact_only,
    )
    if not findings:
        print("CONDAMAD refactor scan: no findings")
        return 0

    print(f"CONDAMAD refactor scan: {len(findings)} finding(s)")
    for path, lineno, pattern, line in findings[:500]:
        location = path if lineno == 0 else f"{path}:{lineno}"
        print(f"{location}: /{pattern}/ {line}")
    if len(findings) > 500:
        print(f"... truncated {len(findings) - 500} additional finding(s)")
    return 1 if args.fail_on_hit else 0


if __name__ == "__main__":
    sys.exit(main())
