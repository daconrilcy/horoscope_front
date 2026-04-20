from __future__ import annotations

import ast
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
        root / "app" / "llm_orchestration" / "gateway.py",
        root / "app" / "api" / "v1" / "routers" / "admin_llm.py",
        root / "app" / "prediction" / "llm_narrator.py",
        root / "app" / "prompts" / "common_context.py",
        root / "app" / "llm_orchestration" / "admin_models.py",
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
