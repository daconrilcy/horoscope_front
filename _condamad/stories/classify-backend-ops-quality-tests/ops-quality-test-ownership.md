# Ops / Quality Test Ownership Registry

Canonical ownership decision for backend docs, scripts, secrets, security, and ops tests.

## Suite Decision

| Decision | Value |
|---|---|
| Standard backend pytest scope changed | no |
| User approval required | no |
| Reason | All concerned tests remain under the existing `backend/pyproject.toml` `app/tests` root, so no backend scope change is introduced. |
| Canonical validation command | `pytest -q` from `backend` after `.\.venv\Scripts\Activate.ps1` |
| Reintroduction guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` |

## Allowed Owners

| Owner | Purpose |
|---|---|
| Backend quality suite registry | Documentation and script correctness checks that remain part of backend quality. |
| Security quality suite registry | Secret and security verification checks that remain part of backend quality. |
| Backend integration suite | Ops API and service tests that validate backend behavior. |

## Ownership Rows

| File | Group | Owner | Canonical command | OS dependency | Subprocess dependency | Collection decision |
|---|---|---|---|---|---|---|
| `backend/app/tests/unit/test_natal_pro_docs.py` | docs | Backend quality suite registry | `pytest -q app/tests/unit/test_natal_pro_docs.py` | none | none | standard_backend_pytest |
| `backend/app/tests/unit/test_b2b_usage_migration_scripts.py` | scripts | Backend quality suite registry | `pytest -q app/tests/unit/test_b2b_usage_migration_scripts.py` | none | none | standard_backend_pytest |
| `backend/app/tests/unit/test_start_dev_stack_script.py` | scripts | Backend quality suite registry | `pytest -q app/tests/unit/test_start_dev_stack_script.py` | none | none | standard_backend_pytest |
| `backend/app/tests/unit/test_llm_release_readiness_script.py` | scripts | Backend quality suite registry | `pytest -q app/tests/unit/test_llm_release_readiness_script.py` | none | none | standard_backend_pytest |
| `backend/app/tests/unit/test_load_test_critical_script.py` | scripts | Backend quality suite registry | `pytest -q app/tests/unit/test_load_test_critical_script.py` | none | none | standard_backend_pytest |
| `backend/app/tests/unit/test_scripts_ownership.py` | scripts | Backend quality suite registry | `pytest -q app/tests/unit/test_scripts_ownership.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_pipeline_scripts.py` | scripts | Backend quality suite registry | `pytest -q app/tests/integration/test_pipeline_scripts.py` | Windows/PowerShell compatible | script subprocess | standard_backend_pytest |
| `backend/app/tests/integration/test_backup_restore_scripts.py` | scripts | Backend quality suite registry | `pytest -q app/tests/integration/test_backup_restore_scripts.py` | Windows/PowerShell compatible | script subprocess | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_review_queue_alerts_script.py` | scripts | Backend quality suite registry | `pytest -q app/tests/integration/test_ops_review_queue_alerts_script.py` | Windows/PowerShell compatible | script subprocess | standard_backend_pytest |
| `backend/app/tests/integration/test_secrets_scan_script.py` | secrets | Security quality suite registry | `pytest -q app/tests/integration/test_secrets_scan_script.py` | Windows/PowerShell compatible | script subprocess | standard_backend_pytest |
| `backend/app/tests/integration/test_secret_rotation_process_restart.py` | secrets | Security quality suite registry | `pytest -q app/tests/integration/test_secret_rotation_process_restart.py` | Windows/PowerShell compatible | process restart subprocess | standard_backend_pytest |
| `backend/app/tests/integration/test_secret_rotation_critical_flows.py` | secrets | Security quality suite registry | `pytest -q app/tests/integration/test_secret_rotation_critical_flows.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_security_verification_script.py` | security | Security quality suite registry | `pytest -q app/tests/integration/test_security_verification_script.py` | Windows/PowerShell compatible | script subprocess | standard_backend_pytest |
| `backend/app/tests/unit/test_ops_monitoring_service.py` | ops | Backend integration suite | `pytest -q app/tests/unit/test_ops_monitoring_service.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_batch_handle_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_batch_handle_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_events_batch_retry_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_events_list_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_events_list_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_event_handle_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_event_handle_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_event_handling_history_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_suppression_rules_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_alert_suppression_rules_effects_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_feature_flags_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_feature_flags_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_monitoring_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_monitoring_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_monitoring_llm_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_monitoring_llm_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_persona_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_persona_api.py` | none | none | standard_backend_pytest |
| `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | ops | Backend integration suite | `pytest -q app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | none | none | standard_backend_pytest |

## Quality Suite Command

For targeted quality ownership verification:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_natal_pro_docs.py app/tests/unit/test_b2b_usage_migration_scripts.py app/tests/unit/test_start_dev_stack_script.py app/tests/integration/test_pipeline_scripts.py app/tests/integration/test_backup_restore_scripts.py app/tests/integration/test_ops_review_queue_alerts_script.py app/tests/integration/test_secrets_scan_script.py app/tests/integration/test_secret_rotation_process_restart.py app/tests/integration/test_secret_rotation_critical_flows.py app/tests/integration/test_security_verification_script.py
```

## Ops Suite Command

For targeted ops backend verification:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_ops_monitoring_service.py app/tests/integration/test_ops_alert_batch_handle_api.py app/tests/integration/test_ops_alert_events_batch_retry_api.py app/tests/integration/test_ops_alert_events_list_api.py app/tests/integration/test_ops_alert_event_handle_api.py app/tests/integration/test_ops_alert_event_handling_history_api.py app/tests/integration/test_ops_alert_suppression_rules_api.py app/tests/integration/test_ops_alert_suppression_rules_effects_api.py app/tests/integration/test_ops_entitlement_mutation_audits_api.py app/tests/integration/test_ops_feature_flags_api.py app/tests/integration/test_ops_monitoring_api.py app/tests/integration/test_ops_monitoring_llm_api.py app/tests/integration/test_ops_persona_api.py app/tests/integration/test_ops_review_queue_alerts_retry_api.py
```
