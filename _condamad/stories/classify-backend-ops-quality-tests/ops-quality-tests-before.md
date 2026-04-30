# Ops / Quality Test Inventory - Before

Baseline captured before classification. Source command:

```powershell
rg --files backend -g "test_*.py" | rg "(docs|scripts|ops|secret|security)"
```

| Group | File | Current collection | Initial ownership state |
|---|---|---|---|
| docs | `backend/app/tests/unit/test_natal_pro_docs.py` | standard backend pytest via `app/tests` | implicit |
| scripts | `backend/app/tests/unit/test_b2b_usage_migration_scripts.py` | standard backend pytest via `app/tests` | implicit |
| scripts | `backend/app/tests/integration/test_pipeline_scripts.py` | standard backend pytest via `app/tests` | implicit |
| scripts | `backend/app/tests/integration/test_backup_restore_scripts.py` | standard backend pytest via `app/tests` | implicit |
| scripts | `backend/app/tests/integration/test_ops_review_queue_alerts_script.py` | standard backend pytest via `app/tests` | implicit |
| secrets | `backend/app/tests/integration/test_secrets_scan_script.py` | standard backend pytest via `app/tests` | implicit |
| secrets | `backend/app/tests/integration/test_secret_rotation_process_restart.py` | standard backend pytest via `app/tests` | implicit |
| secrets | `backend/app/tests/integration/test_secret_rotation_critical_flows.py` | standard backend pytest via `app/tests` | implicit |
| security | `backend/app/tests/integration/test_security_verification_script.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/unit/test_ops_monitoring_service.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_batch_handle_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_events_list_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_event_handle_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_feature_flags_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_monitoring_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_monitoring_llm_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_persona_api.py` | standard backend pytest via `app/tests` | implicit |
| ops | `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | standard backend pytest via `app/tests` | implicit |

## Baseline Decision

Before this story, the tests were collected by backend pytest but did not have a persistent owner row, exact validation command, or OS/subprocess dependency classification.
