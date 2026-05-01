"""Garde la prediction contre le retour du narrateur LLM deprecie."""

from __future__ import annotations

import ast
from pathlib import Path

_LEGACY_CLASS = "LLM" + "Narrator"
_LEGACY_MODULE = "app.prediction.llm_narrator"
_LEGACY_PATCH_TARGET = _LEGACY_MODULE + "." + _LEGACY_CLASS + ".narrate"
_DIRECT_PROVIDER_TYPE = "openai" + "." + "AsyncOpenAI"
_DIRECT_CHAT_CALL = "chat" + "." + "completions" + "." + "create"
_CANONICAL_PROVIDER_PARTS = ("app", "infra", "providers", "llm")


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


def _source_files(root: Path) -> list[Path]:
    """Liste les sources applicatives et tests a inspecter par AST."""
    roots = [root / "app", root / "tests"]
    files: list[Path] = []
    for source_root in roots:
        files.extend(
            sorted(
                path
                for path in source_root.rglob("*.py")
                if "__pycache__" not in path.parts and path.name != Path(__file__).name
            )
        )
    return files


def _is_canonical_provider(file_path: Path) -> bool:
    """Indique si le fichier appartient au provider LLM autorise."""
    return all(part in file_path.parts for part in _CANONICAL_PROVIDER_PARTS)


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


def test_prediction_runtime_does_not_reintroduce_legacy_narrator_surface() -> None:
    """Echoue si la facade runtime legacy redevient importable ou instanciable."""
    root = _backend_root()
    legacy_path = root / "app" / "prediction" / "llm_narrator.py"
    violations: list[str] = []
    if legacy_path.exists():
        violations.append(f"{legacy_path.relative_to(root)} exists")

    for file_path in _source_files(root):
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        relative = file_path.relative_to(root)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == _LEGACY_MODULE:
                violations.append(f"{relative}: imports deprecated narrator module")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == _LEGACY_CLASS:
                    violations.append(f"{relative}: instantiates deprecated narrator class")

    assert not violations, "Legacy narrator runtime surface detected.\n- " + "\n- ".join(violations)


def test_non_provider_sources_do_not_call_openai_directly() -> None:
    """Echoue si un module hors provider canonique appelle directement OpenAI."""
    root = _backend_root()
    violations: list[str] = []

    for file_path in _source_files(root):
        if _is_canonical_provider(file_path):
            continue
        source = file_path.read_text(encoding="utf-8")
        relative = file_path.relative_to(root)
        if _DIRECT_PROVIDER_TYPE in source:
            violations.append(f"{relative}: constructs direct provider client")
        if _DIRECT_CHAT_CALL in source:
            violations.append(f"{relative}: calls direct chat completion API")

    assert not violations, "Direct provider calls outside canonical provider detected.\n- " + (
        "\n- ".join(violations)
    )
