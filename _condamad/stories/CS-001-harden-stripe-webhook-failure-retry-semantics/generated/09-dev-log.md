# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty `_condamad/stories/story-status.md`; pre-existing untracked `CS-001`, `CS-002`, `CS-003` story folders.
- Applicable AGENTS.md: repository root `AGENTS.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` read; `RG-004`, `RG-005`, `RG-006`, `RG-024` applied.

## Search evidence

- `rg -n "failed_internal|JSONResponse|HTTPException|from app\.api|import app\.api" ...` identified the old HTTP 200 `failed_internal` assertions and service outcome.
- `rg --files backend\app\tests backend\tests | rg "api.*boundary|adapter|boundary"` found existing architecture guards under `test_api_error_architecture.py` and `test_api_router_architecture.py`.

## Implementation notes

- Baseline test confirmed HTTP 200 + `failed_internal` before runtime edit.
- Route now maps signed `failed_internal` outcome to centralized `stripe_webhook_processing_failed` HTTP 500 after committing the failed idempotency row.
- Unexpected signed handler exceptions now also return retryable HTTP 500 instead of silent HTTP 200.
- Exact SQL-boundary allowlist was realigned mechanically for touched `public/billing.py` line numbers; no new SQL debt was added.
- Existing Stripe legacy guard was corrected to treat missing parent package as expected absence.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pytest -q app/tests/integration/test_stripe_webhook_api.py::test_webhook_business_failure_persists_failed_and_retry_is_accepted` | PASS | Baseline: 1 passed before runtime edit. |
| `pytest -q app/tests/unit/test_stripe_webhook_service.py app/tests/unit/test_stripe_webhook_idempotency_service.py app/tests/integration/test_stripe_webhook_api.py` | PASS | 36 passed. |
| `pytest -q app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package` | PASS | 9 passed before SQL allowlist realignment; 10 passed with SQL guard included after realignment. |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package` | PASS | 10 passed. |
| `pytest -q app/tests/unit/test_stripe_client.py::test_legacy_integrations_stripe_client_module_is_absent` | PASS | 1 passed after guard fix. |
| `ruff check .` | PASS | Full backend lint. |
| `ruff format --check ...` | PASS | 7 touched Python files already formatted after targeted formatting. |
| `pytest -q` | PASS | 3550 passed, 12 skipped. |

## Issues encountered

- The CONDAMAD prepare helper normalized story key casing on Windows; the story capsule was restored and regenerated in the requested folder.
- The first full `pytest -q` run failed on exact SQL allowlist line drift and on a brittle Stripe legacy guard; both were corrected and the full suite then passed.

## Decisions made

- Use HTTP 500 for signed processing failures because the central error catalog resolves unknown application error codes to 500 and the story allows 500 or 503.
- Keep `failed_internal` as an internal service outcome but forbid it as HTTP 200 response.

## Final `git status --short`

- Recorded in `generated/10-final-evidence.md`.
