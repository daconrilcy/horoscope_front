# Garde de frontiere entre taches planifiables et outils backend.
"""Verifie que les taches planifiables restent sous un owner explicite."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = BACKEND_ROOT / "app"
SCHEDULED_TASKS_ROOT = APP_ROOT / "scheduled_tasks"
REMOVED_JOBS_ROOT = APP_ROOT / "jobs"
TEST_ROOTS = (APP_ROOT, BACKEND_ROOT / "tests", BACKEND_ROOT / "scripts")

ALLOWED_SCHEDULED_TASK_MODULES = {
    "__init__.py",
}
FORBIDDEN_IMPORT_PREFIXES = (
    "app.jobs",
    "app.jobs.calibration",
    "app.jobs.qa",
)
ALLOWED_SCHEDULED_TASK_IMPORTS: set[str] = set()


def _python_files(root: Path) -> list[Path]:
    """Retourne les fichiers Python collectables sous une racine existante."""
    if not root.exists():
        return []
    return [path for path in root.rglob("*.py") if "__pycache__" not in path.parts]


def _imports_from_file(path: Path) -> set[str]:
    """Extrait les imports absolus depuis un fichier Python."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_scheduled_tasks_package_contains_only_schedulable_entrypoints() -> None:
    """La racine scheduled_tasks reste bornee aux traitements planifiables."""
    current_modules = {path.name for path in SCHEDULED_TASKS_ROOT.glob("*.py")}

    assert current_modules == ALLOWED_SCHEDULED_TASK_MODULES
    assert not REMOVED_JOBS_ROOT.exists()


def test_scheduled_tasks_package_marker_has_no_executable_logic() -> None:
    """Le package marker ne doit pas importer de logique executable."""
    tree = ast.parse((SCHEDULED_TASKS_ROOT / "__init__.py").read_text(encoding="utf-8"))
    executable_nodes = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(getattr(node, "value", None), ast.Constant)
            or isinstance(node, ast.ImportFrom)
            and node.module == "__future__"
            and [alias.name for alias in node.names] == ["annotations"]
        )
    ]

    assert executable_nodes == []


def test_non_job_helpers_are_not_imported_from_removed_jobs_namespace() -> None:
    """Les consommateurs doivent cibler les owners canoniques non-job."""
    offenders: list[str] = []
    for root in TEST_ROOTS:
        for path in _python_files(root):
            relative = path.relative_to(BACKEND_ROOT).as_posix()
            for imported in _imports_from_file(path):
                if imported.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    offenders.append(f"{relative}: {imported}")
                elif (
                    imported.startswith("app.scheduled_tasks.")
                    and imported not in ALLOWED_SCHEDULED_TASK_IMPORTS
                ):
                    offenders.append(f"{relative}: {imported}")

    assert sorted(offenders) == []
