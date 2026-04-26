"""Contrats OpenAPI minimaux pour les routeurs API v1 conserves."""

from __future__ import annotations

from app.main import app

EXPECTED_ROUTE_METHODS = {
    ("/v1/admin/llm/catalog", "get"),
    ("/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample", "post"),
    ("/v1/admin/llm/assembly/configs", "get"),
    ("/v1/admin/llm/consumption/canonical", "get"),
    ("/v1/admin/llm/releases/{snapshot_id}/activate", "post"),
    ("/v1/admin/content/texts", "get"),
    ("/v1/b2b/astrology/weekly-by-sign", "get"),
    ("/v1/ops/monitoring/conversation-kpis", "get"),
    ("/v1/predictions/daily", "get"),
    ("/v1/users/me/birth-data", "get"),
}

MOVED_ROUTE_OPENAPI_BASELINE = {
    ("/v1/b2b/credentials", "get"): {
        "tags": ["b2b-credentials"],
        "operationId": "list_enterprise_credentials_v1_b2b_credentials_get",
        "responses": ["200", "401", "403", "404", "422", "429"],
    },
    ("/v1/b2b/credentials/generate", "post"): {
        "tags": ["b2b-credentials"],
        "operationId": "generate_enterprise_credential_v1_b2b_credentials_generate_post",
        "responses": ["200", "401", "403", "404", "422", "429", "503"],
    },
    ("/v1/b2b/credentials/rotate", "post"): {
        "tags": ["b2b-credentials"],
        "operationId": "rotate_enterprise_credential_v1_b2b_credentials_rotate_post",
        "responses": ["200", "401", "403", "404", "422", "429", "503"],
    },
    ("/v1/ops/b2b/entitlements/audit", "get"): {
        "tags": ["ops-b2b-entitlements"],
        "operationId": "get_b2b_entitlements_audit_v1_ops_b2b_entitlements_audit_get",
        "responses": ["200", "401", "403", "422", "429"],
    },
    ("/v1/ops/b2b/entitlements/repair/classify-zero-units", "post"): {
        "tags": ["ops-b2b-entitlements"],
        "operationId": (
            "classify_zero_units_v1_ops_b2b_entitlements_repair_classify_zero_units_post"
        ),
        "responses": ["200", "401", "403", "422", "429"],
    },
    ("/v1/ops/b2b/entitlements/repair/run", "post"): {
        "tags": ["ops-b2b-entitlements"],
        "operationId": "run_repair_v1_ops_b2b_entitlements_repair_run_post",
        "responses": ["200", "401", "403", "422", "429"],
    },
    ("/v1/ops/b2b/entitlements/repair/set-admin-user", "post"): {
        "tags": ["ops-b2b-entitlements"],
        "operationId": "set_admin_user_v1_ops_b2b_entitlements_repair_set_admin_user_post",
        "responses": ["200", "401", "403", "422", "429"],
    },
    ("/v1/ops/b2b/reconciliation/issues", "get"): {
        "tags": ["ops-b2b-reconciliation"],
        "operationId": "list_reconciliation_issues_v1_ops_b2b_reconciliation_issues_get",
        "responses": ["200", "401", "403", "422", "429", "503"],
    },
    ("/v1/ops/b2b/reconciliation/issues/{issue_id}", "get"): {
        "tags": ["ops-b2b-reconciliation"],
        "operationId": (
            "get_reconciliation_issue_detail_v1_ops_b2b_reconciliation_issues__issue_id__get"
        ),
        "responses": ["200", "401", "403", "404", "422", "429", "503"],
    },
    ("/v1/ops/b2b/reconciliation/issues/{issue_id}/actions", "post"): {
        "tags": ["ops-b2b-reconciliation"],
        "operationId": (
            "execute_reconciliation_action_v1_ops_b2b_reconciliation_issues__issue_id__actions_post"
        ),
        "responses": ["200", "401", "403", "404", "422", "429", "503"],
    },
}


def test_conserved_v1_routes_remain_in_openapi() -> None:
    """Les chemins publics conserves restent montes apres le rangement Python."""
    schema = app.openapi()
    missing = [
        f"{method.upper()} {path}"
        for path, method in sorted(EXPECTED_ROUTE_METHODS)
        if method not in schema["paths"].get(path, {})
    ]

    assert missing == []


def test_moved_routes_keep_targeted_openapi_contract() -> None:
    """Les routeurs déplacés gardent path, méthode, tags, operationId et statuts."""
    schema = app.openapi()
    mismatches: list[str] = []
    for (path, method), expected in MOVED_ROUTE_OPENAPI_BASELINE.items():
        operation = schema["paths"].get(path, {}).get(method)
        if operation is None:
            mismatches.append(f"{method.upper()} {path} missing")
            continue
        for key in ("tags", "operationId"):
            if operation.get(key) != expected[key]:
                mismatches.append(f"{method.upper()} {path} {key}={operation.get(key)!r}")
        responses = sorted(operation.get("responses", {}))
        if responses != expected["responses"]:
            mismatches.append(f"{method.upper()} {path} responses={responses!r}")

    assert mismatches == []
