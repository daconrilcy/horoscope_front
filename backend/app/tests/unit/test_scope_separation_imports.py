import ast
import importlib
import inspect


def _get_imported_names(module_name: str) -> set[str]:
    """Retourne l'ensemble des noms importés dans un module (via ast)."""
    module = importlib.import_module(module_name)
    source = inspect.getsource(module)
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[-1])
                if alias.asname:
                    names.add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name)
                if alias.asname:
                    names.add(alias.asname)
    return names


def test_b2b_gate_does_not_import_quota_usage_service():
    names = _get_imported_names("app.services.b2b.api_entitlement_gate")
    assert "QuotaUsageService" not in names, (
        "b2b_api_entitlement_gate ne doit pas importer QuotaUsageService"
    )


def test_b2b_usage_summary_does_not_import_quota_usage_service():
    names = _get_imported_names("app.services.b2b.canonical_usage_service")
    assert "QuotaUsageService" not in names, (
        "b2b_canonical_usage_service ne doit pas importer QuotaUsageService"
    )


def test_b2b_billing_does_not_import_quota_usage_service():
    names = _get_imported_names("app.services.b2b.billing_service")
    assert "QuotaUsageService" not in names, (
        "b2b_billing_service ne doit pas importer QuotaUsageService"
    )


def test_b2b_reconciliation_does_not_import_quota_usage_service():
    names = _get_imported_names("app.services.b2b.reconciliation_service")
    assert "QuotaUsageService" not in names, (
        "b2b_reconciliation_service ne doit pas importer QuotaUsageService"
    )


def test_chat_gate_does_not_import_enterprise_quota_usage_service():
    names = _get_imported_names("app.services.entitlement.chat_entitlement_gate")
    assert "EnterpriseQuotaUsageService" not in names, (
        "chat_entitlement_gate ne doit pas importer EnterpriseQuotaUsageService"
    )


def test_thematic_consultation_gate_does_not_import_enterprise_quota_usage_service():
    names = _get_imported_names("app.services.entitlement.thematic_consultation_entitlement_gate")
    assert "EnterpriseQuotaUsageService" not in names, (
        "thematic_consultation_entitlement_gate ne doit pas importer EnterpriseQuotaUsageService"
    )


def test_natal_chart_long_gate_does_not_import_enterprise_quota_usage_service():
    names = _get_imported_names("app.services.entitlement.natal_chart_long_entitlement_gate")
    assert "EnterpriseQuotaUsageService" not in names, (
        "natal_chart_long_entitlement_gate ne doit pas importer EnterpriseQuotaUsageService"
    )
