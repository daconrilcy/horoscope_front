"""Garde-fous structurels pour la story 70.23 sur le namespace services."""

from __future__ import annotations

from pathlib import Path

SERVICES_ROOT_ALLOWLIST = {
    "__init__.py",
    "auth_service.py",
    "chart_json_builder.py",
    "chart_result_service.py",
    "cross_tool_report.py",
    "current_context.py",
    "daily_prediction_service.py",
    "daily_prediction_types.py",
    "disclaimer_registry.py",
    "email_provider.py",
    "email_service.py",
    "feature_flag_service.py",
    "feature_registry_consistency_validator.py",
    "geocoding_service.py",
    "persona_config_service.py",
    "privacy_service.py",
    "quota_usage_service.py",
    "quota_window_resolver.py",
    "reference_data_service.py",
    "relative_scoring_service.py",
}

REMOVED_ROOT_SERVICE_FILES = {
    "astro_context_builder.py",
    "audit_service.py",
    "b2b_api_entitlement_gate.py",
    "b2b_astrology_service.py",
    "b2b_audit_service.py",
    "b2b_billing_service.py",
    "b2b_canonical_plan_resolver.py",
    "b2b_canonical_usage_service.py",
    "b2b_editorial_service.py",
    "b2b_entitlement_repair_service.py",
    "b2b_reconciliation_service.py",
    "billing_service.py",
    "consultation_catalogue_service.py",
    "consultation_fallback_service.py",
    "consultation_precheck_service.py",
    "consultation_third_party_service.py",
    "enterprise_credentials_service.py",
    "enterprise_quota_usage_service.py",
    "incident_service.py",
    "natal_calculation_service.py",
    "natal_pdf_export_service.py",
    "natal_preparation_service.py",
    "ops_monitoring_service.py",
    "prediction_compute_runner.py",
    "prediction_context_repair_service.py",
    "prediction_fallback_policy.py",
    "prediction_request_resolver.py",
    "prediction_run_reuse_policy.py",
    "pricing_experiment_service.py",
    "stripe_billing_profile_service.py",
    "stripe_checkout_service.py",
    "stripe_customer_portal_service.py",
    "stripe_webhook_idempotency_service.py",
    "stripe_webhook_service.py",
    "user_astro_profile_service.py",
    "user_birth_profile_service.py",
    "user_natal_chart_service.py",
    "user_prediction_baseline_service.py",
}

FORBIDDEN_SERVICE_SUFFIXES = ("_legacy", "_old", "_tmp", "_refacto", "_new", "_v2")


def _services_root() -> Path:
    return Path(__file__).resolve().parents[2] / "services"


def test_services_root_matches_story_70_23_allowlist() -> None:
    """La racine services ne doit conserver que les services transverses documentes."""
    current_files = {
        path.name
        for path in _services_root().iterdir()
        if path.is_file() and "__pycache__" not in path.parts
    }

    assert current_files == SERVICES_ROOT_ALLOWLIST


def test_removed_root_service_files_are_physically_absent() -> None:
    """Les anciens chemins plats migres ne doivent plus exister."""
    services_root = _services_root()
    assert all(not (services_root / file_name).exists() for file_name in REMOVED_ROOT_SERVICE_FILES)


def test_services_tests_package_is_absent() -> None:
    """Aucun package de test ne doit rester sous app.services."""
    tests_dir = _services_root() / "tests"
    assert not tests_dir.exists()


def test_services_modules_do_not_reference_backend_scripts() -> None:
    """Le runtime applicatif ne doit pas importer backend/scripts depuis app.services."""
    forbidden_fragments = ("from scripts.", "import scripts.", '"scripts/', "'scripts/")

    for file_path in _services_root().rglob("*.py"):
        if "__pycache__" in file_path.parts:
            continue
        content = file_path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            assert fragment not in content, f"{fragment} found in {file_path}"


def test_services_init_does_not_reexport_business_modules() -> None:
    """Le package services doit rester neutre et ne pas rejouer de compatibilite legacy."""
    content = (_services_root() / "__init__.py").read_text(encoding="utf-8")

    assert "from ." not in content
    assert "__all__" not in content
    assert "compat" not in content


def test_forbidden_suffixes_are_absent_from_canonical_service_paths() -> None:
    """Les chemins canoniques services ne doivent pas reutiliser de suffixes de transition."""
    forbidden_paths = []
    for file_path in _services_root().rglob("*.py"):
        if "__pycache__" in file_path.parts:
            continue
        stem = file_path.stem
        if any(stem.endswith(suffix) for suffix in FORBIDDEN_SERVICE_SUFFIXES):
            forbidden_paths.append(file_path.relative_to(_services_root()).as_posix())

    assert forbidden_paths == []


def test_b2c_runtime_gates_delegate_to_shared_kernel() -> None:
    """Les gates B2C ne doivent plus repliquer leur logique commune localement."""
    entitlement_root = _services_root() / "entitlement"
    gate_files = [
        entitlement_root / "chat_entitlement_gate.py",
        entitlement_root / "thematic_consultation_entitlement_gate.py",
        entitlement_root / "natal_chart_long_entitlement_gate.py",
    ]
    forbidden_snippets = (
        "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
        "QuotaUsageService.consume",
        "select_quota_usage_state",
        "map_b2c_reason_to_legacy",
    )

    for file_path in gate_files:
        content = file_path.read_text(encoding="utf-8")
        assert "from app.services.entitlement.b2c_runtime_gate import" in content
        for snippet in forbidden_snippets:
            assert snippet not in content, f"{snippet} found in {file_path}"


def test_nominal_services_do_not_keep_story_70_23_legacy_bypasses() -> None:
    """Les services canoniques ne doivent plus conserver de bypass legacy nominaux."""
    forbidden_snippets_by_file = {
        "consultation/catalogue_service.py": (
            "map_legacy_key",
            "support legacy",
            "compatibilité des clés legacy",
        ),
        "entitlement/horoscope_daily_entitlement_gate.py": (
            "horoscope_daily_entitlement_fallback_full",
            "Backward compatibility",
            "Legacy compatibility",
        ),
    }

    for relative_path, forbidden_snippets in forbidden_snippets_by_file.items():
        content = (_services_root() / relative_path).read_text(encoding="utf-8")
        for snippet in forbidden_snippets:
            assert snippet not in content, f"{snippet} found in {relative_path}"
