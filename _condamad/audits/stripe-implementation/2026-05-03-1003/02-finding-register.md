# Finding Register - stripe-implementation

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | data-integrity-risk | stripe-implementation | E-003, E-009, E-010, E-014 | A signed Stripe event can fail local business processing, be marked `failed`, and still be acknowledged with HTTP 200, preventing Stripe automatic retry and leaving billing state stale until manual resend or later reconciliation. | Change the webhook contract so failed signed processing either returns non-2xx for Stripe retry or is durably enqueued/reconciled before returning 2xx; add tests proving automatic retry eligibility or durable async retry. | yes |
| F-002 | Medium | High | runtime-contract-drift | stripe-implementation | E-003, E-005, E-015 | New Stripe requests default to an old API version, while tests and `.env.example` encode that value; future Stripe SDK/API upgrades may be skipped silently and webhook/event shape expectations can diverge from current Stripe behavior. | Plan and validate an API version upgrade to current Stripe API, update defaults/docs/tests, and explicitly verify webhook endpoint version behavior. | yes |
| F-003 | Medium | High | duplicate-responsibility | stripe-implementation | E-010, E-011 | Supported webhook events are defined in multiple places with drift, so new event support can be added to runtime dispatch without docs/listener/test coverage or user-resolution parity. | Introduce one canonical supported-event registry or manifest consumed by dispatch/resolution docs/tests/scripts, and reconcile the currently omitted runtime-accepted events. | yes |
| F-004 | Info | High | legacy-surface | stripe-implementation | E-005, E-008, E-014 | The implementation avoids legacy Stripe payment APIs and keeps payment collection on hosted Stripe surfaces, reducing PCI and maintenance exposure. | No action; keep negative scans for Charges/Sources/Tokens/Card Element if Stripe payment surfaces are changed. | no |
| F-005 | Info | High | security-risk | stripe-implementation | E-006, E-007, E-010, E-014, E-016 | Current controls include authenticated user endpoints, unsigned webhook rejection, missing-secret handling, central Stripe client setup, and no real committed Stripe secrets in active scan results. | No immediate action; preserve these controls in future Stripe stories and keep secret scans in release validation. | no |
| F-006 | Medium | High | boundary-violation | stripe-implementation | E-001, E-004, E-005, E-018 | The Stripe SDK client was owned by `app.integrations` even though the repository architecture assigns external clients to `app.infra`, creating a second ownership convention for integrations. | Move the Stripe SDK client to `app.infra.stripe.client`, update imports/tests, and keep the old `app.integrations.stripe_client` path absent instead of adding a compatibility wrapper. | no |

## Finding Details

### F-001 - Webhook failure acknowledgement suppresses automatic retry

- Severity: High
- Confidence: High
- Category: data-integrity-risk
- Domain: stripe-implementation
- Evidence: E-003, E-009, E-010, E-014.
- Expected rule: a billing webhook that fails after signature verification must either remain eligible for Stripe delivery retry or be durably captured for independent retry/reconciliation before acknowledgement.
- Actual state: `StripeWebhookService.handle_event` catches business exceptions, marks the event failed, returns `failed_internal`, and the router commits and returns HTTP 200. The idempotency doc says failed status lets Stripe retry later, but Stripe only automatically retries failed deliveries when the endpoint previously returned non-2xx.
- Impact: A signed Stripe event can fail local business processing, be marked `failed`, and still be acknowledged with HTTP 200, preventing Stripe automatic retry and leaving billing state stale until manual resend or later reconciliation.
- Recommended action: Change the webhook contract so failed signed processing either returns non-2xx for Stripe retry or is durably enqueued/reconciled before returning 2xx; add tests proving automatic retry eligibility or durable async retry.
- Story candidate: yes
- Suggested archetype: data-integrity-guard-hardening

### F-002 - Stripe API version default is stale

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: stripe-implementation
- Evidence: E-003, E-005, E-015.
- Expected rule: the Stripe API version should be intentionally current or explicitly pinned with an upgrade policy and tests.
- Actual state: `backend/app/core/config.py`, `.env.example`, and Stripe client tests use `2024-12-18.acacia`; official Stripe docs observed during the audit report `2026-04-22.dahlia` as current.
- Impact: New Stripe requests default to an old API version, while tests and `.env.example` encode that value; future Stripe SDK/API upgrades may be skipped silently and webhook/event shape expectations can diverge from current Stripe behavior.
- Recommended action: Plan and validate an API version upgrade to current Stripe API, update defaults/docs/tests, and explicitly verify webhook endpoint version behavior.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-003 - Supported webhook events are not canonically owned

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: stripe-implementation
- Evidence: E-010, E-011.
- Expected rule: the supported Stripe event list should have one canonical owner used by runtime dispatch, user resolution, local CLI scripts, docs, and guards.
- Actual state: `stripe_webhook_service.py` embeds event tuples in both dispatch and user resolution; docs/scripts/tests carry separate subsets. Runtime accepts `checkout.session.async_payment_succeeded` and `subscription_schedule.created|updated|canceled|completed`, but the canonical local docs do not list those events as backend-accepted.
- Impact: Supported webhook events are defined in multiple places with drift, so new event support can be added to runtime dispatch without docs/listener/test coverage or user-resolution parity.
- Recommended action: Introduce one canonical supported-event registry or manifest consumed by dispatch/resolution docs/tests/scripts, and reconcile the currently omitted runtime-accepted events.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-004 - Legacy Stripe payment APIs are absent

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: stripe-implementation
- Evidence: E-005, E-008, E-014.
- Expected rule: subscription payments should use Checkout Sessions, Customer Portal, or other supported Stripe abstractions, not Charges/Sources/Tokens/Card Element/raw PAN flows.
- Actual state: active app code uses Checkout Sessions and Customer Portal; negative scans found no legacy payment API use in active Stripe code.
- Impact: The implementation avoids legacy Stripe payment APIs and keeps payment collection on hosted Stripe surfaces, reducing PCI and maintenance exposure.
- Recommended action: No action; keep negative scans for Charges/Sources/Tokens/Card Element if Stripe payment surfaces are changed.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-005 - Core Stripe security controls are present

- Severity: Info
- Confidence: High
- Category: security-risk
- Domain: stripe-implementation
- Evidence: E-006, E-007, E-010, E-014, E-016.
- Expected rule: user payment endpoints require auth, webhooks verify signatures, secrets are env-driven, and Stripe concerns do not leak across API/service boundaries.
- Actual state: checkout/portal/subscription endpoints require authenticated users; webhook rejects invalid signatures and missing secret config; active secret scan found no real committed Stripe secret; service layers do not import API adapters.
- Impact: Current controls include authenticated user endpoints, unsigned webhook rejection, missing-secret handling, central Stripe client setup, and no real committed Stripe secrets in active scan results.
- Recommended action: No immediate action; preserve these controls in future Stripe stories and keep secret scans in release validation.
- Story candidate: no
- Suggested archetype: auth-security-audit

### F-006 - Stripe SDK client was outside canonical infra ownership

- Severity: Medium
- Confidence: High
- Category: boundary-violation
- Domain: stripe-implementation
- Evidence: E-001, E-004, E-005, E-018.
- Expected rule: external technical clients belong to `backend/app/infra`, per the repository architecture reference.
- Actual state: at audit time, the Stripe SDK client lived in `backend/app/integrations/stripe_client.py`; after user acceptance, the working tree moves it to `backend/app/infra/stripe/client.py`.
- Impact: The Stripe SDK client was owned by `app.integrations` even though the repository architecture assigns external clients to `app.infra`, creating a second ownership convention for integrations.
- Recommended action: Move the Stripe SDK client to `app.infra.stripe.client`, update imports/tests, and keep the old `app.integrations.stripe_client` path absent instead of adding a compatibility wrapper.
- Story candidate: no
- Suggested archetype: service-boundary-refactor
