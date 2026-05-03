# Risk Matrix - stripe-implementation

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---:|---|---|---|---|
| F-001 | High | Medium | Admin forced subscription refresh, API/service boundary, Stripe SDK ownership | A route-level Stripe SDK owner can drift from billing service behavior and bypass future service-level guards. | Medium: integration test passes but patches router-owned client. | P1 |
| F-002 | Medium | Medium | Checkout, portal, webhook hydration, startup validation, admin refresh | Slow or transient Stripe failures can be handled inconsistently without a central timeout/retry policy. | Medium: many call sites share the same client but no policy guard exists. | P2 |
| F-003 | Medium | Medium | Stripe billing profile, webhook idempotency, plan/quota billing persistence | Repository-boundary convergence later will be broader because services directly use SQLAlchemy models and sessions. | High: stable existing tests, but broad refactor if chosen. | P2 |
| F-004 | Info | Low | Previously remediated webhook/client/event/version surfaces | Prior Stripe findings could regress if guard tests are removed. | Low: targeted tests and docs/script parity guards pass. | P3 |
| F-005 | Info | Low | Stripe secrets, local dev listener, hosted payment surface | Security posture could regress if payment collection changes without scans. | Low: scans currently pass. | P3 |
