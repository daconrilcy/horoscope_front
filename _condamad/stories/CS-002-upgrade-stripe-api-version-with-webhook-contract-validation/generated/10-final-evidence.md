# Final Evidence - CS-002

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-002-upgrade-stripe-api-version-with-webhook-contract-validation
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/00-story.md`
- Initial `git status --short`: `_condamad/stories/story-status.md` modified; `CS-002` and `CS-003` story directories untracked; pytest artifact directories emitted access warnings.
- Pre-existing dirty files: `_condamad/stories/story-status.md`, `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/`, `_condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/`.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific target map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `backend/app/core/config.py` and `.env.example` default to `2026-04-22.dahlia`; baseline/after evidence persisted. | `pytest -q app/tests/unit/test_stripe_client.py` PASS; runtime settings command with `APP_DISABLE_BACKEND_DOTENV=1` PASS. | PASS | Local `backend/.env` can still override by design. |
| AC2 | `backend/app/infra/stripe/client.py` remains canonical and test asserts `stripe_version=2026-04-22.dahlia`; duplicate constructor removed from `app/jobs/calibration`. | `pytest -q app/tests/unit/test_stripe_client.py` PASS; `rg -n "StripeClient\(" app tests` classified canonical constructor plus guard-test hit. | PASS | No compatibility wrapper added. |
| AC3 | Checkout, portal, invoice preview, subscription upgrade and webhook services kept existing payload shapes. | Unit Stripe billing subset PASS: 61 tests; combined targeted subset PASS: 107 tests. | PASS | No service behavior change besides canonical client ownership cleanup. |
| AC4 | Billing API route contracts unchanged. | Integration Stripe billing subset PASS: 41 tests; combined targeted subset PASS: 107 tests. | PASS | App import/start check also PASS. |
| AC5 | `evidence/stripe-api-version-baseline.md`, `evidence/stripe-api-version-after.md`, and `docs/billing-webhook-local-testing.md` record SDK decision, webhook version expectation and rollback. | Evidence/doc scan for `stripe==14.4.1`, `2026-04-22.dahlia`, and rollback-specific old override PASS with relevant hits. | PASS | Old version remains only as historical/rollback text. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `.env.example` | modified | Update sample Stripe API version. | AC1 |
| `backend/app/core/config.py` | modified | Update runtime default Stripe API version. | AC1 |
| `backend/app/jobs/calibration/__init__.py` | modified | Remove duplicate Stripe SDK client constructor. | AC2 |
| `backend/app/tests/unit/test_stripe_client.py` | modified | Assert configured SDK version, cache behavior, legacy absence and single constructor ownership. | AC2 |
| `docs/billing-webhook-local-testing.md` | modified | Document Dashboard API version expectation and rollback procedure. | AC5 |
| `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/00-story.md` | modified | Mark task/status progress. | AC1-AC5 |
| `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/generated/*.md` | added/modified | Execution capsule, validation plan, traceability and evidence. | AC1-AC5 |
| `_condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/evidence/*.md` | added | Baseline and after upgrade evidence. | AC5 |

## Files deleted

- None.

## Tests added or updated

- `backend/app/tests/unit/test_stripe_client.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Preflight state captured; access warnings for pytest artifact directories. |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.core.config import Settings; import stripe; print(Settings().stripe_api_version); print(getattr(stripe, 'VERSION', getattr(stripe, '__version__', 'unknown')))"` | repo root | PASS | 0 | Baseline captured `2024-12-18.acacia` and SDK `14.4.1`. |
| `pytest -q app/tests/unit/test_stripe_client.py` | `backend/` | FAIL | 1 | First run exposed self-match in new guard; fixed immediately. |
| `pytest -q app/tests/unit/test_stripe_client.py` | `backend/` | PASS | 0 | 5 tests passed. |
| `pytest -q app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_webhook_service.py` | `backend/` | PASS | 0 | 61 tests passed. |
| `pytest -q app/tests/integration/test_stripe_checkout_api.py app/tests/integration/test_stripe_customer_portal_api.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | 41 tests passed. |
| `python -c "from app.core.config import Settings; assert Settings().stripe_api_version == '2026-04-22.dahlia'"` | `backend/` | FAIL | 1 | Local `backend/.env` override still contains old version; not a default failure. |
| `$env:APP_DISABLE_BACKEND_DOTENV='1'; python -c "from app.core.config import Settings; assert Settings().stripe_api_version == '2026-04-22.dahlia'"` | `backend/` | PASS | 0 | Pure runtime default passes. |
| `rg -n "from app\.api\|import app\.api" app\services app\domain app\infra app\core` | `backend/` | PASS | 1 | Zero hits; RG-004/RG-006 boundary preserved. |
| `rg -n "app\.integrations\.stripe_client\|app/integrations/stripe_client.py" app tests ..\docs ..\.env.example` | `backend/` | PASS | 1 | Zero active legacy path hits. |
| `rg -n "2024-12-18\.acacia" app tests ..\.env.example ..\docs ..\_condamad\stories\CS-002-upgrade-stripe-api-version-with-webhook-contract-validation` | `backend/` | PASS | 0 | Hits are story/evidence/rollback historical references only. |
| `ruff check app/infra/stripe/client.py app/core/config.py app/jobs/calibration/__init__.py app/services/billing app/tests/unit/test_stripe_client.py` | `backend/` | PASS | 0 | All checks passed. |
| `ruff format app/core/config.py app/jobs/calibration/__init__.py app/tests/unit/test_stripe_client.py` | `backend/` | PASS | 0 | 1 file reformatted, 2 unchanged. |
| `ruff format --check app/infra/stripe/client.py app/core/config.py app/jobs/calibration/__init__.py app/tests/unit/test_stripe_client.py` | `backend/` | PASS | 0 | 4 files already formatted. |
| `pytest -q app/tests/unit/test_stripe_client.py app/tests/unit/test_stripe_checkout_service.py app/tests/unit/test_stripe_customer_portal_service.py app/tests/unit/test_stripe_webhook_service.py app/tests/integration/test_stripe_checkout_api.py app/tests/integration/test_stripe_customer_portal_api.py app/tests/integration/test_stripe_webhook_api.py` | `backend/` | PASS | 0 | 107 tests passed. |
| `pytest -q` | repo root | PASS | 0 | User rerun after root pytest fixes: 3552 passed, 12 skipped, 34 warnings before warning filter; subsequent warning-targeted subset passed cleanly. |
| `$env:APP_DISABLE_BACKEND_DOTENV='1'; python -c "from app.main import app; assert app.title == 'horoscope-backend'; print(app.title)"` | `backend/` | PASS | 0 | App imports and FastAPI app is constructed. |
| `rg -n "stripe==14\.4\.1\|2026-04-22\.dahlia\|STRIPE_API_VERSION=2024-12-18\.acacia" ..\docs ..\_condamad\stories\CS-002-upgrade-stripe-api-version-with-webhook-contract-validation\evidence` | `backend/` | PASS | 0 | Relevant evidence and docs hits present. |
| `rg -n "StripeClient\(" app tests` | `backend/` | PASS | 0 | Canonical constructor plus guard-test self-reference only. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors; line-ending warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed. |
| `git status --short` | repo root | PASS | 0 | Final worktree status captured with expected story changes and pre-existing entries. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All required checks completed after user rerun and root pytest warning filter fix. | None. | Full suite and targeted checks passed. |

## DRY / No Legacy evidence

- Removed the duplicate `stripe.StripeClient(...)` construction from `backend/app/jobs/calibration/__init__.py`.
- `rg -n "StripeClient\(" app tests` returns the canonical infra constructor plus the guard test self-reference.
- `rg -n "app\.integrations\.stripe_client|app/integrations/stripe_client.py" app tests ../docs ../.env.example` returns zero active hits.
- Old version `2024-12-18.acacia` remains only in story/evidence/rollback documentation, not in runtime defaults or tests.
- `RG-004`/`RG-006` scan for `app.api` imports from services/domain/infra/core returns zero hits.

## Diff review

- `git diff --stat`: story-related backend/config/docs files only, plus pre-existing `_condamad/stories/story-status.md` not touched by this implementation.
- `git diff --check`: PASS with line-ending warnings only.
- Relevant hunks reviewed for `.env.example`, `backend/app/core/config.py`, `backend/app/jobs/calibration/__init__.py`, `backend/app/tests/unit/test_stripe_client.py`, and `docs/billing-webhook-local-testing.md`.

## Final worktree status

```text
 M .env.example
 M _condamad/stories/story-status.md
 M backend/app/core/config.py
 M backend/app/jobs/calibration/__init__.py
 M backend/app/tests/unit/test_stripe_client.py
 M docs/billing-webhook-local-testing.md
?? _condamad/stories/CS-002-upgrade-stripe-api-version-with-webhook-contract-validation/
?? _condamad/stories/CS-003-centralize-supported-stripe-webhook-event-ownership/
```

`_condamad/stories/story-status.md` and `CS-003` were already dirty/untracked at preflight and were not modified by this implementation.

## Remaining risks

- Live Stripe Dashboard compatibility is not proven locally; the story explicitly excludes production Dashboard migration.
- Local `backend/.env` can override the default. The default was validated with backend dotenv loading disabled.

## Suggested reviewer focus

- Confirm that removing the unused duplicate Stripe client constructor from `app.jobs.calibration` is acceptable.
- Review the webhook version/rollback documentation for operational accuracy.
- Confirm the full-suite pass is acceptable as user-provided final validation evidence.
