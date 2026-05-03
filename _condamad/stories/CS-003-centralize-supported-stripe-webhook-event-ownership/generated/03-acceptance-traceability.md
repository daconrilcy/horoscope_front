# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Canonical registry exists outside API. | Added `app/services/billing/stripe_webhook_events.py`; parity guard imports it. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` passed; API import scan passed. | PASS |
| AC2 | Dispatch consumes registry. | `StripeWebhookService.handle_event` uses `is_supported_webhook_event` and `CHECKOUT_UPGRADE_EVENT_TYPES`. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` passed; runtime guard checks service source. | PASS |
| AC3 | User resolution consumes registry grouping. | `_resolve_user_id` uses `CHECKOUT_CLIENT_REFERENCE_EVENT_TYPES`, `CUSTOMER_LOOKUP_EVENT_TYPES`, and `CUSTOMER_OBJECT_ID_LOOKUP_EVENT_TYPES`. | `pytest -q app/tests/unit/test_stripe_webhook_service.py` passed; runtime guard checks resolver source. | PASS |
| AC4 | Local docs match registry. | Docs and PowerShell listener aligned to `LOCAL_LISTENER_EVENT_TYPES`; guard compares docs/script to registry. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` passed. | PASS |
| AC5 | Unsupported invoice success remains ignored. | `invoice.payment_succeeded` absent from registry; unit and integration behavior returns `event_ignored`. | `pytest -q app/tests/integration/test_stripe_webhook_api.py` passed. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
