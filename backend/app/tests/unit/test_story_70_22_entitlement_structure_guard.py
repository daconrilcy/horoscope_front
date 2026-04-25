"""Garde-fous structurels pour la story 70.22 sur le namespace entitlement."""

from pathlib import Path

ROOT_ALLOWLIST = {
    "quota_usage_service.py",
    "quota_window_resolver.py",
}

ENTITLEMENT_NAMESPACE_ALLOWLIST = {
    "__init__.py",
    "b2c_runtime_gate.py",
    "chat_entitlement_gate.py",
    "entitlement_types.py",
    "effective_entitlement_gate_helpers.py",
    "effective_entitlement_resolver_service.py",
    "feature_scope_registry.py",
    "horoscope_daily_entitlement_gate.py",
    "natal_chart_long_entitlement_gate.py",
    "thematic_consultation_entitlement_gate.py",
}

CANONICAL_ENTITLEMENT_ALLOWLIST = {
    "__init__.py",
    "alert/__init__.py",
    "alert/batch_handling.py",
    "alert/batch_retry.py",
    "alert/handling.py",
    "alert/query.py",
    "alert/retry.py",
    "alert/service.py",
    "audit/__init__.py",
    "audit/audit_query.py",
    "audit/audit_review.py",
    "audit/diff_service.py",
    "audit/mutation_service.py",
    "audit/review_queue.py",
    "shared/__init__.py",
    "shared/alert_delivery_runtime.py",
    "shared/db_consistency_validator.py",
    "suppression/__init__.py",
    "suppression/application.py",
    "suppression/rule.py",
}

LEGACY_SERVICE_FILES = {
    "entitlement_service.py",
    "quota_service.py",
    "canonical_entitlement_alert_batch_handling_service.py",
    "canonical_entitlement_alert_batch_retry_service.py",
    "canonical_entitlement_alert_handling_service.py",
    "canonical_entitlement_alert_query_service.py",
    "canonical_entitlement_alert_retry_service.py",
    "canonical_entitlement_alert_service.py",
    "canonical_entitlement_alert_suppression_application_service.py",
    "canonical_entitlement_alert_suppression_rule_service.py",
    "canonical_entitlement_db_consistency_validator.py",
    "canonical_entitlement_mutation_audit_query_service.py",
    "canonical_entitlement_mutation_audit_review_service.py",
    "canonical_entitlement_mutation_diff_service.py",
    "canonical_entitlement_mutation_service.py",
    "canonical_entitlement_review_queue_service.py",
    "chat_entitlement_gate.py",
    "effective_entitlement_gate_helpers.py",
    "effective_entitlement_resolver_service.py",
    "entitlement_types.py",
    "feature_scope_registry.py",
    "horoscope_daily_entitlement_gate.py",
    "natal_chart_long_entitlement_gate.py",
    "thematic_consultation_entitlement_gate.py",
}

FORBIDDEN_IMPORT_SNIPPETS = {
    "from app.services.entitlement_service import",
    "import app.services.entitlement_service",
    "from app.services.quota_service import",
    "import app.services.quota_service",
    "from app.services.chat_entitlement_gate import",
    "import app.services.chat_entitlement_gate",
    "from app.services.effective_entitlement_gate_helpers import",
    "import app.services.effective_entitlement_gate_helpers",
    "from app.services.effective_entitlement_resolver_service import",
    "import app.services.effective_entitlement_resolver_service",
    "from app.services.entitlement_types import",
    "import app.services.entitlement_types",
    "from app.services.feature_scope_registry import",
    "import app.services.feature_scope_registry",
    "from app.services.horoscope_daily_entitlement_gate import",
    "import app.services.horoscope_daily_entitlement_gate",
    "from app.services.natal_chart_long_entitlement_gate import",
    "import app.services.natal_chart_long_entitlement_gate",
    "from app.services.thematic_consultation_entitlement_gate import",
    "import app.services.thematic_consultation_entitlement_gate",
    "app.services.canonical_entitlement_alert_batch_handling_service",
    "app.services.canonical_entitlement_alert_batch_retry_service",
    "app.services.canonical_entitlement_alert_handling_service",
    "app.services.canonical_entitlement_alert_query_service",
    "app.services.canonical_entitlement_alert_retry_service",
    "app.services.canonical_entitlement_alert_service",
    "app.services.canonical_entitlement_alert_suppression_application_service",
    "app.services.canonical_entitlement_alert_suppression_rule_service",
    "app.services.canonical_entitlement_db_consistency_validator",
    "app.services.canonical_entitlement_mutation_audit_query_service",
    "app.services.canonical_entitlement_mutation_audit_review_service",
    "app.services.canonical_entitlement_mutation_diff_service",
    "app.services.canonical_entitlement_mutation_service",
    "app.services.canonical_entitlement_review_queue_service",
}


def test_entitlement_root_allowlist_matches_canonical_cartography() -> None:
    """La racine services ne doit plus porter les gates runtime de 70.22."""
    services_root = Path(__file__).resolve().parents[2] / "services"
    current_files = {
        path.name
        for path in services_root.iterdir()
        if path.is_file() and ("entitlement" in path.name or path.name.startswith("quota_"))
    }

    assert current_files == ROOT_ALLOWLIST


def test_entitlement_namespace_matches_allowlist() -> None:
    """Le namespace entitlement doit porter exactement les modules migres."""
    namespace_root = Path(__file__).resolve().parents[2] / "services" / "entitlement"
    current_files = {
        path.relative_to(namespace_root).as_posix()
        for path in namespace_root.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    assert current_files == ENTITLEMENT_NAMESPACE_ALLOWLIST


def test_canonical_entitlement_subtree_matches_allowlist() -> None:
    """Le sous-domaine canonical entitlement doit rester fermé et nominatif."""
    canonical_root = Path(__file__).resolve().parents[2] / "services" / "canonical_entitlement"
    current_files = {
        path.relative_to(canonical_root).as_posix()
        for path in canonical_root.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    assert current_files == CANONICAL_ENTITLEMENT_ALLOWLIST


def test_legacy_entitlement_service_files_are_absent() -> None:
    """Les anciens chemins plats entitlement ne doivent pas réapparaître."""
    services_root = Path(__file__).resolve().parents[2] / "services"
    assert all(not (services_root / file_name).exists() for file_name in LEGACY_SERVICE_FILES)


def test_no_legacy_entitlement_import_path_is_reintroduced() -> None:
    """Les imports production et tests doivent utiliser les chemins entitlement canoniques."""
    project_root = Path(__file__).resolve().parents[2]
    search_roots = [project_root, project_root.parent / "tests"]

    for root in search_roots:
        for file_path in root.rglob("*.py"):
            if "__pycache__" in file_path.parts:
                continue
            if file_path.name == "test_story_70_22_entitlement_structure_guard.py":
                continue
            content = file_path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_IMPORT_SNIPPETS:
                assert forbidden not in content, f"{forbidden} found in {file_path}"


def test_services_init_does_not_reexport_entitlement_legacy_paths() -> None:
    """Le package services ne doit pas rejouer des alias ou re-exports legacy entitlement."""
    services_init = Path(__file__).resolve().parents[2] / "services" / "__init__.py"
    content = services_init.read_text(encoding="utf-8")

    assert "entitlement_service" not in content
    assert "quota_service" not in content
    assert "canonical_entitlement_" not in content
    assert "chat_entitlement_gate" not in content
    assert "effective_entitlement_resolver_service" not in content
    assert "entitlement_types" not in content
    assert "feature_scope_registry" not in content
