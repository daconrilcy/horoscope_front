# Risk Matrix - stripe-implementation

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Stripe webhook endpoint and billing snapshot reconciliation | High: failed rows depend on manual resend or future custom reconciliation | Medium | P0 |
| F-002 | Medium | Medium | Stripe SDK/API contract and webhook payload assumptions | Medium: tests currently preserve old version value | Medium | P1 |
| F-003 | Medium | Medium | Stripe event dispatch, user resolution, docs, scripts, and guards | Medium: duplicated lists create drift and missed guard coverage | Medium | P1 |
| F-004 | Info | Low | Payment API selection | Low: regression only if future code introduces old Stripe APIs | Low | Monitor |
| F-005 | Info | Low | Stripe endpoint security and secrets | Low: preserve with tests/scans | Low | Monitor |
| F-006 | Medium | Low | Stripe SDK client ownership and import paths | Low: already remediated in current working tree; risk is reintroducing `app.integrations.stripe_client` | Low | Done |

## Regression Guardrail Mapping

| Guardrail | Applicability | Findings |
|---|---|---|
| RG-004 | API errors should remain centralized and services should not depend on FastAPI. | F-001, F-005 |
| RG-005 | API must not own business logic/persistence. | F-001, F-005 |
| RG-006 | Non-API layers must not import `app.api`. | F-005 |
| RG-008 | Known direct SQL/API exceptions must not grow silently. | F-005 |
| RG-024 | Local dev stack must not require Stripe unless explicitly enabled. | F-003, F-004 |

## Recommended Priority

1. P0: fix F-001 before relying on Stripe webhooks for production entitlement correctness.
2. P1: handle F-002 and F-003 together or sequentially before the next major billing feature.
3. Done: F-006 is remediated by moving the client under `app.infra.stripe`.
4. Monitor: preserve F-004 and F-005 with negative scans and existing targeted tests.
