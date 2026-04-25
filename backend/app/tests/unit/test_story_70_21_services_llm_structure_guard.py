"""Garde-fous structurels pour la story 70.21 sur les services LLM."""

from __future__ import annotations

from pathlib import Path


def test_no_llm_service_module_remains_at_services_root() -> None:
    services_root = Path(__file__).resolve().parents[2] / "services"
    root_llm_modules = sorted(path.name for path in services_root.glob("llm_*_service.py"))
    assert root_llm_modules == []


def test_no_legacy_llm_service_import_path_is_reintroduced() -> None:
    project_root = Path(__file__).resolve().parents[2]
    files_to_guard = [
        project_root / "api" / "v1" / "routers" / "admin_llm_consumption.py",
        project_root / "api" / "v1" / "routers" / "admin_exports.py",
        project_root / "api" / "v1" / "routers" / "ops_monitoring_llm.py",
        project_root / "api" / "v1" / "routers" / "internal" / "llm" / "qa.py",
        project_root / "startup" / "llm_qa_seed.py",
        project_root / "services" / "__init__.py",
    ]
    forbidden_snippets = [
        "app.services.llm_canonical_consumption_service",
        "app.services.llm_ops_monitoring_service",
        "app.services.llm_qa_seed_service",
        "from app.services import llm_qa_seed_service",
        "from app.services import llm_canonical_consumption_service",
        "from app.services import llm_ops_monitoring_service",
    ]

    for file_path in files_to_guard:
        content = file_path.read_text(encoding="utf-8")
        for forbidden in forbidden_snippets:
            assert forbidden not in content, f"{forbidden} found in {file_path}"


def test_admin_routes_no_longer_call_private_consumption_helpers() -> None:
    project_root = Path(__file__).resolve().parents[2]
    files_to_guard = [
        project_root / "api" / "v1" / "routers" / "admin_llm_consumption.py",
        project_root / "api" / "v1" / "routers" / "admin_exports.py",
    ]
    forbidden_snippets = [
        "LlmCanonicalConsumptionService._normalized_calls",
        "LlmCanonicalConsumptionService._period_start_utc",
        "LlmCanonicalConsumptionService._normalize_taxonomy",
    ]

    for file_path in files_to_guard:
        content = file_path.read_text(encoding="utf-8")
        for forbidden in forbidden_snippets:
            assert forbidden not in content, f"{forbidden} found in {file_path}"
