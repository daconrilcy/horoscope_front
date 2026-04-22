from __future__ import annotations

import json
from pathlib import Path

from app.ops.llm.db_cleanup_validator import (
    LlmDbCleanupValidator,
    discover_llm_tables,
    scan_python_sources_for_legacy_patterns,
    validate_registry_structure,
    validate_reviewed_migrations,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_registry() -> dict:
    root = _repo_root()
    registry_path = root / "backend" / "docs" / "llm-db-cleanup-registry.json"
    return json.loads(registry_path.read_text(encoding="utf-8"))


def test_llm_db_cleanup_validator_passes_on_repository_tree() -> None:
    validator = LlmDbCleanupValidator(_repo_root())
    violations = validator.validate_all()
    assert violations == [], [violation.as_user_string() for violation in violations]


def test_registry_requires_minimum_object_coverage() -> None:
    root = _repo_root()
    registry = _load_registry()
    registry["objects"] = [
        obj for obj in registry["objects"] if obj["object_id"] != "column:llm_call_logs.use_case"
    ]

    violations = validate_registry_structure(registry, root_path=root)
    assert any(violation.code == "REGISTRY_REQUIRED_OBJECTS" for violation in violations)


def test_reviewed_migrations_guard_detects_missing_inventory_entry() -> None:
    root = _repo_root()
    registry = _load_registry()
    registry["reviewed_migrations"] = registry["reviewed_migrations"][:-1]
    known_tables = discover_llm_tables(root / "backend" / "app" / "infra" / "db" / "models")

    violations = validate_reviewed_migrations(
        registry,
        migrations_root=root / "backend" / "migrations" / "versions",
        known_tables=known_tables,
    )

    assert any(violation.code == "UNREVIEWED_LLM_MIGRATION" for violation in violations)


def test_legacy_usage_allowlist_detects_reintroduced_usage(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    app_root = repo_root / "backend" / "app" / "services"
    scripts_root = repo_root / "backend" / "scripts"
    app_root.mkdir(parents=True)
    scripts_root.mkdir(parents=True)
    (app_root / "rogue_service.py").write_text(
        "from app.infra.db.models.llm_observability import LlmCallLogModel\n"
        "VALUE = LlmCallLogModel.use_case\n",
        encoding="utf-8",
    )

    violations = scan_python_sources_for_legacy_patterns(
        root_path=repo_root,
        compatibility_rules=[
            {
                "rule_id": "legacy-call-log-use-case-read",
                "pattern": "LlmCallLogModel\\.use_case",
                "allowed_paths": ["backend/app/api/v1/routers/admin_ai.py"],
            }
        ],
    )

    assert any(violation.code == "LEGACY_ACCESS_OUTSIDE_ALLOWLIST" for violation in violations)


def test_main_no_longer_depends_on_legacy_use_case_registry() -> None:
    root = _repo_root()
    content = (root / "backend" / "app" / "main.py").read_text(encoding="utf-8")

    assert "LlmUseCaseConfigModel" not in content
    assert "seed_use_cases" not in content
