# Ops / Quality Test Inventory - After

After classification, every concerned backend docs, scripts, secrets, security, and ops test has one row in:

`_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`

The backend pytest collection remains unchanged.

## Classified Inventory

| Group | File | Owner | Collection decision |
|---|---|---|---|
| docs | `backend/app/tests/unit/test_natal_pro_docs.py` | Backend quality suite registry | standard_backend_pytest |
| scripts | `backend/app/tests/unit/test_b2b_usage_migration_scripts.py` | Backend quality suite registry | standard_backend_pytest |
| scripts | `backend/app/tests/integration/test_pipeline_scripts.py` | Backend quality suite registry | standard_backend_pytest |
| scripts | `backend/app/tests/integration/test_backup_restore_scripts.py` | Backend quality suite registry | standard_backend_pytest |
| scripts | `backend/app/tests/integration/test_ops_review_queue_alerts_script.py` | Backend quality suite registry | standard_backend_pytest |
| secrets | `backend/app/tests/integration/test_secrets_scan_script.py` | Security quality suite registry | standard_backend_pytest |
| secrets | `backend/app/tests/integration/test_secret_rotation_process_restart.py` | Security quality suite registry | standard_backend_pytest |
| secrets | `backend/app/tests/integration/test_secret_rotation_critical_flows.py` | Security quality suite registry | standard_backend_pytest |
| security | `backend/app/tests/integration/test_security_verification_script.py` | Security quality suite registry | standard_backend_pytest |
| ops | `backend/app/tests/unit/test_ops_monitoring_service.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_batch_handle_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_events_list_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_event_handle_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_feature_flags_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_monitoring_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_monitoring_llm_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_persona_api.py` | Backend integration suite | standard_backend_pytest |
| ops | `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | Backend integration suite | standard_backend_pytest |

## Expected Invariant

Any new backend test matching docs, scripts, secret, security, or ops naming must be added to the ownership registry with an owner, command, dependency classification, and collection decision.
