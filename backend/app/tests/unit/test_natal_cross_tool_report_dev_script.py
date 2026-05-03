# Garde du contrat dev-only pour le rapport natal cross-tool.
"""Verifie que le script natal cross-tool reste borne au developpement local."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "natal-cross-tool-report-dev.py"
ROOT_SCRIPTS_DIR = REPO_ROOT / "scripts"
BACKEND_APP_ROOT = BACKEND_ROOT / "app"


def _python_files(root: Path) -> list[Path]:
    """Retourne les fichiers Python applicables en ignorant les caches locaux."""
    return [
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts and ".tmp-pytest" not in path.parts
    ]


def _imports_module(file_path: Path, module_name: str) -> bool:
    """Indique si un fichier importe directement un module donne."""
    tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(
                alias.name == module_name or alias.name.startswith(f"{module_name}.")
                for alias in node.names
            ):
                return True
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == module_name or node.module.startswith(f"{module_name}."):
                return True
    return False


def test_natal_cross_tool_report_script_refuses_ci_execution() -> None:
    """Le script racine echoue explicitement quand `CI=true`."""
    env = os.environ.copy()
    env["CI"] = "true"
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--limit", "0", "--format", "json"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "dev-only" in result.stderr
    assert "forbidden in CI" in result.stderr


def test_natal_cross_tool_report_is_the_only_runtime_adjacent_golden_import() -> None:
    """Les fixtures golden ne doivent pas etre consommees par le runtime backend."""
    offenders: list[str] = []
    for file_path in _python_files(BACKEND_APP_ROOT):
        relative = file_path.relative_to(BACKEND_ROOT).as_posix()
        if relative.startswith("app/tests/"):
            continue
        if _imports_module(file_path, "app.tests.golden"):
            offenders.append(relative)

    assert offenders == []
    assert _imports_module(SCRIPT_PATH, "app.tests.golden")


def test_cross_tool_report_helper_is_not_duplicated_under_root_scripts() -> None:
    """Le helper cross-tool reste dans le package backend `scripts`."""
    duplicated_helpers = sorted(
        path.name
        for path in ROOT_SCRIPTS_DIR.glob("cross_tool_report*.py")
        if path.name != "natal-cross-tool-report-dev.py"
    )

    assert duplicated_helpers == []
    assert _imports_module(SCRIPT_PATH, "scripts.cross_tool_report")
