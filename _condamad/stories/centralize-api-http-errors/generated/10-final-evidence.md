# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: centralize-api-http-errors
- Source story: `_condamad/stories/centralize-api-http-errors/00-story.md`
- Capsule path: `_condamad/stories/centralize-api-http-errors/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `M backend/horoscope.db`, untracked capsule directory.
- AGENTS.md considered: `AGENTS.md`
- Capsule generated: yes, via `condamad_prepare.py`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated after implementation. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Updated commands recorded here. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated guardrails used with scans. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Added `backend/app/core/exceptions.py`; auth dependency errors now inherit `ApplicationError`. | `pytest -q app/tests/unit/test_api_error_contracts.py ...` passed. | PASS | No FastAPI dependency in core exception. |
| AC2 | Added `backend/app/api/errors/catalog.py` and contract tests. | `test_http_error_catalog_is_unique_and_valid` passed. | PASS | Codes unique, statuses valid, messages non-empty. |
| AC3 | Added architecture guard with explicit HTTPException allowlist. | `test_api_http_exception_usage_is_allowlisted` passed. | PASS_WITH_LIMITATIONS | Some route files still use `HTTPException` and are documented in allowlist. |
| AC4 | Removed route/local service `_error_response` and `_create_error_response` names; helpers now `_raise_error`. | Negative `rg` scan returned no hits. | PASS | No local envelope builders remain. |
| AC5 | Migrated services from `api_error_response`/HTTP responses to raising `ApplicationError`. | Negative service scan returned no `JSONResponse`, `HTTPException`, `api_error_response`, `_error_response`. | PASS | Services still import some API schemas/dependency types outside this error construction scope. |
| AC6 | `ApplicationError` fallback handled centrally in `app.api.errors.handlers`. | Unit and integration fallback tests passed. | PASS | No unmapped stacktrace leak for `ApplicationError`. |
| AC7 | `build_error_response` preserves `error.code/message/details/request_id`. | Unit and integration response tests passed. | PASS | Request id resolved from request. |
| AC8 | OpenAPI smoke verifies representative existing paths after package migration. | `test_openapi_paths_are_still_available_after_error_package_migration` passed. | PASS_WITH_LIMITATIONS | Representative path guard, not full pre/post snapshot. |
| AC9 | Lint, targeted tests, scans run in activated venv. | `ruff check .` passed; targeted pytest passed; full pytest timed out. | PASS_WITH_LIMITATIONS | Full regression did not finish within 10 minutes. |

## Files changed

See `git diff --stat` for full list. Main categories:

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/core/exceptions.py` | added | ApplicationError base outside API. | AC1 |
| `backend/app/api/errors/*` | added | Canonical contracts, catalog, handlers, raising helper. | AC2, AC7 |
| `backend/app/api/v1/errors.py` | deleted | Remove historical facade. | AC4, AC5 |
| `backend/app/main.py` | modified | Register central ApplicationError handler and reuse response builder. | AC6, AC7 |
| `backend/app/services/**/*.py` | modified | Raise `ApplicationError` instead of returning HTTP responses. | AC5 |
| `backend/app/api/v1/routers/**/*.py` | modified | Rename imported service helper from `_error_response` to `_raise_error`. | AC4 |
| `backend/app/tests/unit/test_api_error_contracts.py` | modified | Contract tests for new package. | AC1, AC2, AC7 |
| `backend/app/tests/unit/test_api_error_architecture.py` | added | No-legacy/import guards. | AC3, AC4, AC5 |
| `backend/app/tests/integration/test_api_error_responses.py` | added | Integration envelope and OpenAPI smoke tests. | AC7, AC8 |
| `_condamad/stories/centralize-api-http-errors/error-audit.md` | added | Migration/removal audit. | AC6 |

## Files deleted

| File | Reason |
|---|---|
| `backend/app/api/v1/errors.py` | Replaced by canonical `backend/app/api/errors/` package; no re-export facade kept. |

## Tests added or updated

- `backend/app/tests/unit/test_api_error_contracts.py`
- `backend/app/tests/unit/test_api_error_architecture.py`
- `backend/app/tests/integration/test_api_error_responses.py`
- `backend/app/tests/unit/test_api_router_architecture.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\\.venv\\Scripts\\Activate.ps1; python .agents\\skills\\condamad-dev-story\\scripts\\condamad_prepare.py _condamad\\stories\\centralize-api-http-errors\\00-story.md --root . --story-key centralize-api-http-errors --with-optional` | repo root | PASS | 0 | Capsule generated. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_error_responses.py` | repo root | PASS | 0 | 54 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/integration/test_api_error_responses.py` | repo root | PASS | 0 | 2 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` | repo root | PASS | 0 | Formatting applied, final run unchanged. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check . --fix` | repo root | PASS | 0 | Import sorting fixed. |
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `rg -n "def _error_response|def _create_error_response|api_error_response\\(" backend/app/api/v1/routers backend/app/api/dependencies backend/app/services` | repo root | PASS | 1 | No forbidden helper hits. |
| `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\\(" backend/app/services` | repo root | PASS | 1 | No service HTTP response construction hits. |
| `Test-Path backend/app/api/v1/errors.py` | repo root | PASS | 0 | Returned `False`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | yes | Timed out after 604 seconds with no completion output. | Full regression may still contain unrelated or slow-suite failures. | Targeted unit/integration tests, architecture tests, lint, scans, and OpenAPI smoke passed. |

## DRY / No Legacy evidence

| Pattern | Classification | Action | Status |
|---|---|---|---|
| `backend/app/api/v1/errors.py` | active legacy removed | Deleted file. | PASS |
| `app.api.v1.errors` | test guard expected hit | Only appears in tests that block reintroduction. | PASS |
| `api_error_response(` | active legacy removed | Removed from app code. | PASS |
| `_error_response` / `_create_error_response` | active legacy removed | Renamed service helpers to `_raise_error`; route imports updated. | PASS |
| `JSONResponse` in services | active legacy removed | Services raise `ApplicationError` instead. | PASS |

## Diff review

- `git diff --stat` reviewed.
- `git diff --check` passed.
- `backend/horoscope.db` was already dirty at preflight and remains untouched intentionally.
- Broad route diffs are mechanical `_error_response` -> `_raise_error` import/call renames.

## Final worktree status

Recorded with `git status --short`: expected story changes plus pre-existing `M backend/horoscope.db`; untracked capsule and new package/test files.

## Remaining risks

- Full `pytest -q` timed out after 10 minutes.
- Some route files still use `HTTPException`; these are explicit allowlist entries in `test_api_error_architecture.py` and should be reviewer focus for follow-up migration.
- Some service modules still import API schemas/dependency DTOs unrelated to HTTP response construction; this story removed HTTP response construction, not all historical schema coupling.

## Suggested reviewer focus

- Confirm the `_raise_error` service helper pattern is acceptable as the intermediate service-boundary shape.
- Review the `HTTPException` allowlist and decide whether to schedule a follow-up for full route migration.
- Review the deleted `app.api.v1.errors` path and confirm no external first-party consumer needs migration.

## Post-review correction addendum

- Blocking review findings from `generated/11-code-review.md` were corrected.
- `ApplicationError` no longer carries `status_code`; HTTP status resolution now lives in `backend/app/api/errors/catalog.py`.
- Remaining `HTTPException` usages under `backend/app/api` were migrated to centralized API helpers.
- Service-layer `status_code` / `error.status_code` usage was removed from `backend/app/services`.
- OpenAPI integration coverage now verifies all registered route path/method pairs and guards against duplicate canonical error schemas.
- `backend/horoscope.db` was restored out of the diff.
- Re-validation after fixes:
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` -> PASS.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` -> PASS.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/integration/test_api_error_responses.py` -> PASS, `16 passed`.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` -> timed out after about 10 minutes; not counted as passed.

## Regression correction addendum

- Corrected broad integration regressions reported after the first review fix:
  - `ApplicationError` is no longer frozen, so native exception traceback assignment works.
  - API-specific errors temporarily exposed `status_code` compatibility while the core exception stayed HTTP-agnostic; the strict cleanup below removes that compatibility again.
  - Central status resolution now covers observed domain codes for auth, B2B, natal, LLM admin, ops persona, privacy evidence, Stripe, webhook, and prediction flows.
  - Legacy `detail` is emitted only for converted historical HTTP errors while the canonical `error` envelope remains present.
  - Route helpers that still receive historical status arguments preserve their intended HTTP status through the central handler.
- Additional validation after these fixes:
  - Auth/B2B representative group -> PASS, `30 passed`.
  - Geocoding/daily prediction group -> PASS, `60 passed`.
  - Admin LLM catalog/email group -> PASS, `38 passed`.
  - Admin content/config/persona/Stripe action group -> PASS, `17 passed`.
  - Natal calculate/prepare/interpretation/history group -> PASS, `55 passed`.
  - Ops/persona/privacy/Stripe representative groups -> PASS, `87 passed` and `69 passed`.
  - Final story tests -> PASS, `16 passed`.
  - Final `ruff format .`, `ruff check .`, scans and `git diff --check` -> PASS.

## Strict status_code cleanup addendum

- `ApiHttpError.status_code` compatibility was removed; API-specific errors now expose only `http_status_code`.
- Auth and B2B exception handlers that previously read `error.status_code` now read `error.http_status_code`, so endpoint-specific auth semantics are preserved without the legacy alias.
- Added regression coverage:
  - `test_api_http_error_does_not_expose_legacy_status_code_property`.
  - `test_api_handlers_do_not_read_legacy_error_status_code`.
- Re-validation:
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format ...` -> PASS.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` -> PASS.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/unit/test_require_admin_user.py app/tests/integration/test_auth_api.py app/tests/integration/test_b2b_astrology_api.py app/tests/integration/test_b2b_billing_api.py app/tests/integration/test_b2b_usage_api.py` -> PASS, `53 passed`.
  - `rg -n "error\\.status_code|def status_code" backend/app/api backend/app/core backend/app/tests` -> only expected test guard / unrelated LLM compactor test hits.

## Full-suite regression follow-up

- Corrected the 8 remaining failures from the full `pytest -q` run by extending central status resolution for observed codes:
  - `b2b_api_access_denied`, `b2b_api_quota_exceeded`, `b2b_no_binding`.
  - `weekly_generation_failed`.
  - `enterprise_account_inactive` for non-auth service responses.
  - `alert_event_not_retryable`.
  - `token_expired`, `invalid_token_type`.
- Added `test_resolve_application_error_status_covers_regression_codes`.
- Re-validation:
  - The 8 failing tests reported from the full run -> PASS, `8 passed`.
  - Expanded regression group covering API error contracts, architecture, auth, B2B, enterprise credentials, alert retry, and birth profile -> PASS, `104 passed`.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` -> PASS.

## Post-full-suite artifact update

- User reported the repository-wide `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` now passes.
- Additional scans were run to verify service/route alignment with the implemented API error management:
  - `rg -n "status_code" backend/app/services` -> PASS, no hit.
  - `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services` -> PASS, no hit.
  - `rg -n "from app\.api\.v1\.errors|app\.api\.v1\.errors" backend/app backend/tests` -> PASS except expected architecture guard references.
  - `rg -n "HTTPException" backend/app/api` -> PASS, no hit.
  - `rg -n "error\.status_code|def status_code" backend/app/api backend/app/core backend/app/tests` -> PASS except expected test guard and unrelated LLM compactor test.
  - `rg -n "JSONResponse\(" backend/app/api/v1/routers` -> identified route-local error envelopes that were later migrated in the AC3/AC7/AC9 closure addendum.
- Route-local `JSONResponse` findings are documented in `_condamad/stories/centralize-api-http-errors/error-audit.md`.
- Conclusion:
  - Services are aligned with the story's error-boundary requirement.
  - Routes no longer use `HTTPException` or the deleted legacy error module.
  - Routes needed one final alignment pass because multiple route files still built local error envelopes via `JSONResponse`.
  - Current tests can pass while this route-level debt remains; architecture guards should be extended in a follow-up migration if strict completion is required.

## AC3/AC7/AC9 Closure Addendum

- Migrated the remaining route-local `JSONResponse(content={"error": ...})` envelopes to the central `build_error_response` helper in:
  - `backend/app/api/v1/routers/public/auth.py`
  - `backend/app/api/v1/routers/public/chat.py`
  - `backend/app/api/v1/routers/public/users.py`
  - `backend/app/api/v1/routers/public/consultations.py`
  - `backend/app/api/v1/routers/public/entitlements.py`
  - `backend/app/api/v1/routers/public/guidance.py`
  - `backend/app/api/v1/routers/public/help.py`
  - `backend/app/api/v1/routers/public/ephemeris.py`
  - `backend/app/api/v1/routers/admin/pdf_templates.py`
- Added architecture guard `test_api_routes_do_not_build_error_envelopes_with_json_response`.
- Preserved non-error/special `JSONResponse` uses:
  - ephemeris status responses.
  - idempotent `200` suppression-rule response.
- Re-validation:
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` -> PASS.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_error_responses.py app/tests/integration/test_auth_api.py app/tests/integration/test_chat_api.py app/tests/integration/test_user_birth_profile_api.py app/tests/integration/test_user_natal_chart_api.py app/tests/integration/test_guidance_api.py app/tests/integration/test_consultations_router.py app/tests/integration/test_entitlements_me.py app/tests/integration/test_entitlements_plans.py tests/integration/test_help_api.py` -> PASS, `215 passed`.
  - `rg -n "HTTPException" backend/app/api` -> PASS, no hit.
  - `rg -n "status_code" backend/app/services` -> PASS, no hit.
  - `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services` -> PASS, no hit.
  - `rg -n -F '"error": {' backend/app/api/v1/routers` -> PASS, no hit after docstring cleanup.
  - `git diff --check` -> PASS, line-ending warnings only.
- Conclusion:
  - AC3: no business `HTTPException` path remains under `backend/app/api`.
  - AC7: route-local error envelopes now use the central builder or handler path.
  - AC9: lint, targeted tests, architecture guard, and scans pass without the previous limitation.

## Docstring Cleanup Addendum

- Removed misleading literal error-envelope examples from `backend/app/api/v1/routers/public/ephemeris.py`.
- Re-validation:
  - `rg -n -F '"error": {' backend/app/api/v1/routers backend/app/api backend/app/core backend/app/services` -> PASS, no hit.
  - `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check app/api/v1/routers/public/ephemeris.py app/tests/unit/test_api_error_architecture.py` -> PASS.
- User reported the full repository test suite passes after these final cleanups.
