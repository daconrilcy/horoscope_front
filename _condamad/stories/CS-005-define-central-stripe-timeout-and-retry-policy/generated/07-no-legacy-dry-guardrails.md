# No Legacy / DRY Guardrails

## Canonical ownership

- Configuration: `backend/app/core/config.py`.
- Application SDK: `backend/app/infra/stripe/client.py`.
- Error mapping: services billing/startup existants puis adaptateurs API.

## Forbidden

- `stripe.StripeClient(` hors `backend/app/infra/stripe/client.py`.
- `timeout` ou `max_network_retries` Stripe dans `backend/app/services/billing/**`, `backend/app/api/**`, `backend/app/startup/**`.
- Nouveau wrapper client Stripe.
- Import `app.api` ou FastAPI dans services billing/infra/startup.
- Fallback legacy pour valeurs timeout/retry.

## Required evidence

- Garde AST dans `test_stripe_client.py`.
- Scan cible des symboles `timeout|max_network_retries|StripeClient(`.
- Scan boundary `from app.api|import app.api|HTTPException|JSONResponse|fastapi`.

## Applicable regression guardrails

- `RG-004`: ne pas decentraliser les erreurs HTTP.
- `RG-006`: conserver la frontiere API stricte.
- `RG-024`: ne pas rendre Stripe obligatoire au demarrage local.
