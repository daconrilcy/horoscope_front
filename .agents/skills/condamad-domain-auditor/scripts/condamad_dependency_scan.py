#!/usr/bin/env python3
"""Scanne des imports et symboles interdits dans un perimetre donne."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Hit:
    """Occurrence d'un import ou symbole interdit."""

    path: Path
    line: int
    token: str
    kind: str
    text: str


def iter_python_files(source: Path, ignore: list[str]) -> list[Path]:
    """Liste les fichiers Python inclus dans le scan."""
    paths = [source] if source.is_file() else list(source.rglob("*.py"))
    return [
        path
        for path in paths
        if not any(
            fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern)
            for pattern in ignore
        )
    ]


def imported_names(tree: ast.AST) -> list[tuple[int, str]]:
    """Extrait les imports Python sous forme de noms pleinement qualifiables."""
    names: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.append((node.lineno, module))
            for alias in node.names:
                names.append((node.lineno, alias.name))
                names.append(
                    (node.lineno, f"{module}.{alias.name}" if module else alias.name)
                )
    return names


def attribute_name(node: ast.AST) -> str | None:
    """Construit un nom qualifie depuis une expression attribut si possible."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = attribute_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def symbol_names(tree: ast.AST) -> list[tuple[int, str]]:
    """Extrait les symboles Python reels sans scanner commentaires et strings."""
    names: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append((node.lineno, node.id))
        elif isinstance(node, ast.Attribute):
            name = attribute_name(node)
            if name:
                names.append((node.lineno, name))
    return names


def scan_source(source: Path, forbidden: list[str], ignore: list[str]) -> list[Hit]:
    """Retourne toutes les occurrences interdites."""
    hits: list[Hit] = []
    for path in iter_python_files(source, ignore):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            tree = None
            hits.append(
                Hit(
                    path,
                    exc.lineno or 1,
                    "syntax-error",
                    "parse-error",
                    (exc.text or "Python syntax error").strip(),
                )
            )
        if tree is not None:
            for line, name in imported_names(tree):
                for token in forbidden:
                    already_hit = any(
                        hit.path == path and hit.line == line and hit.token == token
                        for hit in hits
                    )
                    if (
                        name == token or name.startswith(f"{token}.")
                    ) and not already_hit:
                        line_text = (
                            text.splitlines()[line - 1].strip()
                            if line <= len(text.splitlines())
                            else ""
                        )
                        hits.append(Hit(path, line, token, "import", line_text))
        if tree is None:
            continue
        for line_number, name in symbol_names(tree):
            for token in forbidden:
                already_hit = any(
                    hit.path == path and hit.line == line_number and hit.token == token
                    for hit in hits
                )
                if (
                    name == token or name.startswith(f"{token}.")
                ) and not already_hit:
                    line_text = (
                        text.splitlines()[line_number - 1].strip()
                        if line_number <= len(text.splitlines())
                        else ""
                    )
                    hits.append(Hit(path, line_number, token, "symbol", line_text))
    return hits


def main() -> int:
    """Execute le scan de dependances interdites."""
    parser = argparse.ArgumentParser(description="Scan forbidden imports and symbols.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--forbid", nargs="+", required=True)
    parser.add_argument("--fail-on-hit", action="store_true")
    parser.add_argument("--ignore", action="append", default=[])
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.exists():
        print(f"ERROR: source does not exist: {source}", file=sys.stderr)
        return 2
    hits = scan_source(source, args.forbid, args.ignore)
    for hit in hits:
        print(f"{hit.path}:{hit.line}: {hit.kind}: forbidden {hit.token}: {hit.text}")
    if not hits:
        print("No forbidden dependency hit.")
    has_blocking_hit = any(hit.kind != "parse-error" for hit in hits)
    has_parse_error = any(hit.kind == "parse-error" for hit in hits)
    if has_parse_error:
        return 2
    return 1 if has_blocking_hit and args.fail_on_hit else 0


if __name__ == "__main__":
    raise SystemExit(main())
