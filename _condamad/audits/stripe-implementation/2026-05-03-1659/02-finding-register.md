# Finding Register - stripe-implementation

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | boundary-violation | stripe-implementation | E-005, E-006, E-007, E-010 | `refresh_subscription` is an API route that directly owns Stripe SDK retrieval and event-payload construction, so a second Stripe use-case owner exists outside the billing service layer. | Move admin subscription refresh orchestration into a billing/admin service, keep the API route as a thin adapter, and add a guard that API routers do not call `get_stripe_client` or `stripe_client.*` directly. | yes |
| F-002 | Medium | High | observability-gap | stripe-implementation | E-010, E-011, E-014, E-018 | Stripe calls share no app-owned timeout/retry policy, so a slow or transient Stripe API failure can affect checkout, portal, startup validation, webhook hydration, or admin refresh inconsistently. | Define a central Stripe client/network policy with explicit timeout and retry decisions, then verify checkout, portal, webhook hydration, startup validation, and admin refresh error mapping. | yes |
| F-003 | Medium | Medium | boundary-violation | stripe-implementation | E-001, E-012, E-018 | Stripe billing persistence is tightly coupled to SQLAlchemy models and sessions inside services; this is stable today but blocks a clean infra/repository boundary and makes future cross-cutting guards harder. | needs-user-decision | needs-user-decision |
| F-004 | Info | High | runtime-contract-drift | stripe-implementation | E-003, E-013, E-014, E-018 | The previous webhook retry, API version, event registry, and infra client ownership risks are resolved or guarded in the audited target. | No new story. Preserve the existing targeted Stripe regression suite and registry/client guards. | no |
| F-005 | Info | High | security-risk | stripe-implementation | E-008, E-009, E-015, E-016, E-018 | Core Stripe security controls remain present: services do not depend on API adapters, local Stripe dev is opt-in, and no live secrets or legacy card/payment APIs were found. | No new story. Re-run secret and legacy-payment scans before changing payment collection surfaces. | no |

## Finding Details

### F-001 - Admin subscription refresh owns Stripe SDK orchestration in the API layer

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: stripe-implementation
- Evidence: E-005, E-006, E-007, E-010.
- Expected rule: API routers should remain HTTP adapters; Stripe SDK calls and billing synchronization use cases should be owned by services or infra-facing application services.
- Actual state: `backend/app/api/v1/routers/admin/users.py` imports `get_stripe_client`, retrieves `stripe_client.subscriptions.retrieve(...)`, builds an `admin.forced_refresh` event payload, and calls `StripeBillingProfileService.update_from_event_payload(...)`. The integration test patches the router's imported `get_stripe_client`, confirming router-level ownership.
- Impact: `refresh_subscription` is an API route that directly owns Stripe SDK retrieval and event-payload construction, so a second Stripe use-case owner exists outside the billing service layer.
- Recommended action: Move admin subscription refresh orchestration into a billing/admin service, keep the API route as a thin adapter, and add a guard that API routers do not call `get_stripe_client` or `stripe_client.*` directly.
- Story candidate: yes
- Suggested archetype: service-boundary-refactor

### F-002 - Stripe external calls lack an app-owned timeout/retry policy

- Severity: Medium
- Confidence: High
- Category: observability-gap
- Domain: stripe-implementation
- Evidence: E-010, E-011, E-014, E-018.
- Expected rule: external payment-provider calls should have an explicit application policy for timeout, retry, and error mapping, even when the SDK has internal defaults.
- Actual state: the central client configures `stripe_version`, but scans found no `timeout` or `max_network_retries` policy. Stripe calls exist in checkout, portal sessions, subscription updates, invoice previews, subscription schedule retrieval, startup validation, and admin refresh.
- Impact: Stripe calls share no app-owned timeout/retry policy, so a slow or transient Stripe API failure can affect checkout, portal, startup validation, webhook hydration, or admin refresh inconsistently.
- Recommended action: Define a central Stripe client/network policy with explicit timeout and retry decisions, then verify checkout, portal, webhook hydration, startup validation, and admin refresh error mapping.
- Story candidate: yes
- Suggested archetype: observability-guard-hardening

### F-003 - Stripe billing persistence remains service-coupled

- Severity: Medium
- Confidence: Medium
- Category: boundary-violation
- Domain: stripe-implementation
- Evidence: E-001, E-012, E-018.
- Expected rule: the service boundary contract prefers services orchestrating use cases through repositories/ports rather than directly owning persistence model access.
- Actual state: `backend/app/services/billing` directly imports infra DB models and performs `select`, `db.scalar`, `db.query`, `db.add`, and `db.flush` for Stripe billing profiles, webhook idempotency, plan catalog, quota runtime, and related billing state.
- Impact: Stripe billing persistence is tightly coupled to SQLAlchemy models and sessions inside services; this is stable today but blocks a clean infra/repository boundary and makes future cross-cutting guards harder.
- Recommended action: needs-user-decision
- Story candidate: needs-user-decision
- Suggested archetype: data-model-boundary-convergence

### F-004 - Previous Stripe correction stories are resolved or guarded

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: stripe-implementation
- Evidence: E-003, E-013, E-014, E-018.
- Expected rule: previously identified Stripe risks should either be implemented or remain tracked as story candidates.
- Actual state: the current implementation has retryable signed-webhook failure behavior, a canonical webhook event registry, an infra-owned Stripe client, and explicit API version config/tests/docs.
- Impact: The previous webhook retry, API version, event registry, and infra client ownership risks are resolved or guarded in the audited target.
- Recommended action: No new story. Preserve the existing targeted Stripe regression suite and registry/client guards.
- Story candidate: no
- Suggested archetype: runtime-contract-preservation

### F-005 - Core Stripe security and No Legacy controls are present

- Severity: Info
- Confidence: High
- Category: security-risk
- Domain: stripe-implementation
- Evidence: E-008, E-009, E-015, E-016, E-018.
- Expected rule: Stripe implementation should keep secrets out of source, use hosted payment surfaces, keep local listener opt-in, and avoid API dependencies in service/infra layers.
- Actual state: scans found no API imports or FastAPI response types in billing services/infra, no live Stripe secrets, no raw card collection or legacy Charges/Sources/Tokens usage, and local Stripe listener ownership is documented and tested.
- Impact: Core Stripe security controls remain present: services do not depend on API adapters, local Stripe dev is opt-in, and no live secrets or legacy card/payment APIs were found.
- Recommended action: No new story. Re-run secret and legacy-payment scans before changing payment collection surfaces.
- Story candidate: no
- Suggested archetype: auth-security-audit
