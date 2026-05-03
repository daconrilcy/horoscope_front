# Finding Register - stripe-client

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | data-integrity-risk | stripe-client | E-003, E-006, E-014, E-015 | The previous signed-webhook failure acknowledgement risk is resolved in the audited target: failed signed processing now returns retryable HTTP 500 and failed idempotency records can be retried. | No new story. Preserve this behavior with the existing integration test and idempotency coverage. | no |
| F-002 | Info | High | runtime-contract-drift | stripe-client | E-003, E-004, E-013, E-014 | The previous stale Stripe API default is resolved in the audited target: config/tests/docs use `2026-04-22.dahlia`, and the infra client passes that version to `stripe.StripeClient`. | No new story. Future Stripe upgrades should keep the same explicit version pin and webhook-contract validation path. | no |
| F-003 | Info | High | duplicate-responsibility | stripe-client | E-003, E-005, E-007, E-011, E-014 | The previous supported-event ownership drift is resolved in the audited target: runtime, resolver, docs, script, and guards converge on the canonical registry. | No new story. Keep docs/script parity tests when adding or removing supported events. | no |
| F-004 | Info | High | boundary-violation | stripe-client | E-004, E-008, E-009, E-010, E-013, E-014 | The Stripe SDK client is now owned by the canonical infra layer and no active service/infra code depends on API adapters or HTTP response types. | No new story. Keep the `app.integrations.stripe_client` absence guard and constructor uniqueness guard. | no |
| F-005 | Info | High | legacy-surface | stripe-client | E-012, E-014 | No active legacy Stripe payment API surface or committed live Stripe secret was found in the audited target. | No new story. Re-run the negative scan if payment collection surfaces change. | no |

## Finding Details

### F-001 - Signed webhook failure semantics are now retryable

- Severity: Info
- Confidence: High
- Category: data-integrity-risk
- Domain: stripe-client
- Evidence: E-003, E-006, E-014, E-015.
- Expected rule: a signed Stripe webhook that fails local business processing must remain eligible for Stripe retry or be durably retried by the application.
- Actual state: `StripeWebhookService.handle_event` can return `failed_internal`; the public billing router maps that outcome to HTTP 500 with code `stripe_webhook_processing_failed`; integration coverage proves first failure persists `failed` and a second delivery can become `processed`.
- Impact: The previous signed-webhook failure acknowledgement risk is resolved in the audited target: failed signed processing now returns retryable HTTP 500 and failed idempotency records can be retried.
- Recommended action: No new story. Preserve this behavior with the existing integration test and idempotency coverage.
- Story candidate: no
- Suggested archetype: data-integrity-guard-hardening

### F-002 - Stripe API version default is current and explicit

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: stripe-client
- Evidence: E-003, E-004, E-013, E-014.
- Expected rule: Stripe API version usage must be intentional, tested, and aligned between config, client construction, docs, and tests.
- Actual state: `.env.example`, `backend/app/core/config.py`, docs, and `test_stripe_client.py` reference `2026-04-22.dahlia`; `get_stripe_client()` passes `settings.stripe_api_version` to `stripe.StripeClient`.
- Impact: The previous stale Stripe API default is resolved in the audited target: config/tests/docs use `2026-04-22.dahlia`, and the infra client passes that version to `stripe.StripeClient`.
- Recommended action: No new story. Future Stripe upgrades should keep the same explicit version pin and webhook-contract validation path.
- Story candidate: no
- Suggested archetype: runtime-contract-preservation

### F-003 - Supported webhook events have one service-owned registry

- Severity: Info
- Confidence: High
- Category: duplicate-responsibility
- Domain: stripe-client
- Evidence: E-003, E-005, E-007, E-011, E-014.
- Expected rule: supported Stripe webhook events should have one canonical owner used by dispatch, user resolution, local listener, docs, and guards.
- Actual state: `stripe_webhook_events.py` owns the registry and derived groups; `StripeWebhookService` consumes these groups; tests assert PowerShell listener parity, docs parity, runtime dispatch usage, and ignored behavior for `invoice.payment_succeeded`.
- Impact: The previous supported-event ownership drift is resolved in the audited target: runtime, resolver, docs, script, and guards converge on the canonical registry.
- Recommended action: No new story. Keep docs/script parity tests when adding or removing supported events.
- Story candidate: no
- Suggested archetype: duplicate-rule-removal

### F-004 - Stripe client ownership respects service/infra boundaries

- Severity: Info
- Confidence: High
- Category: boundary-violation
- Domain: stripe-client
- Evidence: E-004, E-008, E-009, E-010, E-013, E-014.
- Expected rule: external technical clients belong to infra; services must not import API adapters or return HTTP responses.
- Actual state: the Stripe SDK client lives at `app.infra.stripe.client`; active scans found no API adapter imports or FastAPI/HTTP response types in audited service/infra code; tests guard against reintroducing `app.integrations.stripe_client`.
- Impact: The Stripe SDK client is now owned by the canonical infra layer and no active service/infra code depends on API adapters or HTTP response types.
- Recommended action: No new story. Keep the `app.integrations.stripe_client` absence guard and constructor uniqueness guard.
- Story candidate: no
- Suggested archetype: service-boundary-refactor

### F-005 - Legacy payment surfaces remain absent

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: stripe-client
- Evidence: E-012, E-014.
- Expected rule: subscription payment collection should stay on hosted Stripe surfaces and must not introduce Charges/Sources/Tokens/Card Element/raw PAN handling without a dedicated security design.
- Actual state: targeted scans found no active legacy payment APIs, raw card collection snippets, or live Stripe keys in audited source/docs/scripts.
- Impact: No active legacy Stripe payment API surface or committed live Stripe secret was found in the audited target.
- Recommended action: No new story. Re-run the negative scan if payment collection surfaces change.
- Story candidate: no
- Suggested archetype: legacy-surface-audit
