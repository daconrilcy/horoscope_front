# Story Candidates - stripe-implementation

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Harden Stripe webhook failure retry semantics
- Suggested archetype: `data-integrity-guard-hardening`
- Primary domain: stripe-implementation
- Required contracts: API adapter boundary, service boundary, webhook idempotency, Stripe event delivery contract, regression guardrails `RG-004`, `RG-005`, `RG-006`.
- Draft objective: Ensure every signed Stripe event that fails local business processing is either eligible for Stripe automatic retry or durably retried by the application without silent billing snapshot drift.
- Must include:
  - Decide between non-2xx retry semantics and durable async queue/reconciliation before 2xx acknowledgement.
  - Update `backend/app/api/v1/routers/public/billing.py`, `StripeWebhookService`, and idempotency tests accordingly.
  - Update `docs/billing-webhook-idempotency.md` so documented retry behavior matches runtime behavior.
  - Add a test proving failed signed processing does not become silently terminal.
  - Include a reconciliation or operator path for existing `stripe_webhook_events.status = failed`.
- Validation hints:
  - `. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py`
  - Targeted route/error contract tests for signed failure behavior.
- Blockers: choose retry strategy: Stripe automatic retry via non-2xx, or internal durable queue/reconciler with immediate 2xx.

## SC-002

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Upgrade Stripe API version with webhook contract validation
- Suggested archetype: `runtime-contract-preservation`
- Primary domain: stripe-implementation
- Required contracts: Stripe SDK/API versioning, API contract shape, webhook versioning, regression guardrails `RG-004`, `RG-006`.
- Draft objective: Move the application from the stale default Stripe API version to the current supported Stripe API version through an explicit, tested compatibility upgrade.
- Must include:
  - Update `STRIPE_API_VERSION` default and `.env.example`.
  - Update `test_stripe_client.py` expectations.
  - Verify Stripe Python SDK compatibility and decide whether `stripe==14.4.1` remains acceptable.
  - Review Checkout, Customer Portal, invoice preview, subscription schedule, and webhook payload assumptions.
  - Document webhook endpoint version expectations and rollback guidance.
- Validation hints:
  - `. .\.venv\Scripts\Activate.ps1; cd backend; ruff check app/integrations/stripe_client.py app/services/billing app/tests/unit/test_stripe_client.py`
  - `. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/integration/test_stripe_checkout_api.py app/tests/integration/test_stripe_customer_portal_api.py app/tests/integration/test_stripe_webhook_api.py`
- Blockers: confirm whether production Stripe account/workbench can be upgraded now or whether the application should temporarily keep a documented intentional pin.

## SC-003

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Centralize supported Stripe webhook event ownership
- Suggested archetype: `duplicate-rule-removal`
- Primary domain: stripe-implementation
- Required contracts: service boundary, No Legacy / DRY, docs/runtime parity, regression guardrails `RG-024`.
- Draft objective: Create one canonical supported-event registry for Stripe webhooks and use it to keep dispatch, user resolution, local docs/scripts, and guards in sync.
- Must include:
  - Define the canonical event registry in a non-API Stripe billing module.
  - Refactor `StripeWebhookService.handle_event` and `_resolve_user_id` to consume that registry or typed grouping.
  - Reconcile whether `checkout.session.async_payment_succeeded` and `subscription_schedule.*` are intentionally supported and document them.
  - Update local runbook/listener docs and guards to assert parity with the registry.
  - Preserve ignored-event behavior for unsupported events such as `invoice.payment_succeeded`.
- Validation hints:
  - `. .\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/integration/test_stripe_webhook_api.py`
  - `rg -n "subscription_schedule|checkout.session.async_payment_succeeded" backend/app/services/billing docs scripts backend/app/tests`
- Blockers: decide whether subscription schedule events are first-class supported behavior or accidental acceptance.
