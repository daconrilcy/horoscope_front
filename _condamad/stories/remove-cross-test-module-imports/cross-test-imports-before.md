# Cross-test imports before

Command from repository root:

```powershell
rg -n "from (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_|import (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_" backend/app/tests backend/tests
```

Result: 9 hits.

```text
backend/app/tests\unit\test_canonical_entitlement_alert_handling_service_events.py:19:from app.tests.unit.test_canonical_entitlement_alert_handling_service import (
backend/app/tests\integration\test_billing_api_61_65.py:9:from app.tests.integration.test_billing_api import _cleanup_tables, _register_and_get_access_token
backend/app/tests\integration\test_billing_api_61_66.py:11:from app.tests.integration.test_billing_api import _cleanup_tables, _register_and_get_access_token
backend/app/tests\integration\test_engine_persistence_e2e.py:11:from app.tests.regression.test_engine_non_regression import build_engine_input, load_json
backend/app/tests\integration\test_ops_alert_batch_handle_api.py:17:from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
backend/app/tests\integration\test_ops_alert_events_batch_retry_api.py:18:from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
backend/app/tests\integration\test_ops_alert_events_list_api.py:13:from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
backend/app/tests\integration\test_ops_alert_event_handle_api.py:14:from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
backend/app/tests\integration\test_ops_alert_event_handling_history_api.py:13:from app.tests.integration.test_ops_review_queue_alerts_retry_api import (
```
