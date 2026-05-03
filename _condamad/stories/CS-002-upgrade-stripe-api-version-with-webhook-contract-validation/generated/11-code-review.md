# CONDAMAD Code Review

## Review target

- Story: `CS-002-upgrade-stripe-api-version-with-webhook-contract-validation`
- Source: `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/00-story.md`
- Reviewed commit: `974d137b Upgrade Stripe API version to dahlia`
- Reviewer date: 2026-05-03

## Inputs reviewed

- Story contract and acceptance criteria AC1-AC5.
- Capsule evidence: `generated/03-acceptance-traceability.md`, `generated/06-validation-plan.md`, `generated/07-no-legacy-dry-guardrails.md`, `generated/10-final-evidence.md`.
- Persistent evidence: `evidence/stripe-api-version-baseline.md`, `evidence/stripe-api-version-after.md`.
- Regression guardrail registry: `_condamad/stories/regression-guardrails.md`.
- Diff for `.env.example`, `backend/app/core/config.py`, `backend/app/infra/stripe/client.py`, `backend/app/jobs/calibration/__init__.py`, `backend/app/tests/unit/test_stripe_client.py`, `docs/billing-webhook-local-testing.md`, `pytest.ini`, and related test updates.

## Diff summary

- Runtime Stripe API default changed to `2026-04-22.dahlia` in `backend/app/core/config.py` and `.env.example`.
- Stripe SDK construction remains centralized in `backend/app/infra/stripe/client.py`.
- Duplicate Stripe SDK constructor was removed from `backend/app/jobs/calibration/__init__.py`.
- Unit guard coverage was added in `backend/app/tests/unit/test_stripe_client.py`.
- Webhook API version and rollback expectations were documented in `docs/billing-webhook-local-testing.md`.
- Root pytest collection settings were adjusted in `pytest.ini` to support the recorded validation run.

## Review layers

- Diff integrity: reviewed changed files and `git diff --check HEAD^..HEAD`.
- Acceptance audit: mapped AC1-AC5 to code, tests, docs, and persistent evidence.
- Validation audit: reran required targeted commands in the activated venv.
- DRY / No Legacy audit: scanned for legacy Stripe paths, duplicate constructors, old active defaults, and forbidden API imports.
- Edge/security audit: checked that webhook failure semantics and API error/import boundaries were not changed by this story.

## Findings

No actionable findings.

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `backend/app/core/config.py:382` and `.env.example:38` default to `2026-04-22.dahlia`; runtime settings command passes with `APP_DISABLE_BACKEND_DOTENV=1`. |
| AC2 | PASS | `backend/app/infra/stripe/client.py:20` constructs `stripe.StripeClient(..., stripe_version=settings.stripe_api_version)`; `backend/app/tests/unit/test_stripe_client.py:31` asserts the configured version is passed. |
| AC3 | PASS | Targeted unit billing tests for checkout, customer portal and webhook services passed. No billing service payload shape changes were introduced. |
| AC4 | PASS | Targeted billing integration tests for checkout, customer portal and webhook APIs passed. FastAPI app import/start construction passed. |
| AC5 | PASS | `evidence/stripe-api-version-after.md:7` records the SDK decision; `docs/billing-webhook-local-testing.md:94` documents endpoint version expectation and rollback. |

## Validation audit

Commands run by reviewer:

| Command | Working directory | Result |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/infra/stripe/client.py app/core/config.py app/jobs/calibration/__init__.py app/services/billing app/tests/unit/test_stripe_client.py` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/integration/test_stripe_checkout_api.py app/tests/integration/test_stripe_customer_portal_api.py app/tests/integration/test_stripe_webhook_api.py` | repo root | PASS, 107 passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; $env:APP_DISABLE_BACKEND_DOTENV='1'; python -c "from app.core.config import Settings; assert Settings().stripe_api_version == '2026-04-22.dahlia'"` | repo root | PASS |
| `git diff --check HEAD^..HEAD` | repo root | PASS |
| `rg -n "from app\.api\|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core` | repo root | PASS, zero hits |
| `rg -n "app\.integrations\.stripe_client\|app/integrations/stripe_client.py" backend/app backend/tests docs .env.example` | repo root | PASS, zero hits |
| `rg -n "StripeClient\(" backend/app backend/tests` | repo root | PASS, canonical constructor plus guard-test self-reference |
| `rg -n "2024-12-18\.acacia" backend/app backend/tests .env.example docs` | repo root | PASS, rollback documentation only |
| `.\.venv\Scripts\Activate.ps1; cd backend; $env:APP_DISABLE_BACKEND_DOTENV='1'; python -c "from app.main import app; assert app.title == 'horoscope-backend'; print(app.title)"` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; $env:APP_DISABLE_BACKEND_DOTENV='1'; python -c "from app.main import app; assert app.title == 'horoscope-backend'; print(app.title)"; pytest -q` | repo root | TIMEOUT after 180s; not counted as passed |
| `pytest -q` | backend | PASS, user-provided manual rerun: 3552 passed, 12 skipped in 601.43s |

The reviewer rerun of the full suite timed out after 180 seconds, but the user provided a later manual full-suite result: `3552 passed, 12 skipped in 601.43s`.

## DRY / No Legacy audit

- Duplicate Stripe SDK construction is not active: `rg -n "StripeClient\(" backend/app backend/tests` finds only `backend/app/infra/stripe/client.py:20` and the self-reference in `backend/app/tests/unit/test_stripe_client.py:87`.
- Forbidden legacy path is absent from active code/docs scans.
- Old API version is not an active default; it appears only in `docs/billing-webhook-local-testing.md:100` as rollback guidance.
- `RG-004` and `RG-006` remain satisfied for this story scope: no `app.api` imports were found from services, domain, infra or core.

## Residual risks

- Live Stripe Dashboard compatibility was not validated locally and remains outside story scope.
- The reviewer did not reproduce the full `pytest -q` pass because the command timed out after 180 seconds; the user provided a later manual full-suite pass.

## Verdict

`CLEAN`
