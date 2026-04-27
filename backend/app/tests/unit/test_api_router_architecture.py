"""Garde-fous d'architecture pour le classement des routeurs API v1."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
from typing import NamedTuple

import pytest
from fastapi.routing import APIRoute

ROUTERS_ROOT = Path(__file__).resolve().parents[2] / "api" / "v1" / "routers"
API_V1_ROOT = ROUTERS_ROOT.parent
API_DEPENDENCIES_ROOT = API_V1_ROOT.parent / "dependencies"
SCHEMAS_ROOT = API_V1_ROOT / "schemas"
SERVICE_CONTRACTS_ROOT = API_V1_ROOT.parents[1] / "services" / "api_contracts"
STORY_EVIDENCE_ROOT = (
    Path(__file__).resolve().parents[4]
    / "_condamad"
    / "stories"
    / "harden-api-adapter-boundary-guards"
)
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
ALLOWED_ROUTER_CLASS_DEFINITIONS: dict[Path, set[str]] = {
    Path("registry.py"): {"RouterRegistration"}
}
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
ADMIN_LLM_OBSERVABILITY_ROUTE_OWNER = "app.api.v1.routers.admin.llm.observability"
ADMIN_LLM_OBSERVABILITY_ROUTE_KEYS = {
    ("/v1/admin/llm/call-logs", "GET"),
    ("/v1/admin/llm/dashboard", "GET"),
    ("/v1/admin/llm/replay", "POST"),
    ("/v1/admin/llm/call-logs/purge", "POST"),
}
ADMIN_LLM_OBSERVABILITY_FORBIDDEN_PROMPTS_DECORATORS = {
    ("get", "/call-logs"),
    ("get", "/dashboard"),
    ("post", "/replay"),
    ("post", "/call-logs/purge"),
}
ADMIN_LLM_OBSERVABILITY_FORBIDDEN_TOKENS = (
    "select(",
    "db.query",
    "Session",
    "LlmCallLogModel",
)


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

ALLOWED_ROUTER_IMPORTS: dict[Path, dict[str, object]] = {}
FORBIDDEN_SQL_IMPORT_ROOTS = (
    "sqlalchemy",
    "app.infra.db.models",
    "app.infra.db.session",
)
FORBIDDEN_SESSION_METHODS = {
    "add",
    "commit",
    "delete",
    "execute",
    "flush",
    "get",
    "query",
    "refresh",
    "rollback",
    "scalar",
    "scalars",
}


class SqlBoundaryEntry(NamedTuple):
    """Identifie exactement une dette SQL encore toleree dans la couche API."""

    file: str
    line: int
    kind: str
    symbol: str
    function: str


def _python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs du package de routeurs."""
    return sorted(path for path in ROUTERS_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _api_v1_python_files() -> list[Path]:
    """Retourne les fichiers Python applicatifs du package API v1."""
    return sorted(path for path in API_V1_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _api_sql_boundary_python_files() -> list[Path]:
    """Retourne les fichiers de frontière API soumis a la garde SQL."""
    roots = [ROUTERS_ROOT, API_DEPENDENCIES_ROOT]
    return sorted(
        path
        for root in roots
        if root.exists()
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _schemas_python_files() -> list[Path]:
    """Retourne les fichiers Python des contrats Pydantic API v1."""
    return sorted(path for path in SCHEMAS_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def _service_contract_python_files() -> list[Path]:
    """Retourne les fichiers Python des contrats partagés hors API."""
    return sorted(
        path for path in SERVICE_CONTRACTS_ROOT.rglob("*.py") if "__pycache__" not in path.parts
    )


def _source_tree(path: Path) -> ast.Module:
    """Parse un fichier routeur pour inspecter ses imports sans l'executer."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _parent_map(tree: ast.Module) -> dict[ast.AST, ast.AST]:
    """Construit les liens parents pour retrouver la fonction proprietaire."""
    return {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def _containing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    """Retourne la fonction englobante d'un noeud AST ou le module."""
    parent = parents.get(node)
    while parent is not None:
        if isinstance(parent, ast.FunctionDef | ast.AsyncFunctionDef):
            return parent.name
        parent = parents.get(parent)
    return "<module>"


def _is_get_db_session_dependency(node: ast.Call) -> bool:
    """Indique si un appel FastAPI `Depends` cible explicitement la session DB."""
    dependency = node.args[0] if node.args else None
    keyword_dependency = next(
        (keyword.value for keyword in node.keywords if keyword.arg == "dependency"),
        None,
    )
    return any(
        isinstance(candidate, ast.Name) and candidate.id == "get_db_session"
        for candidate in (dependency, keyword_dependency)
    )


def _collect_sql_boundary_entries() -> set[SqlBoundaryEntry]:
    """Detecte les imports et appels SQL interdits sauf allowlist exacte."""
    entries: set[SqlBoundaryEntry] = set()
    for path in _api_sql_boundary_python_files():
        tree = _source_tree(path)
        parents = _parent_map(tree)
        relative_file = path.relative_to(API_V1_ROOT.parents[2]).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(FORBIDDEN_SQL_IMPORT_ROOTS):
                        entries.add(
                            SqlBoundaryEntry(
                                relative_file,
                                node.lineno,
                                "import",
                                alias.name,
                                _containing_function(node, parents),
                            )
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith(FORBIDDEN_SQL_IMPORT_ROOTS):
                    imported_names = ",".join(alias.name for alias in node.names)
                    entries.add(
                        SqlBoundaryEntry(
                            relative_file,
                            node.lineno,
                            "import_from",
                            f"{node.module}:{imported_names}",
                            _containing_function(node, parents),
                        )
                    )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                receiver = node.func.value
                receiver_name = receiver.id if isinstance(receiver, ast.Name) else ""
                if (
                    receiver_name in {"db", "session"}
                    and node.func.attr in FORBIDDEN_SESSION_METHODS
                ):
                    entries.add(
                        SqlBoundaryEntry(
                            relative_file,
                            node.lineno,
                            "session_call",
                            f"{receiver_name}.{node.func.attr}",
                            _containing_function(node, parents),
                        )
                    )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id != "Depends":
                    continue
                if _is_get_db_session_dependency(node):
                    entries.add(
                        SqlBoundaryEntry(
                            relative_file,
                            node.lineno,
                            "dependency",
                            "Depends(get_db_session)",
                            _containing_function(node, parents),
                        )
                    )
    return entries


def _load_sql_allowlist() -> dict[SqlBoundaryEntry, tuple[str, str]]:
    """Charge l'allowlist SQL persistante et valide ses metadonnees obligatoires."""
    allowlist_path = STORY_EVIDENCE_ROOT / "router-sql-allowlist.md"
    rows = [
        line
        for line in allowlist_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("| `")
    ]
    allowlist: dict[SqlBoundaryEntry, tuple[str, str]] = {}
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 7:
            raise AssertionError(f"invalid SQL allowlist row shape: {row}")
        file_cell, line_cell, kind_cell, symbol_cell, function_cell, reason, decision = cells
        file_value = file_cell.strip("`")
        if "*" in file_value or file_value.endswith("/"):
            raise AssertionError(f"wildcard SQL allowlist row forbidden: {row}")
        entry = SqlBoundaryEntry(
            file=file_value,
            line=int(line_cell),
            kind=kind_cell.strip("`"),
            symbol=symbol_cell.strip("`"),
            function=function_cell.strip("`"),
        )
        allowlist[entry] = (reason, decision)
    return allowlist


def _router_decorator_path(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, str] | None:
    """Retourne la méthode et le chemin d'un décorateur `router` simple."""
    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        function = decorator.func
        if not (
            isinstance(function, ast.Attribute)
            and function.attr in {"get", "post", "patch", "delete", "put"}
            and isinstance(function.value, ast.Name)
            and function.value.id == "router"
        ):
            continue
        if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
            continue
        if isinstance(decorator.args[0].value, str):
            return function.attr, decorator.args[0].value
    return None


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


def test_admin_llm_observability_routes_are_registered_once_from_canonical_router() -> None:
    """Les endpoints observability doivent être servis par le routeur canonique unique."""
    from app.main import app

    matches: list[tuple[str, str, str]] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods or set():
            if (route.path, method) in ADMIN_LLM_OBSERVABILITY_ROUTE_KEYS:
                matches.append((route.path, method, route.endpoint.__module__))

    assert sorted((path, method) for path, method, _owner in matches) == sorted(
        ADMIN_LLM_OBSERVABILITY_ROUTE_KEYS
    )
    assert {owner for _path, _method, owner in matches} == {ADMIN_LLM_OBSERVABILITY_ROUTE_OWNER}


def test_admin_llm_prompts_does_not_redefine_observability_routes() -> None:
    """La façade prompts ne doit pas redevenir propriétaire des routes observability."""
    tree = _source_tree(ROUTERS_ROOT / "admin" / "llm" / "prompts.py")
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        decorator = _router_decorator_path(node)
        if decorator in ADMIN_LLM_OBSERVABILITY_FORBIDDEN_PROMPTS_DECORATORS:
            method, path = decorator
            offenders.append(f"{node.name} defines @{method}({path})")

    assert offenders == []


def test_admin_llm_observability_router_stays_service_delegating_adapter() -> None:
    """Le routeur observability ne doit pas réintroduire SQL ni importer prompts.py."""
    path = ROUTERS_ROOT / "admin" / "llm" / "observability.py"
    content = path.read_text(encoding="utf-8")
    forbidden_content = [
        token for token in ADMIN_LLM_OBSERVABILITY_FORBIDDEN_TOKENS if token in content
    ]
    tree = _source_tree(path)
    forbidden_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "app.api.v1.routers.admin.llm.prompts":
                forbidden_imports.append(f"{node.lineno} imports {node.module}")
            if node.module.startswith("sqlalchemy"):
                forbidden_imports.append(f"{node.lineno} imports {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("sqlalchemy"):
                    forbidden_imports.append(f"{node.lineno} imports {alias.name}")

    assert forbidden_content == []
    assert forbidden_imports == []


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
        Path("routers") / "registry.py",
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


def test_api_v1_router_registry_is_main_registration_source() -> None:
    """Le montage API v1 doit passer par le registre canonique."""
    main_path = API_V1_ROOT.parents[1] / "main.py"
    tree = _source_tree(main_path)
    router_import_offenders: list[str] = []
    registry_call_found = False
    exception_call_found = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            allowed_main_router_modules = {
                "app.api.v1.routers.registry",
            }
            if (
                node.module.startswith("app.api.v1.routers.")
                and node.module not in allowed_main_router_modules
            ):
                router_import_offenders.append(f"{node.lineno} imports {node.module}")
        if isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name) and function.id == "include_api_v1_routers":
                registry_call_found = True
            if (
                isinstance(function, ast.Name)
                and function.id == "include_registered_route_exceptions"
            ):
                exception_call_found = True

    assert router_import_offenders == []
    assert registry_call_found
    assert exception_call_found


def test_route_mount_exceptions_are_structured_and_exact() -> None:
    """Les montages hors registre doivent etre portes par le registre structure."""
    from app.api.route_exceptions import API_ROUTE_MOUNT_EXCEPTIONS

    by_key = {exception.key: exception for exception in API_ROUTE_MOUNT_EXCEPTIONS}
    assert set(by_key) == {
        "health",
        "public_email_unsubscribe",
        "internal_llm_qa_seed_user",
        "internal_llm_qa_guidance",
        "internal_llm_qa_chat",
        "internal_llm_qa_natal",
        "internal_llm_qa_horoscope_daily",
    }

    for exception in API_ROUTE_MOUNT_EXCEPTIONS:
        assert exception.route_path.startswith("/")
        assert exception.methods
        assert exception.router_module
        assert exception.endpoint_module
        assert exception.reason
        assert exception.decision
        assert exception.condition


def test_runtime_routes_match_structured_exception_register() -> None:
    """La table runtime ne doit contenir que des exceptions exactes hors registre."""
    from app.api.route_exceptions import API_ROUTE_MOUNT_EXCEPTIONS
    from app.main import app

    exceptions_by_route = {
        (exception.route_path, method): exception
        for exception in API_ROUTE_MOUNT_EXCEPTIONS
        for method in exception.methods
    }
    offenders: list[str] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        path = route.path
        endpoint_module = getattr(route.endpoint, "__module__", "")
        should_match_exception = (
            endpoint_module.startswith("app.api.v1.")
            and not path.startswith("/v1/")
            or endpoint_module == "app.api.v1.routers.internal.llm.qa"
        )
        if should_match_exception:
            for method in route.methods or set():
                if method in {"HEAD", "OPTIONS"}:
                    continue
                exception = exceptions_by_route.get((path, method))
                if exception is None:
                    offenders.append(f"{method} {path} from {endpoint_module} is not registered")
                elif endpoint_module != exception.endpoint_module:
                    offenders.append(
                        f"{method} {path} owner {endpoint_module} != {exception.endpoint_module}"
                    )

    assert offenders == []


def test_registered_qa_route_exceptions_match_router_routes() -> None:
    """Le routeur QA conditionnel doit avoir une exception par route concrete."""
    from app.api.route_exceptions import API_ROUTE_MOUNT_EXCEPTIONS
    from app.api.v1.routers.internal.llm.qa import router as qa_router

    qa_exceptions = {
        (exception.route_path, method)
        for exception in API_ROUTE_MOUNT_EXCEPTIONS
        if exception.endpoint_module == "app.api.v1.routers.internal.llm.qa"
        for method in exception.methods
    }
    qa_routes = {
        (route.path, method)
        for route in qa_router.routes
        if isinstance(route, APIRoute)
        for method in route.methods or set()
        if method not in {"HEAD", "OPTIONS"}
    }

    assert qa_exceptions == qa_routes


def test_api_contracts_do_not_import_fastapi_or_api_layer() -> None:
    """Les contrats partagés ne doivent pas dépendre de FastAPI ni de `app.api`."""
    offenders: list[str] = []
    for path in _service_contract_python_files():
        relative_path = path.relative_to(SERVICE_CONTRACTS_ROOT)
        tree = _source_tree(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "fastapi" or alias.name.startswith("fastapi."):
                        offenders.append(f"{relative_path}:{node.lineno} imports {alias.name}")
                    if alias.name == "app.api" or alias.name.startswith("app.api."):
                        offenders.append(f"{relative_path}:{node.lineno} imports {alias.name}")
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "fastapi" or node.module.startswith("fastapi."):
                    offenders.append(f"{relative_path}:{node.lineno} imports {node.module}")
                if node.module == "app.api" or node.module.startswith("app.api."):
                    offenders.append(f"{relative_path}:{node.lineno} imports {node.module}")
            if isinstance(node, ast.Assign):
                assigns_router = any(
                    isinstance(target, ast.Name) and target.id == "router"
                    for target in node.targets
                )
                if assigns_router:
                    offenders.append(f"{relative_path}:{node.lineno} defines router")

    assert offenders == []


def test_non_api_layers_do_not_import_api_package() -> None:
    """Les couches non-API ne doivent plus dépendre de l'adaptateur HTTP."""
    backend_app = API_V1_ROOT.parents[1]
    roots = ["services", "domain", "infra", "core"]
    offenders: list[str] = []
    for root_name in roots:
        for path in sorted((backend_app / root_name).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative_path = path.relative_to(backend_app)
            tree = _source_tree(path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "app.api" or alias.name.startswith("app.api."):
                            offenders.append(f"{relative_path}:{node.lineno} imports {alias.name}")
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module == "app.api" or node.module.startswith("app.api."):
                        offenders.append(f"{relative_path}:{node.lineno} imports {node.module}")

    assert offenders == []


def test_legacy_http_error_surfaces_are_removed() -> None:
    """Les helpers d'erreur HTTP legacy ne doivent plus être actifs."""
    backend_app = API_V1_ROOT.parents[1]
    forbidden_tokens = ("raise_http_error", "legacy_detail", 'content["detail"]')
    offenders: list[str] = []
    for path in sorted((backend_app / "api").rglob("*.py")) + sorted(
        (backend_app / "tests").rglob("*.py")
    ):
        if "__pycache__" in path.parts or path == Path(__file__):
            continue
        content = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in content:
                offenders.append(f"{path.relative_to(backend_app)} contains {token}")

    assert offenders == []


def test_non_v1_routes_under_api_v1_are_explicit_exceptions() -> None:
    """Toute route hors /v1 sous api/v1 doit être une exception exacte et justifiée."""
    from app.api.route_exceptions import API_ROUTE_MOUNT_EXCEPTIONS
    from app.main import app

    exceptions_by_path = {
        exception.route_path: exception for exception in API_ROUTE_MOUNT_EXCEPTIONS
    }
    offenders: list[str] = []
    for route in app.routes:
        path = getattr(route, "path", "")
        endpoint_module = getattr(getattr(route, "endpoint", None), "__module__", "")
        if not endpoint_module.startswith("app.api.v1."):
            continue
        if path.startswith("/v1/"):
            continue
        exception = exceptions_by_path.get(path)
        if exception is None:
            offenders.append(f"{path} from {endpoint_module} is not allowlisted")
        elif exception.endpoint_module != endpoint_module:
            offenders.append(
                f"{path} from {endpoint_module} mismatches {exception.endpoint_module}"
            )

    assert offenders == []


def test_api_sql_boundary_debt_matches_exact_allowlist() -> None:
    """Toute dette SQL API restante doit etre inventoriee avec metadonnees exactes."""
    detected = _collect_sql_boundary_entries()
    allowlist = _load_sql_allowlist()
    missing = sorted(detected - set(allowlist), key=lambda item: tuple(item))
    stale = sorted(set(allowlist) - detected, key=lambda item: tuple(item))
    incomplete_metadata = [
        entry for entry, (reason, decision) in allowlist.items() if not reason or not decision
    ]

    assert missing == []
    assert stale == []
    assert incomplete_metadata == []


def test_admin_content_text_update_flow_delegates_persistence_to_service() -> None:
    """Le flux extrait ne doit plus porter d'operations SQL dans le routeur."""
    tree = _source_tree(ROUTERS_ROOT / "admin" / "content.py")
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "update_content_text"
    )
    calls = {
        child.func.attr
        for child in ast.walk(function)
        if isinstance(child, ast.Call)
        and isinstance(child.func, ast.Attribute)
        and isinstance(child.func.value, ast.Name)
        and child.func.value.id == "db"
    }
    service_calls = {
        child.func.id
        for child in ast.walk(function)
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
    }

    assert calls == set()
    assert "update_config_text_value" in service_calls


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
