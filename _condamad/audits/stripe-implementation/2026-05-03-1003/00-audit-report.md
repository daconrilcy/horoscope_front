# CONDAMAD Audit Report - stripe-implementation

## Scope

- Domain target: Stripe billing implementation across backend Stripe services, public billing API adapter, Stripe integration client, Stripe billing persistence, local Stripe scripts/docs, and frontend billing consumers.
- Archetype: `service-boundary-audit` with API adapter, contract-shape, data-integrity, security, DRY, No Legacy, and dependency direction dimensions.
- Mode: read-only for application code; only audit artifacts under `_condamad/audits/**` are created.
- Trigger: user requested a full audit of the Stripe implementation.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-004`, `RG-005`, `RG-006`, `RG-008`, and `RG-024`.

## Executive Verdict

The Stripe implementation has a solid base: checkout and subscription upgrade flows use Stripe Checkout Sessions, self-service management uses Customer Portal sessions, webhook signatures are verified, authenticated user endpoints are protected, Stripe identifiers have DB uniqueness guards, and targeted backend/frontend tests pass.

The main production risk is webhook failure acknowledgement. The current endpoint persists a failed idempotency row but still returns HTTP 200 for signed internal processing failures, which prevents Stripe automatic delivery retry unless an operator manually resends the event. That conflicts with the local idempotency documentation and creates a billing reconciliation risk.

Three medium issues remain: the default Stripe API version is stale relative to the current Stripe API version observed on 2026-05-03, the supported webhook event list is split across service code, resolver code, tests, scripts, and docs with drift for `checkout.session.async_payment_succeeded` and `subscription_schedule.*`, and the Stripe SDK client was under `app.integrations` instead of the canonical infra ownership for external clients.

## Findings

| ID | Severity | Summary | Status |
|---|---|---|---|
| F-001 | High | Signed webhook processing failures return HTTP 200 after marking the event `failed`, suppressing Stripe automatic retry. | story-candidate |
| F-002 | Medium | Default Stripe API version remains `2024-12-18.acacia`, while Stripe's current API version observed during the audit is `2026-04-22.dahlia`. | story-candidate |
| F-003 | Medium | Webhook event ownership is duplicated and drifted between runtime dispatch, user resolution, docs, and local listener guards. | story-candidate |
| F-004 | Info | Payment API selection avoids legacy Charges, Sources, Tokens, Card Element, and raw card handling. | no-action |
| F-005 | Info | Core security controls are present for Stripe endpoints and secrets. | no-action |
| F-006 | Medium | The Stripe SDK client lived under `backend/app/integrations` instead of the canonical `backend/app/infra` external-client layer. | fixed-in-current-working-tree |

## Stripe Surface Inventory

| Surface | Responsibility | Evidence |
|---|---|---|
| `backend/app/integrations/stripe_client.py` | Central Stripe SDK client with configured API version and secret-key cache at audit time; moved to `backend/app/infra/stripe/client.py` after F-006 was accepted. | E-005, E-014, E-018 |
| `backend/app/services/billing/stripe_checkout_service.py` | Subscription Checkout Session creation for Basic/Premium plans. | E-005, E-006, E-008 |
| `backend/app/services/billing/stripe_customer_portal_service.py` | Customer Portal, subscription flows, reactivation, and immediate upgrade payment sessions. | E-005, E-006, E-008 |
| `backend/app/services/billing/stripe_webhook_service.py` | Signature-verified event dispatch and billing profile mutation. | E-005, E-009, E-010, E-011 |
| `backend/app/services/billing/stripe_webhook_idempotency_service.py` | Event claim, duplicate suppression, failed re-claim state machine. | E-005, E-010 |
| `backend/app/services/billing/stripe_billing_profile_service.py` | Stripe customer/subscription snapshot and entitlement derivation. | E-005, E-010 |
| `backend/app/api/v1/routers/public/billing.py` | HTTP adapter for checkout, portal, subscription mutation, and webhook endpoint. | E-005, E-007, E-009 |
| `frontend/src/api/billing.ts` and `SubscriptionSettings.tsx` | Central frontend billing client and Stripe redirect workflows. | E-012, E-013 |
| `scripts/stripe-listen-webhook.ps1` and billing docs | Local Stripe CLI development support. | E-002, E-011 |

## No Legacy / DRY Notes

- No active use of `charges.create`, `PaymentIntent` creation, `createToken`, `createPaymentMethod`, Card Element, Sources API, or Tokens API was found in active Stripe app surfaces (E-008).
- The webhook event list is not canonicalized: runtime dispatch, user resolution, local docs, and tests each carry their own copy or subset (E-010, E-011). This is the only active DRY finding in scope.
- The Stripe SDK client had a misplaced owner under `app.integrations`; the accepted remediation moves it under `app.infra.stripe` and removes the old module rather than preserving a compatibility wrapper (E-018).
- `RG-024` applies to local dev startup: Stripe remains opt-in for the local stack and the canonical listener is PowerShell.

## Recommended Order

1. Fix webhook failure acknowledgement semantics: either enqueue durable async processing before returning 2xx, or return non-2xx for signed internal failures until a retry worker/reconciliation path exists.
2. Upgrade and test the Stripe API version deliberately, including webhook endpoint version expectations and Stripe SDK compatibility.
3. Introduce a single canonical supported-event registry used by service dispatch, user resolution, docs/tests, and local listener scripts.
4. Keep the Stripe SDK client under `app.infra.stripe` and guard against reintroducing `app.integrations.stripe_client`.

## Validation Notes

- Application code was not changed.
- Backend Python lint and tests were run after activating `.venv`.
- Frontend lint and targeted billing tests passed.
- Runtime route inventory was generated after activating `.venv`.
