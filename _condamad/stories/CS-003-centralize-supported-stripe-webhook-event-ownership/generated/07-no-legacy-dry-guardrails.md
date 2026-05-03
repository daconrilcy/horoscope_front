# No Legacy / DRY Guardrails

## Canonical ownership

- Supported Stripe webhook events: `backend/app/services/billing/stripe_webhook_events.py`.
- Runtime dispatch: `backend/app/services/billing/stripe_webhook_service.py` consumes the registry.
- Local listener: `scripts/stripe-listen-webhook.ps1` remains the only local script.
- Documentation: docs may show event names, but tests must compare them to the registry.

## Forbidden

- Duplicate active event tuples in `handle_event` or `_resolve_user_id`.
- Compatibility wrappers, aliases, re-exports, silent fallbacks, or second registries.
- `scripts/stripe-listen-webhook.sh`.
- Moving ownership to `backend/app/api`.
- Marking `invoice.payment_succeeded` as supported.

## Required evidence

- Baseline snapshot before convergence.
- After snapshot proving consumers align to the canonical registry.
- Tests that import the registry and fail on docs/script/runtime drift.
- Scans for `subscription_schedule` and `checkout.session.async_payment_succeeded` with hit classification.
