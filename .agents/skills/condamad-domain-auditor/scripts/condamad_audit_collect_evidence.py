#!/usr/bin/env python3
"""Collecte des preuves read-only et met a jour l'evidence log d'un audit."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AUDIT_ROOT_PARTS = ("_condamad", "audits")
MARKER_START = "<!-- condamad-domain-auditor:evidence:start -->"
MARKER_END = "<!-- condamad-domain-auditor:evidence:end -->"


def is_audit_path(path: Path, repo_root: Path) -> bool:
    """Verifie que la cible se trouve sous _condamad/audits du repository."""
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return (
        len(relative.parts) >= 4
        and relative.parts[0:2] == AUDIT_ROOT_PARTS
        and all(part.strip() for part in relative.parts[2:])
    )


def run_command(
    command: list[str] | str, cwd: Path, timeout: int = 30, shell: bool = False
) -> tuple[int, str]:
    """Execute une commande de collecte sans modifier le code applicatif."""
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
            shell=shell,
        )
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + (exc.stderr or "")).strip()
        notes = output[:300].replace("\n", "<br>")
        return 124, f"timeout after {timeout}s" + (f"; {notes}" if notes else "")
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode, output[:500].replace("\n", "<br>")


def evidence_row(
    evidence_id: str, evidence_type: str, command: str, result: str, notes: str
) -> str:
    """Formate une ligne d'evidence log."""
    return (
        f"| {escape_table_cell(evidence_id)} | {escape_table_cell(evidence_type)} | "
        f"`{escape_table_cell(command)}` | {escape_table_cell(result)} | "
        f"{escape_table_cell(notes)} |"
    )


def escape_table_cell(value: str) -> str:
    """Echappe les caracteres qui cassent une cellule de tableau Markdown."""
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def update_evidence_log(audit_folder: Path, rows: list[str], repo_root: Path) -> None:
    """Met a jour uniquement le fichier d'evidence log sous _condamad/audits."""
    if not is_audit_path(audit_folder, repo_root):
        raise ValueError("audit folder must be under _condamad/audits")
    audit_folder.mkdir(parents=True, exist_ok=True)
    path = audit_folder / "01-evidence-log.md"
    existing = (
        path.read_text(encoding="utf-8")
        if path.exists()
        else "# Evidence Log\n\n| ID | Evidence type | Command / Source | Result | Notes |\n|---|---|---|---|---|\n"
    )
    block = "\n".join(
        [
            MARKER_START,
            f"<!-- updated: {datetime.now().isoformat(timespec='minutes')} -->",
            *rows,
            MARKER_END,
        ]
    )
    if MARKER_START in existing and MARKER_END in existing:
        before = existing.split(MARKER_START, 1)[0].rstrip()
        after = existing.split(MARKER_END, 1)[1].lstrip()
        content = f"{before}\n{block}\n{after}"
    else:
        content = existing.rstrip() + "\n" + block + "\n"
    path.write_text(content, encoding="utf-8")


def main() -> int:
    """Collecte git status et scans rg demandes par le profil."""
    parser = argparse.ArgumentParser(
        description="Collect read-only evidence into 01-evidence-log.md."
    )
    parser.add_argument("audit_folder", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--rg", action="append", default=[], help="rg pattern to run from repo root."
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Path arguments appended to every rg command.",
    )
    parser.add_argument(
        "--dependency-scan-source",
        action="append",
        default=[],
        help="Source path for optional condamad_dependency_scan.py evidence.",
    )
    parser.add_argument(
        "--forbid",
        nargs="+",
        default=[],
        help="Forbidden imports or symbols used by dependency scans.",
    )
    parser.add_argument(
        "--runtime-command",
        action="append",
        default=[],
        help="Optional read-only runtime evidence command to run from repo root.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    audit_folder = args.audit_folder.expanduser().resolve()
    if not is_audit_path(audit_folder, repo_root):
        print(
            "ERROR: evidence collector may write only under _condamad/audits/**",
            file=sys.stderr,
        )
        return 2

    rows: list[str] = []
    code, output = run_command(["git", "status", "--short"], repo_root)
    rows.append(
        evidence_row(
            "E-001",
            "repo-state",
            "git status --short",
            "PASS" if code == 0 else "FAIL",
            output or "clean",
        )
    )
    next_id = 2
    for pattern in args.rg:
        command = ["rg", "-n", "--", pattern, *args.path]
        code, output = run_command(command, repo_root)
        result = "PASS" if code in {0, 1} else "FAIL"
        rows.append(
            evidence_row(
                f"E-{next_id:03d}",
                "static-scan",
                " ".join(command),
                result,
                output or "no hit",
            )
        )
        next_id += 1
    if args.dependency_scan_source and not args.forbid:
        rows.append(
            evidence_row(
                f"E-{next_id:03d}",
                "dependency-scan",
                "condamad_dependency_scan.py",
                "FAIL",
                "--forbid is required when --dependency-scan-source is used",
            )
        )
        next_id += 1
    for source in args.dependency_scan_source if args.forbid else []:
        script = Path(__file__).with_name("condamad_dependency_scan.py")
        command = [
            sys.executable,
            "-S",
            "-B",
            str(script),
            "--source",
            source,
            "--forbid",
            *args.forbid,
            "--fail-on-hit",
        ]
        code, output = run_command(command, repo_root)
        rows.append(
            evidence_row(
                f"E-{next_id:03d}",
                "dependency-scan",
                " ".join(command),
                "PASS" if code == 0 else "FAIL",
                output or "no forbidden dependency hit",
            )
        )
        next_id += 1
    for runtime_command in args.runtime_command:
        code, output = run_command(runtime_command, repo_root, shell=True)
        rows.append(
            evidence_row(
                f"E-{next_id:03d}",
                "runtime-command",
                runtime_command,
                "PASS" if code == 0 else "FAIL",
                output or "completed with no output",
            )
        )
        next_id += 1
    update_evidence_log(audit_folder, rows, repo_root)
    print(f"Updated {audit_folder / '01-evidence-log.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
