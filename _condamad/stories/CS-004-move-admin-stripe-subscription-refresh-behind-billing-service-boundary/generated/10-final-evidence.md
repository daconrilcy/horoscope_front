# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary
- Source story: `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/00-story.md`
- Capsule path: `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/00-story.md`
- Initial `git status --short`: `_condamad/stories/story-status.md` modified; CS-004 and CS-005 capsule directories untracked.
- Pre-existing dirty files: `_condamad/stories/story-status.md`, `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/`, `_condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/`.
- AGENTS.md files considered: repository `AGENTS.md` from prompt and workspace root.
- Capsule generated: yes, generated files completed under this capsule.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Story-specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs mapped and passed. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific target map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific forbidden paths. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `users.py` still exposes `refresh_subscription` and returns `{"status": "success"}` after service call. | Integration tests passed; OpenAPI path assertion passed. | PASS | Route path and method preserved. |
| AC2 | `users.py` no longer imports `get_stripe_client` or calls `stripe_client.subscriptions.retrieve`. | AST guard passed; direct Stripe router scan returned zero hits. | PASS | No route-owned Stripe SDK path remains. |
| AC3 | `StripeBillingProfileService.force_admin_subscription_refresh` owns Stripe retrieve, event payload, profile sync and audit. | Billing service unit tests passed. | PASS | No new service namespace added. |
| AC4 | `StripeBillingAdminRefreshError` maps to 400/503 in the route; generic errors still map to 500 with message. | Admin integration tests for success, missing subscription and missing client passed. | PASS | Error envelope remains centralized through `raise_api_error`. |
| AC5 | Billing service uses plain exceptions and imports no FastAPI/API module. | Service architecture guard passed; service/infra dependency scan returned zero hits. | PASS | `RG-004`, `RG-005`, `RG-006` preserved. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/api/v1/routers/admin/users.py` | modified | Thin route to service call and service error translation. | AC1, AC2, AC4 |
| `backend/app/services/billing/stripe_billing_profile_service.py` | modified | Add billing-owned admin refresh use case and application error. | AC3, AC5 |
| `backend/app/tests/integration/test_admin_stripe_actions_api.py` | modified | Patch service boundary and cover error mappings. | AC1, AC4 |
| `backend/app/tests/unit/test_stripe_billing_profile_service.py` | modified | Cover service-owned refresh behavior and service errors. | AC3 |
| `backend/app/tests/unit/test_api_router_architecture.py` | modified | Add anti-reintroduction guard for direct Stripe SDK in API routers. | AC2, AC5 |
| `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md` | modified | Keep exact SQL-debt line metadata in sync after `users.py` line changes. | AC5 |
| `_condamad/stories/story-status.md` | modified | Mark CS-004 ready-to-review while preserving existing rows. | All |
| `_condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/**` | generated/modified | Capsule, baseline, after evidence and final evidence. | All |

## Files deleted

| File | Reason |
|---|---|
| None | No deletion required. |

## Tests added or updated

- Added service unit tests for admin refresh success, missing subscription and missing Stripe client.
- Added integration tests for admin refresh missing subscription and missing Stripe client.
- Added architecture guard `test_api_routers_do_not_call_stripe_sdk_directly`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; path='/v1/admin/users/{user_id}/refresh-subscription'; route=app.openapi()['paths'].get(path); print(path in app.openapi()['paths']); print(sorted(route.keys()) if route else [])"` | repo root | PASS | 0 | Baseline route present with `post`. |
| `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" backend/app/api/v1/routers` | repo root | PASS | 0 | Baseline found route-owned Stripe calls before implementation. |
| `ruff format app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | PASS | 0 | Five files formatted. |
| `ruff check --fix app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | PASS | 0 | Import ordering fixed. |
| `ruff check app/api/v1/routers/admin/users.py app/services/billing/stripe_billing_profile_service.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py -k "admin_stripe_actions_api or stripe_billing_profile_service or stripe_sdk or service_modules_do_not_import_fastapi_or_wildcards"` | `backend/` | FAIL then PASS | 1 then 0 | First run found an invalid unit-test FK fixture; rerun passed `20 passed, 53 deselected`. |
| `pytest -q app/tests/integration/test_admin_stripe_actions_api.py` | `backend/` | PASS | 0 | `6 passed`. |
| `pytest -q app/tests/unit/test_stripe_billing_profile_service.py` | `backend/` | PASS | 0 | `12 passed`. |
| `pytest -q app/tests/unit/test_api_router_architecture.py -k "stripe_sdk or service_modules_do_not_import_fastapi_or_wildcards"` | `backend/` | PASS | 0 | `2 passed, 53 deselected`. |
| `python -c "from app.main import app; assert '/v1/admin/users/{user_id}/refresh-subscription' in app.openapi()['paths']"` | `backend/` | PASS | 0 | OpenAPI path remains present. |
| `rg -n "get_stripe_client\(|stripe_client\.|client\.subscriptions" app/api/v1/routers` | `backend/` | PASS | 1 | Zero active hits after implementation. |
| `rg -n "app\.api\.v1\.routers\.admin\.users\.get_stripe_client" app/tests` | `backend/` | PASS | 1 | Zero old patch-target hits. |
| `rg -n "from app\.api|import app\.api|HTTPException|JSONResponse|fastapi" app/services/billing app/infra/stripe -g "*.py"` | `backend/` | PASS | 1 | Zero forbidden service/infra dependency hits. |
| `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` | `backend/` | PASS | 0 | Exact SQL allowlist guard passes after line metadata update. |
| `pytest -q app/tests/integration/test_admin_stripe_actions_api.py app/tests/unit/test_stripe_billing_profile_service.py app/tests/unit/test_api_router_architecture.py` | `backend/` | FAIL then PASS | 1 then 0 | First run exposed shifted SQL allowlist metadata; final rerun passed `73 passed`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `python .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary --final` | repo root | PASS | 0 | CONDAMAD validation passed after venv activation. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full backend `pytest -q` | no | Story validation targeted the changed route, service and architecture guard surfaces. | Broader unrelated regressions outside touched surface may remain undetected. | Full targeted bundle passed `73 passed`; ruff and scans passed. |
| Starting a persistent local dev server | no | This backend story was validated through app import/OpenAPI and tests; no long-running server was needed. | Runtime server configuration outside import path not revalidated. | Exact command to run locally remains `.\.venv\Scripts\Activate.ps1; cd backend; uvicorn app.main:app --reload`. |

## DRY / No Legacy evidence

| Pattern | File or scope | Classification | Action | Status |
|---|---|---|---|---|
| `get_stripe_client\(|stripe_client\.|client\.subscriptions` | `app/api/v1/routers` | active_legacy_removed | Removed route-owned Stripe client usage; scan zero hits. | PASS |
| `app.api.v1.routers.admin.users.get_stripe_client` | `app/tests` | active_legacy_removed | Tests patch service boundary instead. | PASS |
| `from app.api|import app.api|HTTPException|JSONResponse|fastapi` | `app/services/billing app/infra/stripe` | false_positive_absent | Scan zero hits. | PASS |
| Existing Stripe SDK usage in billing services | `app/services/billing` | allowed_canonical_owner | Story allowlist permits billing-owned Stripe use cases. | PASS |

## Diff review

- `git diff --stat` inspected.
- `git diff --check` passed with CRLF warnings only.
- Relevant code/test hunks inspected.
- No frontend, dependency manifest or unrelated admin endpoint behavior changed.
- SQL allowlist metadata update is line-number maintenance caused by this story's `users.py` edits; no new SQL debt was added.

## Final worktree status

```text
 M _condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md
 M _condamad/stories/story-status.md
 M backend/app/api/v1/routers/admin/users.py
 M backend/app/services/billing/stripe_billing_profile_service.py
 M backend/app/tests/integration/test_admin_stripe_actions_api.py
 M backend/app/tests/unit/test_api_router_architecture.py
 M backend/app/tests/unit/test_stripe_billing_profile_service.py
?? _condamad/stories/CS-004-move-admin-stripe-subscription-refresh-behind-billing-service-boundary/
?? _condamad/stories/CS-005-define-central-stripe-timeout-and-retry-policy/
```

`CS-005` was already untracked before this implementation and was not modified for this story.

## Remaining risks

- Full backend test suite was not run; targeted backend bundle and scans passed.

## Suggested reviewer focus

- Review that `StripeBillingProfileService.force_admin_subscription_refresh` is the right canonical owner for this admin billing use case.
- Review the route error translation for status/message parity.
- Review the new Stripe SDK router guard and the SQL allowlist metadata update for `admin/users.py`.
