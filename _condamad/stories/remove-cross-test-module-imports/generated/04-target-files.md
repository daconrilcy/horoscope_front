# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_billing_api_61_65.py`
- `backend/app/tests/integration/test_billing_api_61_66.py`
- `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py`
- `backend/app/tests/integration/test_ops_alert_batch_handle_api.py`
- `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py`
- `backend/app/tests/integration/test_ops_alert_events_list_api.py`
- `backend/app/tests/integration/test_ops_alert_event_handle_api.py`
- `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py`
- `backend/app/tests/integration/test_engine_persistence_e2e.py`
- `backend/app/tests/regression/test_engine_non_regression.py`
- `backend/app/tests/regression/helpers.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py`

## Must search

- `rg -n "from (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_|import (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_" backend/app/tests backend/tests`
- `rg --files backend/app/tests backend/tests -g '*helpers*.py' -g conftest.py`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/tests backend/tests -g test_*.py -g '*helpers*.py'`

## Likely modified

- `backend/app/tests/integration/test_billing_api.py`
- `backend/app/tests/integration/test_billing_api_61_65.py`
- `backend/app/tests/integration/test_billing_api_61_66.py`
- `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py`
- ops alert integration consumers listed above
- `backend/app/tests/integration/test_engine_persistence_e2e.py`
- `backend/app/tests/regression/test_engine_non_regression.py`
- `backend/app/tests/regression/helpers.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py`
- `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py`
- `backend/app/tests/unit/test_backend_test_helper_imports.py`
- `_condamad/stories/remove-cross-test-module-imports/*.md`

## Likely added

- `backend/app/tests/integration/billing_helpers.py`
- `backend/app/tests/integration/ops_alert_helpers.py`
- `backend/app/tests/unit/canonical_entitlement_alert_helpers.py`

## Files likely deleted

- None.

## Forbidden unless directly justified

- Production files under `backend/app/api`, `backend/app/services`, `backend/app/domain`, `backend/app/infra`.
- Frontend files.
- `requirements.txt`.
