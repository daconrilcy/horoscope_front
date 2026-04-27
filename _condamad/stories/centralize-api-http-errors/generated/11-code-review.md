# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/centralize-api-http-errors/00-story.md`
- Review pass: AC3/AC7/AC9 closure
- Verdict: `PASS`

## Findings status

| Finding | Status | Evidence |
|---|---|---|
| CR-1 business `HTTPException` paths bypass envelope | Fixed | `rg -n "HTTPException" backend/app/api` returns no hits. |
| CR-2 services encode HTTP status decisions | Fixed | `ApplicationError` no longer has `status_code`; `rg -n "status_code\|error\.status_code" backend/app/services` returns no hits. |
| CR-3 services depend on API error construction | Fixed for error scope | Services no longer import/use legacy error helpers, `JSONResponse`, or `HTTPException`. Existing API schema/dependency imports remain outside HTTP error construction scope. |
| CR-4 OpenAPI validation covers generated contract | Fixed | Integration test checks every registered route path/method, every declared error status, `ErrorEnvelope` `$ref`, and no duplicate canonical error schemas. |
| CR-5 local SQLite artifact dirty | Fixed | `backend/horoscope.db` was restored out of the diff. |
| CR-6 route-local `JSONResponse` error envelopes remain | Fixed | Route-local `JSONResponse(content={"error": ...})` calls were migrated to `build_error_response`; new architecture guard blocks reintroduction. |

## Validation audit

Commands run by reviewer/implementer after fixes:

- `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` -> pass.
- `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` -> pass.
- `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/integration/test_api_error_responses.py` -> pass, `16 passed`.
- `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/integration/test_api_error_responses.py` -> pass, `4 passed` after AC8 strengthening.
- `rg -n "from app\\.api\\.v1\\.errors|app\\.api\\.v1\\.errors" backend/app backend/tests` -> only architecture tests that guard deletion.
- `rg -n "def _error_response|def _create_error_response|api_error_response\\(" backend/app/api/v1/routers backend/app/api/dependencies backend/app/services` -> no hits.
- `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\\(" backend/app/services` -> no hits.
- `rg -n "HTTPException" backend/app/api` -> no hits.
- `rg -n -F '"error": {' backend/app/api/v1/routers backend/app/api backend/app/core backend/app/services` -> no hit after docstring cleanup.
- `rg -n "JSONResponse\\(" backend/app/api/v1/routers` -> only non-error/special JSON responses remain.
- `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_error_responses.py app/tests/integration/test_auth_api.py app/tests/integration/test_chat_api.py app/tests/integration/test_user_birth_profile_api.py app/tests/integration/test_user_natal_chart_api.py app/tests/integration/test_guidance_api.py app/tests/integration/test_consultations_router.py app/tests/integration/test_entitlements_me.py app/tests/integration/test_entitlements_plans.py tests/integration/test_help_api.py` -> pass, `215 passed`.
- `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check app/api/v1/routers/public/ephemeris.py app/tests/unit/test_api_error_architecture.py` -> pass after docstring cleanup.
- User-reported repository-wide `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` -> pass after previous regression fixes.
- `Test-Path backend/app/api/v1/errors.py` -> `False`.
- `git diff --check` -> pass, line-ending warnings only.

## Remaining limitation

- Full-regression validation is now user-reported as passing, but not rerun by this reviewer pass.
- No AC3/AC7/AC8/AC9 limitation remains in this review pass.

## Verdict

`PASS`: AC3, AC7, AC8 and AC9 are covered without the previous limitations. Full repository pytest is user-reported green; this pass reran lint plus the targeted architecture/contract/integration group with `215 passed`, and the strengthened OpenAPI AC8 test passes with `4 passed`.
