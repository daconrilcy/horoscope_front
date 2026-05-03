# CONDAMAD Code Review

## Review target

- Story: `CS-005-define-central-stripe-timeout-and-retry-policy`
- Story file: `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/00-story.md`
- Review date: 2026-05-03
- Reviewer verdict: `CLEAN`

## Inputs reviewed

- Story capsule `00-story.md`
- Generated traceability and final evidence under `generated/`
- Regression guardrails registry `_condamad/stories/regression-guardrails.md`
- Current working tree diff for backend Stripe config/client/services/tests
- Reviewer validation commands listed below

## Diff summary

The implementation remains story-scoped: it changes Stripe settings, the
central Stripe client, admin refresh Stripe error mapping, targeted Stripe
tests, `.env.example`, and CONDAMAD governance artifacts. No unrelated
application surface was found in the diff.

## Findings

No actionable findings remain.

This review pass found no new issue.

Previously resolved:

- `CR-001` formatting drift: `ruff format --check .` initially reported
  `app/infra/stripe/__init__.py` and
  `app/services/billing/stripe_checkout_service.py`. Ruff formatting was
  applied, then `ruff format --check .` passed.
- Private Stripe SDK import was replaced with public
  `stripe.RequestsClient(...)`.
- Direct unsupported `timeout=` on `stripe.StripeClient(...)` was replaced by
  `http_client=stripe.RequestsClient(timeout=...)`; retries remain on
  `StripeClient`.

## Acceptance audit

| AC | Result | Notes |
|---|---|---|
| AC1 | PASS | Timeout is applied through public `stripe.RequestsClient`; retries are applied through `StripeClient`. |
| AC2 | PASS | Ownership remains centralized in config and infra Stripe client; scans show no competing Stripe policy owner. |
| AC3 | PASS | Checkout and portal timeout mappings remain covered by targeted tests. |
| AC4 | PASS | Startup, webhook hydration and admin refresh transient-failure behavior is tested. |
| AC5 | PASS | `.env.example` and settings parsing document/load the chosen values. |

Applicable guardrails:

- `RG-004`: no services/infra/startup FastAPI dependency was found.
- `RG-006`: no `app.api` imports from services/infra/startup were found.
- `RG-024`: no local Stripe startup script change was present.
- `RG-025`: central Stripe network policy owner is present and guarded.

## Validation audit

Reviewer-verified passing commands:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/infra/stripe app/core/config.py app/services/billing app/startup/stripe_portal_validation.py app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_portal_startup_validation.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/integration/test_stripe_webhook_api.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check .
.\.venv\Scripts\Activate.ps1; cd backend; ruff check .
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q
.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(len(app.routes))"
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-005-define-central-stripe-timeout-and-retry-policy --final
git diff --check
```

Results:

- Targeted tests: `91 passed`
- Full backend tests after all fixes: `3576 passed, 12 skipped`
- App import: `220` routes registered
- Ruff format/check: pass
- CONDAMAD validation: pass
- `git diff --check`: pass, with line-ending warnings only

Reviewer-verified scans:

```powershell
rg -n "stripe\._http_client|from stripe\._|timeout|max_network_retries|StripeClient\(" app/infra/stripe app/services/billing app/api/v1/routers app/startup -g "*.py"
rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe app/startup -g "*.py"
```

Scan result:

- Stripe network policy hits are centralized in `app/infra/stripe/client.py`.
- No private Stripe module import remains in the scanned surface.
- Remaining `timeout` hits are unrelated LLM/API error-code references.
- FastAPI/API-boundary scan returned zero hits for services/infra/startup.

## DRY / No Legacy audit

No second `StripeClient` owner was found. The timeout/retry policy is owned by
`backend/app/core/config.py` and applied by
`backend/app/infra/stripe/client.py` through public Stripe SDK APIs.

## Commands run by reviewer

- targeted `git diff` reads
- targeted Ruff check in the activated venv
- targeted pytest command in the activated venv
- global Ruff format check in the activated venv
- Ruff format fix for the two reported files
- global Ruff check in the activated venv
- full backend pytest in the activated venv
- app import probe in the activated venv
- `rg` scans listed above
- `git diff --check`
- CONDAMAD capsule validation

## Residual risks

None identified.

## Verdict

`CLEAN`
