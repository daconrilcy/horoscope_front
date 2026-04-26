"""Garde-fous d'architecture pour le classement des routeurs API v1."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

ROUTERS_ROOT = Path(__file__).resolve().parents[2] / "api" / "v1" / "routers"
CANONICAL_DOMAINS = {"admin", "b2b", "internal", "ops", "public"}
FORBIDDEN_FLAT_PREFIXES = ("admin_", "b2b_", "ops_")
FORBIDDEN_LEGACY_MODULES = (
    ".".join(("app", "api", "v1", "routers", "public", "ai")),
    "app.api.v1.routers.admin_llm",
    "app.api.v1.routers.admin_llm_assembly",
    "app.api.v1.routers.admin_llm_consumption",
    "app.api.v1.routers.admin_llm_release",
    "app.api.v1.routers.admin_llm_sample_payloads",
    "app.api.v1.routers.admin_ai",
    "app.api.v1.routers.b2b_astrology",
    "app.api.v1.routers.ops_monitoring",
)
FORBIDDEN_ROUTER_PREFIXES = ("/v1/" + "ai",)
FORBIDDEN_LEGACY_STRINGS = (
    "ai_engine" + "_router",
    "use_case" + "_compat",
    "legacy" + "_maintenance",
    "legacy" + "_alias",
    "legacy_registry" + "_only",
)
ALLOWED_ROUTER_CLASS_DEFINITIONS = {Path("admin") / "llm" / "error_codes.py": {"AdminLlmErrorCode"}}


def _python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs du package de routeurs."""
    return sorted(path for path in ROUTERS_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _source_tree(path: Path) -> ast.Module:
    """Parse un fichier routeur pour inspecter ses imports sans l'executer."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_router_modules_are_classified_under_domain_packages() -> None:
    """Les routeurs actifs ne doivent plus vivre comme modules plats par prefixe."""
    flat_modules = [
        path.name
        for path in ROUTERS_ROOT.glob("*.py")
        if path.name != "__init__.py" and path.stem.startswith(FORBIDDEN_FLAT_PREFIXES)
    ]

    assert flat_modules == []
    for domain in CANONICAL_DOMAINS:
        assert (ROUTERS_ROOT / domain).is_dir(), f"missing router domain {domain}"


def test_root_router_package_does_not_reexport_domain_routers() -> None:
    """Le package racine ne doit pas maintenir des imports de compatibilite."""
    tree = _source_tree(ROUTERS_ROOT / "__init__.py")
    imports = [node for node in tree.body if isinstance(node, ast.Import | ast.ImportFrom)]

    assert imports == []


@pytest.mark.parametrize("module_name", FORBIDDEN_LEGACY_MODULES)
def test_legacy_flat_router_modules_are_not_importable(module_name: str) -> None:
    """Les anciens chemins plats ne doivent plus servir de wrappers."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


def test_backend_code_uses_canonical_router_imports() -> None:
    """Les imports internes doivent cibler les sous-packages de domaine."""
    offenders: list[str] = []
    for path in _python_files():
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue
            module = node.module
            if not module.startswith("app.api.v1.routers."):
                continue
            suffix = module.removeprefix("app.api.v1.routers.").split(".", maxsplit=1)[0]
            if suffix.startswith(FORBIDDEN_FLAT_PREFIXES):
                offenders.append(f"{path.relative_to(ROUTERS_ROOT)} imports {module}")

    assert offenders == []


def test_router_modules_do_not_define_local_schemas() -> None:
    """Les schémas et classes de support doivent vivre hors des routeurs HTTP."""
    offenders: list[str] = []
    for path in _python_files():
        relative_path = path.relative_to(ROUTERS_ROOT)
        allowed_names = ALLOWED_ROUTER_CLASS_DEFINITIONS.get(relative_path, set())
        tree = _source_tree(path)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name not in allowed_names:
                offenders.append(f"{relative_path}:{node.lineno} defines {node.name}")

    assert offenders == []


def test_router_modules_do_not_define_private_helpers() -> None:
    """La logique non HTTP doit rester dans le package router_logic."""
    offenders: list[str] = []
    for path in _python_files():
        relative_path = path.relative_to(ROUTERS_ROOT)
        tree = _source_tree(path)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith(
                "_"
            ):
                offenders.append(f"{relative_path}:{node.lineno} defines {node.name}")

    assert offenders == []


def test_removed_historical_facade_prefix_is_not_registered() -> None:
    """Le prefixe public LLM historique ne doit plus etre expose par FastAPI."""
    from app.main import app

    paths = {getattr(route, "path", "") for route in app.routes}
    offenders = [
        path
        for path in paths
        if any(
            path == prefix or path.startswith(f"{prefix}/") for prefix in FORBIDDEN_ROUTER_PREFIXES
        )
    ]

    assert offenders == []


def test_removed_historical_facade_strings_do_not_return_in_backend_app() -> None:
    """Bloque le retour des champs, etats et aliases de facades historiques."""
    backend_app = Path(__file__).resolve().parents[2]
    offenders: list[str] = []
    for path in backend_app.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if path == Path(__file__):
            continue
        content = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_LEGACY_STRINGS:
            if token in content:
                offenders.append(f"{path.relative_to(backend_app)} contains {token}")

    assert offenders == []
