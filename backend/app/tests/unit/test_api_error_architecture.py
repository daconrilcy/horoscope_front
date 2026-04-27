"""Gardes d'architecture pour la centralisation des erreurs API."""

from __future__ import annotations

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = APP_ROOT / "api"
API_V1_ROOT = API_ROOT / "v1"
SERVICES_ROOT = APP_ROOT / "services"


def _python_files(root: Path) -> list[Path]:
    """Retourne les fichiers Python applicatifs d'une racine."""
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _source_tree(path: Path) -> ast.Module:
    """Parse un fichier Python pour inspecter les dépendances sans exécution."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_legacy_api_v1_error_module_is_deleted() -> None:
    """Empêche le retour du module historique `app.api.v1.errors`."""
    assert not (API_V1_ROOT / "errors.py").exists()


def test_backend_does_not_import_legacy_api_error_module() -> None:
    """Bloque les imports actifs vers l'ancien chemin d'erreurs."""
    offenders: list[str] = []
    for root in (APP_ROOT, Path(__file__).resolve().parents[3] / "tests"):
        if not root.exists():
            continue
        for path in _python_files(root):
            if path == Path(__file__) or path.name == "test_api_router_architecture.py":
                continue
            content = path.read_text(encoding="utf-8")
            if "app.api.v1.errors" in content or "api_error_response(" in content:
                offenders.append(str(path.relative_to(APP_ROOT.parents[0])))

    assert offenders == []


def test_application_error_is_not_defined_under_api() -> None:
    """La classe mère applicative ne doit pas vivre dans la couche API."""
    offenders: list[str] = []
    for path in _python_files(API_ROOT):
        tree = _source_tree(path)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "ApplicationError":
                offenders.append(str(path.relative_to(APP_ROOT)))

    assert offenders == []


def test_services_do_not_build_http_error_responses() -> None:
    """Les services ne doivent plus construire de réponses HTTP."""
    forbidden_imports = {"fastapi.responses", "app.api.v1.errors"}
    forbidden_names = {"JSONResponse", "HTTPException", "api_error_response"}
    offenders: list[str] = []
    for path in _python_files(SERVICES_ROOT):
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden_imports:
                offenders.append(
                    f"{path.relative_to(APP_ROOT)}:{node.lineno} imports {node.module}"
                )
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in forbidden_names:
                    offenders.append(f"{path.relative_to(APP_ROOT)}:{node.lineno} calls {func.id}")
            if isinstance(node, ast.FunctionDef) and node.name in {
                "_error_response",
                "_create_error_response",
            }:
                uses_application_error = any(
                    isinstance(child, ast.Name) and child.id == "ApplicationError"
                    for child in ast.walk(node)
                )
                if not uses_application_error:
                    offenders.append(f"{path.relative_to(APP_ROOT)}:{node.lineno} {node.name}")

    assert offenders == []


def test_services_do_not_encode_http_status_mapping() -> None:
    """Les services doivent laisser la traduction HTTP à la couche API."""
    offenders: list[str] = []
    for path in _python_files(SERVICES_ROOT):
        content = path.read_text(encoding="utf-8")
        if "status_code" in content or "error.status_code" in content:
            offenders.append(str(path.relative_to(APP_ROOT)))

    assert offenders == []


def test_api_handlers_do_not_read_legacy_error_status_code() -> None:
    """Les handlers API doivent passer par le catalogue ou http_status_code explicite."""
    offenders: list[str] = []
    for path in _python_files(API_ROOT):
        relative_path = path.relative_to(APP_ROOT)
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "status_code"
                and isinstance(node.value, ast.Name)
                and node.value.id == "error"
            ):
                offenders.append(f"{relative_path}:{node.lineno}")

    assert offenders == []


def test_api_http_exception_usage_is_removed() -> None:
    """Les routeurs ne doivent plus lever directement de HTTPException métier."""
    offenders: list[str] = []
    for path in _python_files(API_ROOT):
        relative_path = path.relative_to(API_ROOT)
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "HTTPException":
                    offenders.append(f"{relative_path}:{node.lineno}")

    assert offenders == []


def test_api_routes_do_not_build_error_envelopes_with_json_response() -> None:
    """Les routeurs doivent déléguer l'enveloppe d'erreur au builder central."""
    offenders: list[str] = []
    for path in _python_files(API_V1_ROOT / "routers"):
        relative_path = path.relative_to(APP_ROOT)
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "JSONResponse"
            ):
                continue
            for keyword in node.keywords:
                if keyword.arg != "content" or not isinstance(keyword.value, ast.Dict):
                    continue
                for key in keyword.value.keys:
                    if isinstance(key, ast.Constant) and key.value == "error":
                        offenders.append(f"{relative_path}:{node.lineno}")

    assert offenders == []
