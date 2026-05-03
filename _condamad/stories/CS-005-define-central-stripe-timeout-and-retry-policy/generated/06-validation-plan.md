# Validation Plan

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Tests Stripe cibles | `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | yes | Tous les tests passent. |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ownership timeout/retry | `rg -n "timeout|max_network_retries|StripeClient\\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"` | `backend/` | yes | Hits classes dans allowlist centrale ou faux positifs non Stripe. |
| Boundary API | `rg -n "from app\\.api|import app\\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"` | `backend/` | yes | Aucun import FastAPI/app.api dans services/infra/startup. |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint cible | `ruff check app/infra/stripe app/core/config.py app/services/billing app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | yes | Aucun lint error. |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression | `pytest -q` | `backend/` | yes | Suite complete passe ou limitation documentee. |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | Fichiers dans scope story uniquement. |
| Whitespace check | `git diff --check` | repo root | yes | Aucun marqueur conflit/erreur whitespace. |
