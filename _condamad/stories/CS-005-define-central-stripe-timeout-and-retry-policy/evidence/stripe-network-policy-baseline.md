# Stripe Network Policy Baseline

## Before implementation

- `backend/app/infra/stripe/client.py` instantiated `stripe.StripeClient` with `api_key` and `stripe_version`.
- No app-owned `timeout` or `max_network_retries` setting was applied to the Stripe SDK client.
- `get_stripe_client` returned `None` when `STRIPE_SECRET_KEY` was absent, preserving local Stripe opt-in behavior.
- Checkout, portal, startup validation, webhook hydration and admin refresh already consumed `get_stripe_client` directly or through billing services.

## Baseline scans

- Audit source: `_condamad/audits/stripe-implementation/2026-05-03-1659/01-evidence-log.md#E-011`.
- Finding source: `_condamad/audits/stripe-implementation/2026-05-03-1659/02-finding-register.md#F-002`.
