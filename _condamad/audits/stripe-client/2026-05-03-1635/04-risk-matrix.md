# Risk Matrix - stripe-client

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---:|---|---|---|---|
| F-001 | Info | Low | `POST /v1/billing/stripe-webhook` signed failure path | A signed processing failure could be acknowledged before durable recovery. | None for current code; keep existing tests. | Low |
| F-002 | Info | Low | Stripe SDK client API version | Client and webhook payload shapes could drift from the configured Stripe API version. | None for current code; future upgrade requires validation. | Low |
| F-003 | Info | Low | Supported webhook event ownership | Docs/listener/runtime/resolver could drift on supported event types. | None for current code; use registry for event changes. | Low |
| F-004 | Info | Low | Stripe client ownership and dependency direction | A second Stripe client owner or API dependency could return. | None for current code; keep legacy-path guard. | Low |
| F-005 | Info | Low | Payment collection/security surface | Legacy payment API or secret exposure could expand compliance scope. | None for current code; re-run scan on payment surface changes. | Low |
