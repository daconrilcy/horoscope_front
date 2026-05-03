# No Legacy / DRY Guardrails

## Canonical responsibilities

| Responsibility | Canonical owner | Forbidden alternate |
|---|---|---|
| Stripe SDK client construction | `backend/app/infra/stripe/client.py` | `backend/app/integrations/stripe_client.py` |
| Stripe API version setting | `settings.stripe_api_version` in `backend/app/core/config.py` | per-service constants or alternate env names |
| Billing API contract | Existing FastAPI billing routes and service contracts | frontend-side Stripe payload logic |

## Forbidden patterns

- Recreating `backend/app/integrations/stripe_client.py`.
- Importing `app.integrations.stripe_client`.
- Adding a second Stripe API version variable or per-service override.
- Keeping `2024-12-18.acacia` as an active default.
- Introducing compatibility wrappers, aliases, silent fallbacks, or duplicate Stripe clients.

## Applicable regression guardrails

- `RG-004`: API error behavior remains centralized.
- `RG-006`: services, domain, infra and core do not import `app.api`.

## Required evidence

- Stripe client test proves `stripe_version=settings.stripe_api_version`.
- Negative scan for the forbidden legacy integration path.
- Old version scan classifies historical references only.
- Import boundary scan for `app.api` from non-API layers.
