from __future__ import annotations

import ast
import subprocess
from pathlib import Path


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_nominal_modules_do_not_import_legacy_directly() -> None:
    """
    Story 70.14 watchpoint:
    the nominal perimeter must access legacy only via app.domain.llm.legacy.bridge.
    """
    root = Path(__file__).resolve().parents[2]
    critical_nominal_files = [
        root / "app" / "domain" / "llm" / "runtime" / "gateway.py",
        root / "app" / "api" / "v1" / "routers" / "admin_llm.py",
        root / "app" / "prediction" / "llm_narrator.py",
        root / "app" / "domain" / "llm" / "prompting" / "context.py",
        root / "app" / "domain" / "llm" / "configuration" / "admin_models.py",
    ]
    forbidden_prefixes = (
        "app.llm_orchestration.legacy_prompt_runtime",
        "app.prompts.catalog",
        "app.domain.llm.legacy.runtime_legacy",
        "app.domain.llm.legacy.catalog_legacy",
        "app.domain.llm.legacy.narrator_legacy",
    )

    violations: list[str] = []
    for file_path in critical_nominal_files:
        modules = _imported_modules(file_path)
        for module_name in sorted(modules):
            if module_name.startswith(forbidden_prefixes):
                violations.append(f"{file_path.relative_to(root)} imports {module_name}")

    assert not violations, (
        "Legacy direct imports detected in nominal perimeter. "
        "Use app.domain.llm.legacy.bridge instead.\n- " + "\n- ".join(violations)
    )


def test_runtime_and_bootstrap_modules_do_not_depend_on_legacy_transition_paths() -> None:
    """
    Story 70.14 follow-up:
    canonical runtime/bootstrap entrypoints must not route back through legacy script/service
    paths for the moved LLM surface.
    """
    root = Path(__file__).resolve().parents[2]
    file_expectations = {
        root / "app" / "ops" / "llm" / "bootstrap" / "seed_29_prompts.py": {
            "scripts.seed_29_prompts",
        },
        root / "app" / "ops" / "llm" / "bootstrap" / "seed_30_8_v3_prompts.py": {
            "scripts.seed_30_8_v3_prompts",
        },
        root / "app" / "ops" / "llm" / "bootstrap" / "seed_30_14_chat_prompt.py": {
            "scripts.seed_30_14_chat_prompt",
        },
    }

    violations: list[str] = []
    for file_path, forbidden_modules in file_expectations.items():
        modules = _imported_modules(file_path)
        for module_name in sorted(modules):
            if module_name in forbidden_modules:
                violations.append(f"{file_path.relative_to(root)} imports {module_name}")

    assert not violations, (
        "Canonical runtime/bootstrap modules still depend on legacy transition paths.\n- "
        + "\n- ".join(violations)
    )


def test_admin_observability_router_exposes_only_observability_endpoints() -> None:
    from app.api.v1.routers.admin.llm.observability import router

    paths = sorted(route.path for route in router.routes)
    assert paths == [
        "/v1/admin/llm/call-logs",
        "/v1/admin/llm/call-logs/purge",
        "/v1/admin/llm/dashboard",
        "/v1/admin/llm/replay",
    ]


def test_residual_legacy_directories_are_physically_absent() -> None:
    root = Path(__file__).resolve().parents[2]
    forbidden_paths = [
        root / "app" / "prompts",
        root / "app" / "domain" / "llm" / "legacy",
        root / "app" / "ops" / "llm" / "legacy",
        root / "app" / "ops" / "llm" / "migrations",
    ]

    existing = [str(path.relative_to(root)) for path in forbidden_paths if path.exists()]
    assert not existing, (
        "Residual legacy directories must be physically removed once decommissioned.\n- "
        + "\n- ".join(existing)
    )


def test_git_tracked_files_do_not_include_pycache_or_pyc() -> None:
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    tracked = [line for line in result.stdout.splitlines() if line]
    polluted = [line for line in tracked if "__pycache__" in line or line.endswith(".pyc")]

    assert not polluted, "Tracked files must not include Python cache artifacts.\n- " + "\n- ".join(
        polluted
    )
