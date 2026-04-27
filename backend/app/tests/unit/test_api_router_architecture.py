"""Garde-fous d'architecture pour le classement des routeurs API v1."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
from typing import NamedTuple

import pytest

ROUTERS_ROOT = Path(__file__).resolve().parents[2] / "api" / "v1" / "routers"
API_V1_ROOT = ROUTERS_ROOT.parent
SCHEMAS_ROOT = API_V1_ROOT / "schemas"
CANONICAL_DOMAINS = {"admin", "b2b", "internal", "ops", "public"}
CANONICAL_SCHEMA_ROOTS = {"common.py", "routers"}
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
    "app.api.v1.routers.admin.llm.error_codes",
)
FORBIDDEN_ROUTER_PREFIXES = ("/v1/" + "ai",)
FORBIDDEN_LEGACY_STRINGS = (
    "ai_engine" + "_router",
    "use_case" + "_compat",
    "legacy" + "_maintenance",
    "legacy" + "_alias",
    "legacy_registry" + "_only",
)
ALLOWED_ROUTER_CLASS_DEFINITIONS: dict[Path, set[str]] = {}
SHARED_CONSTANT_NAMES = {
    "ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER",
    "ADMIN_MANUAL_EXECUTE_ROUTE_PATH",
    "ADMIN_MANUAL_LLM_EXECUTE_SURFACE",
    "BLOCKED_CATEGORIES",
    "CHAT_TEMPORARY_UNAVAILABLE_MESSAGE",
    "CALIBRATION_RULE_DESCRIPTIONS",
    "CONSULTATION_TYPE_ALIASES",
    "DEFAULT_DRILLDOWN_LIMIT",
    "DEFAULT_CONFIG_TEXTS",
    "DEFAULT_EDITORIAL_TEMPLATES",
    "FEATURES_TO_QUERY",
    "LEGACY_USE_CASE_KEYS_REMOVED",
    "LOCALE_PATTERN",
    "MAX_PAGE_SIZE",
    "PDF_TEMPLATE_CONFIG_DOC",
    "VALID_ASTROLOGER_PROFILES",
    "VALID_RESOLUTION_SOURCES",
    "VALID_VIEWS",
}
TARGET_RESPONSIBILITY_LIMITS = {
    Path("..") / ".." / "services" / "llm_generation" / "admin_prompts.py": 52_000,
    Path("routers") / "ops" / "entitlement_mutation_audits.py": 50_000,
}
REMOVED_ROUTE_SUPPORT_PACKAGE = "router" + "_logic"


class ExpectedRouterRoot(NamedTuple):
    """Décrit un routeur déplacé et sa racine HTTP canonique."""

    old_module: str
    canonical_module: str
    effective_root: str


EXPECTED_ROUTER_ROOTS = (
    ExpectedRouterRoot(
        old_module="app.api.v1.routers.b2b.reconciliation",
        canonical_module="app.api.v1.routers.ops.b2b.reconciliation",
        effective_root="/v1/ops/b2b/reconciliation",
    ),
    ExpectedRouterRoot(
        old_module="app.api.v1.routers.b2b.entitlement_repair",
        canonical_module="app.api.v1.routers.ops.b2b.entitlement_repair",
        effective_root="/v1/ops/b2b/entitlements/repair",
    ),
    ExpectedRouterRoot(
        old_module="app.api.v1.routers.b2b.entitlements_audit",
        canonical_module="app.api.v1.routers.ops.b2b.entitlements_audit",
        effective_root="/v1/ops/b2b/entitlements",
    ),
    ExpectedRouterRoot(
        old_module="app.api.v1.routers.public.enterprise_credentials",
        canonical_module="app.api.v1.routers.b2b.credentials",
        effective_root="/v1/b2b/credentials",
    ),
)

NON_V1_ROUTE_EXCEPTIONS = {
    "/health": {
        "file": "backend/app/api/health.py",
        "reason": "Route de santé applicative hors API v1.",
        "expiry": "Exception permanente de bootstrap.",
    },
    "/api/email/unsubscribe": {
        "file": "backend/app/api/v1/routers/public/email.py",
        "reason": "URL publique historique active de désabonnement email.",
        "expiry": "Supprimer seulement via story de migration d'URL dédiée.",
    },
}
ALLOWED_ROUTER_IMPORTS: dict[Path, dict[str, object]] = {}


def _python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs du package de routeurs."""
    return sorted(path for path in ROUTERS_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _api_v1_python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs du package API v1."""
    return sorted(path for path in API_V1_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _schemas_python_files() -> list[Path]:
    """Retourne les fichiers Python des contrats Pydantic API v1."""
    return sorted(path for path in SCHEMAS_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


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
    """La logique non HTTP doit rester hors des routeurs."""
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


@pytest.mark.parametrize("expected", EXPECTED_ROUTER_ROOTS)
def test_moved_router_old_modules_are_not_importable(expected: ExpectedRouterRoot) -> None:
    """Les anciens chemins Python de routeurs déplacés ne doivent pas rester actifs."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(expected.old_module)


@pytest.mark.parametrize("expected", EXPECTED_ROUTER_ROOTS)
def test_moved_router_canonical_modules_are_registered(expected: ExpectedRouterRoot) -> None:
    """Les routes OpenAPI déplacées doivent être servies par leur module canonique."""
    from app.main import app

    openapi_paths = set(app.openapi()["paths"])
    matching_paths = [
        path
        for path in openapi_paths
        if path == expected.effective_root or path.startswith(f"{expected.effective_root}/")
    ]
    assert matching_paths, f"missing OpenAPI path under {expected.effective_root}"

    offenders: list[str] = []
    for route in app.routes:
        route_path = getattr(route, "path", "")
        if not (
            route_path == expected.effective_root
            or route_path.startswith(f"{expected.effective_root}/")
        ):
            continue
        more_specific_root = any(
            other.effective_root != expected.effective_root
            and other.effective_root.startswith(f"{expected.effective_root}/")
            and (
                route_path == other.effective_root
                or route_path.startswith(f"{other.effective_root}/")
            )
            for other in EXPECTED_ROUTER_ROOTS
        )
        if more_specific_root:
            continue
        endpoint_module = getattr(getattr(route, "endpoint", None), "__module__", "")
        if endpoint_module != expected.canonical_module:
            offenders.append(f"{route_path} registered by {endpoint_module}")

    assert offenders == []


def test_router_root_audit_lists_every_registered_api_v1_router_module() -> None:
    """L'audit de racine HTTP doit couvrir tous les routeurs API v1 actifs."""
    from app.main import app

    repo_root = Path(__file__).resolve().parents[4]
    audit_path = (
        repo_root
        / "_condamad"
        / "stories"
        / "converge-api-v1-route-architecture"
        / "router-root-audit.md"
    )
    audit_content = audit_path.read_text(encoding="utf-8")
    registered_modules = {
        getattr(getattr(route, "endpoint", None), "__module__", "")
        for route in app.routes
        if getattr(getattr(route, "endpoint", None), "__module__", "").startswith(
            "app.api.v1.routers"
        )
    }
    missing = [
        module for module in sorted(registered_modules) if f"| `{module}` |" not in audit_content
    ]

    assert missing == []


def test_removed_route_support_namespace_directory_is_absent() -> None:
    """L'ancien namespace de support des routeurs API v1 ne doit plus exister."""
    assert not (API_V1_ROOT / REMOVED_ROUTE_SUPPORT_PACKAGE).exists()


def test_removed_route_support_namespace_is_not_importable() -> None:
    """L'ancien namespace de support ne doit pas rester importable via un shim."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(f"app.api.v1.{REMOVED_ROUTE_SUPPORT_PACKAGE}")


def test_backend_code_does_not_reference_removed_route_support_namespace() -> None:
    """Aucun code backend ne doit cibler l'ancien chemin Python de support."""
    forbidden = f"app.api.v1.{REMOVED_ROUTE_SUPPORT_PACKAGE}"
    backend_root = Path(__file__).resolve().parents[3]
    offenders: list[str] = []
    for directory_name in ("app", "tests"):
        for path in sorted((backend_root / directory_name).rglob("*.py")):
            if "__pycache__" in path.parts or path == Path(__file__):
                continue
            content = path.read_text(encoding="utf-8")
            if forbidden in content:
                offenders.append(str(path.relative_to(backend_root)))

    assert offenders == []


def test_api_v1_support_handler_namespace_is_absent() -> None:
    """La couche API v1 ne doit pas contenir de namespace de support hors routeurs."""
    assert not (API_V1_ROOT / "handlers").exists()


def test_service_modules_do_not_import_fastapi_or_wildcards() -> None:
    """Les services ne doivent pas dépendre des adaptateurs HTTP FastAPI."""
    service_roots = [API_V1_ROOT.parents[1] / "services"]
    offenders: list[str] = []
    for root in service_roots:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative_path = path.relative_to(API_V1_ROOT.parents[1])
            tree = _source_tree(path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if any(alias.name == "*" for alias in node.names):
                        offenders.append(f"{relative_path}:{node.lineno} wildcard import")
                    if node.module and (
                        node.module == "fastapi" or node.module.startswith("fastapi.")
                    ):
                        imported = ", ".join(alias.name for alias in node.names)
                        offenders.append(
                            f"{relative_path}:{node.lineno} imports {imported} from {node.module}"
                        )
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "fastapi" or alias.name.startswith("fastapi."):
                            offenders.append(f"{relative_path}:{node.lineno} imports {alias.name}")
                if isinstance(node, ast.Assign):
                    assigns_router = any(
                        isinstance(target, ast.Name) and target.id == "router"
                        for target in node.targets
                    )
                    if assigns_router and isinstance(node.value, ast.Call):
                        function = node.value.func
                        if isinstance(function, ast.Name) and function.id == "APIRouter":
                            offenders.append(f"{relative_path}:{node.lineno} defines APIRouter")

    assert offenders == []


def test_api_v1_non_registry_modules_do_not_import_routers() -> None:
    """Les schémas, helpers et routeurs ne doivent pas dépendre d'autres routeurs."""
    allowed_files = {
        Path("__init__.py"),
        Path("routers") / "__init__.py",
    }
    offenders: list[str] = []
    for path in _api_v1_python_files():
        relative_path = path.relative_to(API_V1_ROOT)
        if relative_path in allowed_files or "__init__.py" in path.name:
            continue
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.module is None:
                continue
            if node.module.startswith("app.api.v1.routers."):
                allowed_modules = ALLOWED_ROUTER_IMPORTS.get(relative_path, {})
                if node.module in allowed_modules:
                    continue
                offenders.append(f"{relative_path}:{node.lineno} imports {node.module}")

    assert offenders == []


def test_non_v1_routes_under_api_v1_are_explicit_exceptions() -> None:
    """Toute route hors /v1 sous api/v1 doit être une exception exacte et justifiée."""
    from app.main import app

    offenders: list[str] = []
    for route in app.routes:
        path = getattr(route, "path", "")
        endpoint_module = getattr(getattr(route, "endpoint", None), "__module__", "")
        if not endpoint_module.startswith("app.api.v1."):
            continue
        if path.startswith("/v1/"):
            continue
        exception = NON_V1_ROUTE_EXCEPTIONS.get(path)
        if exception is None:
            offenders.append(f"{path} from {endpoint_module} is not allowlisted")

    assert offenders == []


def test_api_error_contract_is_centralized() -> None:
    """Les enveloppes d'erreur API v1 doivent vivre dans le contrat commun."""
    offenders: list[str] = []
    for path in _schemas_python_files():
        if path == SCHEMAS_ROOT / "common.py":
            continue
        relative_path = path.relative_to(SCHEMAS_ROOT)
        tree = _source_tree(path)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in {"ErrorPayload", "ErrorEnvelope"}:
                offenders.append(f"{relative_path}:{node.lineno} defines {node.name}")

    assert offenders == []


def test_router_error_helpers_do_not_recreate_response_envelopes() -> None:
    """Les helpers d'erreur locaux ne doivent plus recréer l'enveloppe HTTP."""
    helper_names = {"_audit_unavailable_response", "_create_error_response", "_error_response"}
    offenders: list[str] = []
    for path in _api_v1_python_files():
        relative_path = path.relative_to(API_V1_ROOT)
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name not in helper_names:
                continue
            offenders.append(f"{relative_path}:{node.lineno} {node.name}")

    assert offenders == []


def test_shared_constants_are_not_defined_in_route_schema_or_logic_modules() -> None:
    """Les constantes partagées doivent vivre dans `app.api.v1.constants`."""
    offenders: list[str] = []
    for path in _api_v1_python_files():
        if path == API_V1_ROOT / "constants.py":
            continue
        relative_path = path.relative_to(API_V1_ROOT)
        tree = _source_tree(path)
        for node in tree.body:
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in SHARED_CONSTANT_NAMES:
                    offenders.append(f"{relative_path}:{node.lineno} defines {target.id}")

    assert offenders == []


def test_api_v1_schema_files_are_under_canonical_roots() -> None:
    """Les schemas API v1 doivent être rangés par sous-dossier canonique."""
    offenders: list[str] = []
    for path in _schemas_python_files():
        if path.name == "__init__.py":
            continue
        relative_path = path.relative_to(SCHEMAS_ROOT)
        first_part = relative_path.parts[0]
        if first_part not in CANONICAL_SCHEMA_ROOTS:
            offenders.append(str(relative_path))
            continue
        if first_part == "routers" and len(relative_path.parts) > 1:
            domain = relative_path.parts[1]
            if domain not in CANONICAL_DOMAINS:
                offenders.append(str(relative_path))

    assert offenders == []


def test_legacy_api_v1_errors_module_is_not_importable() -> None:
    """L'ancien module d'erreurs API v1 ne doit pas rester comme facade."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("app.api.v1.errors")


def test_target_api_files_stay_below_responsibility_limits() -> None:
    """Les deux fichiers cibles ne doivent pas revenir à leur taille multi-responsabilités."""
    offenders = []
    for relative_path, max_bytes in TARGET_RESPONSIBILITY_LIMITS.items():
        path = API_V1_ROOT / relative_path
        if path.stat().st_size > max_bytes:
            offenders.append(f"{relative_path} is {path.stat().st_size} bytes > {max_bytes}")

    assert offenders == []


def test_ops_entitlement_audit_list_route_delegates_business_flow() -> None:
    """Le handler de liste mutations reste une couche HTTP fine."""
    path = ROUTERS_ROOT / "ops" / "entitlement_mutation_audits.py"
    tree = _source_tree(path)
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "list_mutation_audits"
    )
    calls = {
        child.func.id
        for child in ast.walk(function)
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
    }

    assert "build_mutation_audit_list_response" in calls
    assert "select" not in calls
