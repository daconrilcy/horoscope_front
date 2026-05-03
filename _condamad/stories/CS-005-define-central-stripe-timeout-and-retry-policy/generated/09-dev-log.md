# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/stories/story-status.md` modified; CS-005 capsule untracked.
- AGENTS considered: `AGENTS.md`.
- Guardrails read: `_condamad/stories/regression-guardrails.md`.

## Decisions

- Valeurs retenues: timeout Stripe 10 secondes, max network retries 2.
- Settings operables via env pour documenter la politique et permettre ajustement ops.
- Startup validation conserve la semantique existante: `warn` fail-open, `strict` fail-closed.
- Webhook hydration transitoire reste fail-closed/retryable pour Stripe.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | FAIL then PASS | First run missed `stripe` import in startup test; rerun passed 87 tests. |
