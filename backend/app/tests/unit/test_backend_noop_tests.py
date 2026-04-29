# Garde d'architecture contre les tests backend collectes sans comportement.
"""Bloque les tests backend vides ou les assertions triviales de type `assert True`."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
TEST_ROOTS = (BACKEND_ROOT / "app" / "tests", BACKEND_ROOT / "tests")
IGNORED_PARTS = {".pytest_cache", ".ruff_cache", "__pycache__"}


def _iter_backend_test_files() -> list[Path]:
    """Retourne les fichiers de tests backend collectables par convention."""
    files: list[Path] = []
    for root in TEST_ROOTS:
        if not root.exists():
            continue
        files.extend(
            path for path in root.rglob("test_*.py") if not IGNORED_PARTS.intersection(path.parts)
        )
    return sorted(files)


def _strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    """Retire la docstring d'une fonction pour analyser son comportement reel."""
    if not body:
        return []
    first_statement = body[0]
    if (
        isinstance(first_statement, ast.Expr)
        and isinstance(first_statement.value, ast.Constant)
        and isinstance(first_statement.value.value, str)
    ):
        return body[1:]
    return body


def _skip_call(statement: ast.stmt) -> ast.Call | None:
    """Retourne l'appel `pytest.skip` quand une fonction de test est volontairement vide."""
    if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
        return None
    call = statement.value
    function = call.func
    if isinstance(function, ast.Attribute):
        is_skip = (
            isinstance(function.value, ast.Name)
            and function.value.id == "pytest"
            and function.attr == "skip"
        )
    else:
        is_skip = isinstance(function, ast.Name) and function.id == "skip"
    if not is_skip:
        return None
    return call


def _is_explicit_skip(statement: ast.stmt) -> bool:
    """Identifie un `pytest.skip` motive comme absence volontaire de comportement."""
    call = _skip_call(statement)
    if call is None:
        return False
    reason_nodes = list(call.args)
    reason_nodes.extend(keyword.value for keyword in call.keywords if keyword.arg == "reason")
    return any(
        isinstance(reason_node, ast.Constant)
        and isinstance(reason_node.value, str)
        and bool(reason_node.value.strip())
        for reason_node in reason_nodes
    )


def _is_direct_noop_test(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Detecte les fonctions de test dont le corps executable est vide."""
    body = _strip_docstring(function.body)
    if len(body) == 1 and _skip_call(body[0]) is not None:
        return not _is_explicit_skip(body[0])
    return not body or all(isinstance(statement, ast.Pass) for statement in body)


def _assert_true_lines(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[int]:
    """Retourne les lignes qui utilisent `assert True` comme preuve triviale."""
    lines: list[int] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant):
            if node.test.value is True:
                lines.append(node.lineno)
    return lines


def test_backend_tests_do_not_keep_empty_test_bodies() -> None:
    """Aucun test backend collecte ne doit passer uniquement via `pass`."""
    offenders: list[str] = []
    for path in _iter_backend_test_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name.startswith("test_") and _is_direct_noop_test(node):
                    relative_path = path.relative_to(BACKEND_ROOT).as_posix()
                    offenders.append(f"{relative_path}::{node.name}")

    assert offenders == []


def test_backend_tests_do_not_use_assert_true_as_behavior() -> None:
    """Aucun test backend ne doit utiliser `assert True` comme assertion nominale."""
    offenders: list[str] = []
    for path in _iter_backend_test_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            for line_number in _assert_true_lines(node):
                relative_path = path.relative_to(BACKEND_ROOT).as_posix()
                offenders.append(f"{relative_path}:{line_number}::{node.name}")

    assert offenders == []


def test_backend_noop_guard_requires_non_empty_skip_reason() -> None:
    """La garde refuse un skip sans raison explicite et non vide."""
    empty_reason = ast.parse('def test_placeholder():\n    pytest.skip("")\n').body[0]
    blank_keyword_reason = ast.parse(
        'def test_placeholder():\n    pytest.skip(reason="   ")\n'
    ).body[0]
    documented_reason = ast.parse(
        'def test_placeholder():\n    pytest.skip("CONDAMAD-123 decision tracked")\n'
    ).body[0]

    assert isinstance(empty_reason, ast.FunctionDef)
    assert isinstance(blank_keyword_reason, ast.FunctionDef)
    assert isinstance(documented_reason, ast.FunctionDef)
    assert _is_direct_noop_test(empty_reason)
    assert _is_direct_noop_test(blank_keyword_reason)
    assert not _is_direct_noop_test(documented_reason)
