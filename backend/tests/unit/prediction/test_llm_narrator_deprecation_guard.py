"""Garde les tests de prediction contre le retour du narrateur deprecie."""

from __future__ import annotations

import ast
from pathlib import Path

_LEGACY_CLASS = "LLM" + "Narrator"
_LEGACY_MODULE = "app.prediction.llm_narrator"
_LEGACY_PATCH_TARGET = _LEGACY_MODULE + "." + _LEGACY_CLASS + ".narrate"


def _backend_root() -> Path:
    """Retourne la racine backend depuis ce test."""
    return Path(__file__).resolve().parents[3]


def _test_files(root: Path) -> list[Path]:
    """Liste les tests collectables dans les deux racines backend connues."""
    roots = [root / "tests", root / "app" / "tests"]
    files: list[Path] = []
    for test_root in roots:
        files.extend(sorted(test_root.rglob("test_*.py")))
    return files


def test_prediction_tests_do_not_reintroduce_deprecated_narrator_class() -> None:
    """Echoue si un test redevient consommateur nominal de la classe depreciee."""
    root = _backend_root()
    violations: list[str] = []

    for file_path in _test_files(root):
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(root)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == _LEGACY_MODULE:
                for alias in node.names:
                    if alias.name == _LEGACY_CLASS:
                        violations.append(f"{relative}: imports deprecated narrator class")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == _LEGACY_CLASS:
                    violations.append(f"{relative}: instantiates deprecated narrator class")
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == _LEGACY_PATCH_TARGET:
                        violations.append(f"{relative}: patches deprecated narrator method")

    assert not violations, (
        "Deprecated narrator class usage is forbidden in nominal tests.\n- "
        + "\n- ".join(violations)
    )
