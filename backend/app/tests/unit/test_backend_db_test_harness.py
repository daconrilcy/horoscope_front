"""Gardes d'architecture pour le harnais DB des tests backend."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
ALLOWLIST_PATH = (
    REPO_ROOT / "_condamad" / "stories" / "converge-db-test-fixtures" / "db-session-allowlist.md"
)
CANONICAL_HELPERS = {
    Path("app/tests/helpers/db_session.py"),
    Path("tests/integration/app_db.py"),
}
FORBIDDEN_PRODUCTION_DB_SESSION_STRING_TARGETS = {
    ".".join(("app", "infra", "db", "session", "SessionLocal")),
    ".".join(("app", "infra", "db", "session", "engine")),
}
APPROVED_CREATE_ALL_PATHS = {
    Path("app/tests/integration/billing_helpers.py"),
    Path("app/tests/integration/conftest.py"),
    Path("app/tests/integration/ops_alert_helpers.py"),
    Path("app/tests/integration/test_admin_actions_api.py"),
    Path("app/tests/integration/test_admin_ai_api.py"),
    Path("app/tests/integration/test_admin_content_api.py"),
    Path("app/tests/integration/test_admin_dashboard_api.py"),
    Path("app/tests/integration/test_admin_entitlements_api.py"),
    Path("app/tests/integration/test_admin_exports_api.py"),
    Path("app/tests/integration/test_admin_llm_config_api.py"),
    Path("app/tests/integration/test_admin_logs_api.py"),
    Path("app/tests/integration/test_admin_persona_endpoints.py"),
    Path("app/tests/integration/test_admin_stripe_actions_api.py"),
    Path("app/tests/integration/test_admin_support_api.py"),
    Path("app/tests/integration/test_astrologers_api.py"),
    Path("app/tests/integration/test_astrologers_v2.py"),
    Path("app/tests/integration/test_audit_api.py"),
    Path("app/tests/integration/test_auth_api.py"),
    Path("app/tests/integration/test_b2b_api_entitlements.py"),
    Path("app/tests/integration/test_b2b_astrology_api.py"),
    Path("app/tests/integration/test_b2b_billing_api.py"),
    Path("app/tests/integration/test_b2b_editorial_api.py"),
    Path("app/tests/integration/test_b2b_entitlement_repair.py"),
    Path("app/tests/integration/test_b2b_entitlements_audit.py"),
    Path("app/tests/integration/test_b2b_reconciliation_api.py"),
    Path("app/tests/integration/test_b2b_usage_api.py"),
    Path("app/tests/integration/test_billing_api.py"),
    Path("app/tests/integration/test_chat_api.py"),
    Path("app/tests/integration/test_chat_idempotence.py"),
    Path("app/tests/integration/test_chat_multi_persona.py"),
    Path("app/tests/integration/test_chat_persona_prompting.py"),
    Path("app/tests/integration/test_consultation_third_party.py"),
    Path("app/tests/integration/test_consultations_router.py"),
    Path("app/tests/integration/test_contract_api.py"),
    Path("app/tests/integration/test_daily_prediction_api.py"),
    Path("app/tests/integration/test_dev_seed.py"),
    Path("app/tests/integration/test_enterprise_credentials_api.py"),
    Path("app/tests/integration/test_entitlements_e2e_matrix.py"),
    Path("app/tests/integration/test_entitlements_plans.py"),
    Path("app/tests/integration/test_gateway_gpt5_params.py"),
    Path("app/tests/integration/test_geocoding_api.py"),
    Path("app/tests/integration/test_guidance_api.py"),
    Path("app/tests/integration/test_horoscope_daily_entitlement.py"),
    Path("app/tests/integration/test_horoscope_daily_variant_narration.py"),
    Path("app/tests/integration/test_llm_qa_router.py"),
    Path("app/tests/integration/test_llm_qa_runtime_contracts.py"),
    Path("app/tests/integration/test_llm_qa_seed.py"),
    Path("app/tests/integration/test_load_smoke_critical_flows.py"),
    Path("app/tests/integration/test_natal_calculate_api.py"),
    Path("app/tests/integration/test_natal_chart_accurate_api.py"),
    Path("app/tests/integration/test_natal_chart_long_entitlement.py"),
    Path("app/tests/integration/test_natal_free_short_variant.py"),
    Path("app/tests/integration/test_ops_alert_suppression_rules_api.py"),
    Path("app/tests/integration/test_ops_alert_suppression_rules_effects_api.py"),
    Path("app/tests/integration/test_ops_entitlement_mutation_audits_api.py"),
    Path("app/tests/integration/test_ops_feature_flags_api.py"),
    Path("app/tests/integration/test_ops_monitoring_api.py"),
    Path("app/tests/integration/test_ops_monitoring_llm_api.py"),
    Path("app/tests/integration/test_ops_persona_api.py"),
    Path("app/tests/integration/test_ops_review_queue_alerts_retry_api.py"),
    Path("app/tests/integration/test_ops_review_queue_alerts_script.py"),
    Path("app/tests/integration/test_privacy_api.py"),
    Path("app/tests/integration/test_privacy_evidence_api.py"),
    Path("app/tests/integration/test_reference_data_api.py"),
    Path("app/tests/integration/test_stripe_billing_profile_service_integration.py"),
    Path("app/tests/integration/test_stripe_checkout_api.py"),
    Path("app/tests/integration/test_stripe_customer_portal_api.py"),
    Path("app/tests/integration/test_support_api.py"),
    Path("app/tests/integration/test_thematic_consultation_entitlement.py"),
    Path("app/tests/integration/test_user_birth_profile_api.py"),
    Path("app/tests/integration/test_user_natal_chart_api.py"),
    Path("app/tests/integration/test_users_settings.py"),
    Path("app/tests/integration/_subprocess/secret_rotation_restart_runner.py"),
    Path("app/tests/regression/helpers.py"),
    Path("app/tests/unit/conftest.py"),
    Path("app/tests/unit/canonical_entitlement_alert_helpers.py"),
    Path("app/tests/unit/legacy_services/conftest.py"),
    Path("app/tests/unit/test_audit_service.py"),
    Path("app/tests/unit/test_auth_service.py"),
    Path("app/tests/unit/test_b2b_billing_service.py"),
    Path("app/tests/unit/test_b2b_editorial_service.py"),
    Path("app/tests/unit/test_b2b_reconciliation_service.py"),
    Path("app/tests/unit/test_billing_service.py"),
    Path("app/tests/unit/test_calibration_runtime.py"),
    Path("app/tests/unit/test_canonical_entitlement_alert_handling_service.py"),
    Path("app/tests/unit/test_canonical_entitlement_db_consistency_validator.py"),
    Path("app/tests/unit/test_canonical_entitlement_mutation_audit.py"),
    Path("app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py"),
    Path("app/tests/unit/test_canonical_entitlement_mutation_service.py"),
    Path("app/tests/unit/test_chart_result_service.py"),
    Path("app/tests/unit/test_chat_guidance_service.py"),
    Path("app/tests/unit/test_effective_entitlement_resolver_service.py"),
    Path("app/tests/unit/test_enterprise_api_key_auth_service.py"),
    Path("app/tests/unit/test_enterprise_credentials_service.py"),
    Path("app/tests/unit/test_enterprise_quota_usage_service.py"),
    Path("app/tests/unit/test_entitlement_mutation_model_structure.py"),
    Path("app/tests/unit/test_gateway_3_roles.py"),
    Path("app/tests/unit/test_gateway_behavioral.py"),
    Path("app/tests/unit/test_gateway_modes.py"),
    Path("app/tests/unit/test_geo_place_resolved.py"),
    Path("app/tests/unit/test_guidance_service.py"),
    Path("app/tests/unit/test_incident_service.py"),
    Path("app/tests/unit/test_natal_calculation_service.py"),
    Path("app/tests/unit/test_natal_golden_swisseph.py"),
    Path("app/tests/unit/test_ops_monitoring_service.py"),
    Path("app/tests/unit/test_persona_config_service.py"),
    Path("app/tests/unit/test_persona_injection.py"),
    Path("app/tests/unit/test_privacy_service.py"),
    Path("app/tests/unit/test_product_entitlements_models.py"),
    Path("app/tests/unit/test_quota_usage_service.py"),
    Path("app/tests/unit/test_reference_data_service.py"),
    Path("app/tests/unit/test_stripe_billing_profile_service.py"),
    Path("app/tests/unit/test_stripe_billing_profile_service_61_65.py"),
    Path("app/tests/unit/test_user_astro_profile_service.py"),
    Path("app/tests/unit/test_user_birth_profile_service.py"),
    Path("app/tests/unit/test_user_natal_chart_service.py"),
    Path("app/tests/unit/test_use_case_contract.py"),
    Path("app/tests/unit/test_validation_sequence.py"),
    Path("tests/evaluation/conftest.py"),
    Path("tests/integration/conftest.py"),
    Path("tests/integration/test_backend_sqlite_alignment.py"),
    Path("tests/integration/test_help_api.py"),
    Path("tests/llm_orchestration/conftest.py"),
    Path("tests/llm_orchestration/test_admin_llm_api.py"),
    Path("tests/llm_orchestration/test_gateway_regressions_fix.py"),
    Path("tests/llm_orchestration/test_prompt_registry_v2.py"),
    Path("tests/unit/test_incident_service_user_statuses.py"),
    Path("tests/unit/test_sensitive_data_non_leakage.py"),
}
APPROVED_SQLITE_FACTORY_PATHS = {
    Path("app/tests/conftest.py"),
    Path("app/tests/helpers/db_session.py"),
    Path("app/tests/integration/conftest.py"),
    Path("app/tests/integration/test_admin_actions_api.py"),
    Path("app/tests/integration/test_admin_ai_api.py"),
    Path("app/tests/integration/test_admin_dashboard_api.py"),
    Path("app/tests/integration/test_admin_entitlements_api.py"),
    Path("app/tests/integration/test_admin_exports_api.py"),
    Path("app/tests/integration/test_admin_logs_api.py"),
    Path("app/tests/integration/test_admin_stripe_actions_api.py"),
    Path("app/tests/integration/test_admin_support_api.py"),
    Path("app/tests/integration/test_auth_api.py"),
    Path("app/tests/integration/test_chat_idempotence.py"),
    Path("app/tests/integration/test_daily_prediction_api.py"),
    Path("app/tests/integration/test_db_bootstrap.py"),
    Path("app/tests/integration/test_db_bootstrap_partial_upgrade.py"),
    Path("app/tests/integration/test_dev_seed.py"),
    Path("app/tests/integration/test_entitlements_e2e_matrix.py"),
    Path("app/tests/integration/test_gateway_gpt5_params.py"),
    Path("app/tests/integration/test_llm_qa_router.py"),
    Path("app/tests/integration/test_llm_qa_runtime_contracts.py"),
    Path("app/tests/integration/test_llm_qa_seed.py"),
    Path("app/tests/integration/test_migration_0037_add_contributors_json.py"),
    Path("app/tests/integration/test_migration_0039_add_is_provisional_calibration.py"),
    Path("app/tests/integration/test_migration_20260422_0073_cleanup_llm_legacy.py"),
    Path("app/tests/integration/test_migration_20260424_0082_drop_remaining_llm_legacy_columns.py"),
    Path("app/tests/integration/test_migration_8b2d52442493_add_input_schema_to_assembly.py"),
    Path("app/tests/integration/test_migration_a_prediction_tables.py"),
    Path("app/tests/integration/test_migration_b_ruleset_tables.py"),
    Path("app/tests/integration/test_migration_c_daily_prediction.py"),
    Path("app/tests/integration/test_ops_review_queue_alerts_script.py"),
    Path("app/tests/integration/test_reference_data_migrations.py"),
    Path("app/tests/integration/test_secret_rotation_process_restart.py"),
    Path("app/tests/integration/test_seed_31_prediction_v2.py"),
    Path("app/tests/integration/test_user_prediction_baseline.py"),
    Path("app/tests/integration/test_users_settings.py"),
    Path("app/tests/regression/helpers.py"),
    Path("app/tests/unit/conftest.py"),
    Path("app/tests/unit/legacy_services/conftest.py"),
    Path("app/tests/unit/test_calibration_runtime.py"),
    Path("app/tests/unit/test_canonical_entitlement_db_consistency_validator.py"),
    Path("app/tests/unit/test_canonical_entitlement_mutation_audit.py"),
    Path("app/tests/unit/test_canonical_entitlement_mutation_service.py"),
    Path("app/tests/unit/test_effective_entitlement_resolver_service.py"),
    Path("app/tests/unit/test_gateway_3_roles.py"),
    Path("app/tests/unit/test_gateway_behavioral.py"),
    Path("app/tests/unit/test_gateway_modes.py"),
    Path("app/tests/unit/test_geo_place_resolved.py"),
    Path("app/tests/unit/test_persona_injection.py"),
    Path("app/tests/unit/test_quota_usage_service.py"),
    Path("app/tests/unit/test_use_case_contract.py"),
    Path("app/tests/unit/test_validation_sequence.py"),
    Path("tests/evaluation/conftest.py"),
    Path("tests/integration/conftest.py"),
    Path("tests/integration/test_backend_sqlite_alignment.py"),
    Path("tests/llm_orchestration/conftest.py"),
    Path("tests/llm_orchestration/test_admin_llm_api.py"),
    Path("tests/llm_orchestration/test_gateway_regressions_fix.py"),
    Path("tests/llm_orchestration/test_prompt_registry_v2.py"),
    Path("tests/unit/test_sensitive_data_non_leakage.py"),
}
APPROVED_PRIMARY_DB_REFERENCE_WITH_CREATE_ALL_PATHS = {
    Path("tests/integration/test_backend_sqlite_alignment.py"),
}


def _test_python_files() -> list[Path]:
    """Liste les fichiers Python de tests couverts par la garde DB."""
    roots = [BACKEND_ROOT / "app" / "tests", BACKEND_ROOT / "tests"]
    return sorted(
        file_path
        for root in roots
        for file_path in root.rglob("*.py")
        if "__pycache__" not in file_path.parts
    )


def _load_allowed_paths() -> set[Path]:
    """Charge les exceptions persistées par fichier depuis l'allowlist de story."""
    allowed_paths: set[Path] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `backend/"):
            continue
        raw_path = stripped.split("|", maxsplit=2)[1].strip().strip("`")
        allowed_paths.add(Path(raw_path).relative_to("backend"))
    return allowed_paths


def _has_forbidden_direct_import(tree: ast.AST) -> bool:
    """Détecte les imports production directs de session/engine DB."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "app.infra.db.session":
            continue
        imported_names = {alias.name for alias in node.names}
        if imported_names.intersection({"SessionLocal", "engine"}):
            return True
    return False


def _has_forbidden_db_session_module_access(tree: ast.AST) -> bool:
    """Détecte l'accès indirect à la session ou au moteur DB de production."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.attr not in {"SessionLocal", "engine"}:
            continue
        if isinstance(node.value, ast.Name) and node.value.id == "db_session_module":
            return True
    return False


def _has_forbidden_production_db_session_string_target(tree: ast.AST) -> bool:
    """Détecte les patchs par chaîne vers la session ou le moteur DB de production."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if node.value in FORBIDDEN_PRODUCTION_DB_SESSION_STRING_TARGETS:
            return True
    return False


def _has_base_metadata_create_all(tree: ast.AST) -> bool:
    """Détecte les appels ORM `Base.metadata.create_all` à classifier."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "create_all":
            continue
        metadata = function.value
        if not isinstance(metadata, ast.Attribute) or metadata.attr != "metadata":
            continue
        if isinstance(metadata.value, ast.Name) and metadata.value.id == "Base":
            return True
    return False


def _has_sqlite_create_engine_factory(tree: ast.AST) -> bool:
    """Détecte les factories SQLite secondaires à garder explicitement classifiées."""
    sqlite_variable_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        value_starts_with_sqlite = False
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value_starts_with_sqlite = node.value.value.startswith("sqlite")
        if isinstance(node.value, ast.JoinedStr):
            value_starts_with_sqlite = any(
                isinstance(value, ast.Constant) and str(value.value).startswith("sqlite")
                for value in node.value.values
            )
        if not value_starts_with_sqlite:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                sqlite_variable_names.add(target.id)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "create_engine":
            continue
        if not node.args:
            continue
        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            if first_arg.value.startswith("sqlite"):
                return True
        if isinstance(first_arg, ast.JoinedStr):
            for value in first_arg.values:
                if isinstance(value, ast.Constant) and str(value.value).startswith("sqlite"):
                    return True
        if isinstance(first_arg, ast.Name) and first_arg.id in sqlite_variable_names:
            return True
    return False


def test_no_new_direct_production_db_session_imports_in_backend_tests() -> None:
    """Empêche les nouveaux tests d'importer la session DB de production."""
    allowed_paths = _load_allowed_paths()
    violations: list[str] = []

    for file_path in _test_python_files():
        relative_path = file_path.relative_to(BACKEND_ROOT)
        if relative_path in CANONICAL_HELPERS:
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        if (
            _has_forbidden_direct_import(tree)
            or _has_forbidden_db_session_module_access(tree)
            or _has_forbidden_production_db_session_string_target(tree)
        ):
            if relative_path not in allowed_paths:
                violations.append(relative_path.as_posix())

    assert violations == []


def test_migrated_representative_tests_stay_off_production_session_imports() -> None:
    """Verrouille le lot migré sur les helpers DB canoniques."""
    migrated_paths = [
        BACKEND_ROOT / "tests" / "integration" / "test_llm_release.py",
        BACKEND_ROOT / "app" / "tests" / "integration" / "test_admin_content_api.py",
    ]

    for file_path in migrated_paths:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        assert not _has_forbidden_direct_import(tree), file_path
        assert not _has_forbidden_db_session_module_access(tree), file_path
        assert not _has_forbidden_production_db_session_string_target(tree), file_path


def test_create_all_usage_stays_classified_outside_primary_horoscope_db() -> None:
    """Bloque les nouveaux `create_all` DB sans classification explicite."""
    violations: list[str] = []
    primary_db_violations: list[str] = []

    for file_path in _test_python_files():
        relative_path = file_path.relative_to(BACKEND_ROOT)
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        if not _has_base_metadata_create_all(tree):
            continue
        if relative_path not in APPROVED_CREATE_ALL_PATHS:
            violations.append(relative_path.as_posix())
        if (
            "horoscope.db" in file_path.read_text(encoding="utf-8")
            and relative_path not in APPROVED_PRIMARY_DB_REFERENCE_WITH_CREATE_ALL_PATHS
        ):
            primary_db_violations.append(relative_path.as_posix())

    assert violations == []
    assert primary_db_violations == []


def test_sqlite_secondary_factories_stay_classified() -> None:
    """Bloque les nouvelles factories SQLite de test sans garde d'alignement dédiée."""
    violations: list[str] = []

    for file_path in _test_python_files():
        relative_path = file_path.relative_to(BACKEND_ROOT)
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
        if (
            _has_sqlite_create_engine_factory(tree)
            and relative_path not in APPROVED_SQLITE_FACTORY_PATHS
        ):
            violations.append(relative_path.as_posix())

    assert violations == []
