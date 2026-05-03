# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Signed processing failure returns retryable non-2xx. | `backend/app/api/v1/routers/public/billing.py` maps `failed_internal` to centralized `stripe_webhook_processing_failed` HTTP 500 after committing the failed idempotency row. | `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py`; baseline/after evidence artifacts. | PASS |
| AC2 | Failed rows remain reclaimable on redelivery. | Existing `StripeWebhookIdempotencyService.claim_event` failed-row reclaim path is preserved. | `pytest -q app/tests/unit/test_stripe_webhook_idempotency_service.py`; integration redelivery assertion in `test_webhook_business_failure_persists_failed_and_retry_is_accepted`. | PASS |
| AC3 | Unsupported events remain acknowledged. | `StripeWebhookService.handle_event` still marks unsupported events processed and returns `event_ignored`. | `pytest -q app/tests/unit/test_stripe_webhook_service.py`; full `pytest -q`. | PASS |
| AC4 | API adapter boundary remains intact. | Route owns HTTP status mapping only; service continues to own business/idempotency outcome and does not import `app.api`. SQL boundary allowlist line numbers realigned to current touched route without adding new SQL debt. | API error architecture pytest passed; SQL boundary exact allowlist pytest passed; targeted non-API import scan returned zero hits. | PASS |
| AC5 | Documentation matches retry behavior. | `docs/billing-webhook-idempotency.md` and `docs/billing-webhook-local-testing.md` document HTTP 500 retry behavior and operator reconciliation path. | Targeted docs scan for forbidden `failed_internal` HTTP 200 wording returned zero hits; full `pytest -q` passed. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
