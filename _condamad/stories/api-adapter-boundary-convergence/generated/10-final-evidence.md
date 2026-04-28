# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: api-adapter-boundary-convergence
- Source story: `_condamad/stories/api-adapter-boundary-convergence/00-story.md`
- Capsule path: `_condamad/stories/api-adapter-boundary-convergence`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/stories/api-adapter-boundary-convergence/` plus access warnings for protected pytest temp directories.
- Pre-existing dirty files: untracked story capsule directory.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: yes, required generated files were missing.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Human story source present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated then refined by execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC10 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map updated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands and scans listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Former `app.api.v1.schemas.routers` contracts moved out of API. | Architecture guard and zero-hit scan. | PASS | |
| AC2 | Non-API imports moved to `app.core.auth_context`, `app.core.api_constants`, `app.services.api_contracts`. | Guard and zero-hit scans for `app.api` imports. | PASS | |
| AC3 | Canonical contract owner documented as `app.services.api_contracts`. | Old schema import scan returns zero hits. | PASS | |
| AC4 | Added `backend/app/api/v1/routers/registry.py`; `main.py` calls `include_api_v1_routers(app)`. | Router architecture tests pass. | PASS | |
| AC5 | Removed `raise_http_error`, `legacy_detail`, and `content["detail"]` active paths; remaining tests now assert the canonical `error` envelope. | Error unit/integration tests pass; scan hit only expected guard text. | PASS | |
| AC6 | `/api/email/unsubscribe` kept and classified external-active. | Non-v1 route guard passes; audit complete. | PASS | |
| AC7 | Routeurs changed for imports and error calls only. | Diff review and targeted tests. | PASS | |
| AC8 | Guards added for contracts, non-API imports, registry, legacy errors. | `pytest -q app/tests/unit/test_api_router_architecture.py` passes. | PASS | |
| AC9 | OpenAPI smoke succeeds with 192 paths. | OpenAPI command passes. | PASS_WITH_LIMITATIONS | Before snapshot was not captured before editing. |
| AC10 | Ruff, targeted tests, and the user-run full backend suite pass. | Targeted command passed locally; user reported global suite green after fixes. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/core/auth_context.py` | added | Canonical auth identity contracts outside API. | AC2, AC3 |
| `backend/app/core/api_constants.py` | added | Canonical shared constants outside API. | AC2, AC3 |
| `backend/app/services/api_contracts/**` | added/moved | Canonical Pydantic contracts consumed by API and services. | AC1, AC2, AC3 |
| `backend/app/api/v1/schemas/routers/**`, `backend/app/api/v1/schemas/common.py` | deleted | Remove API-owned contract tree consumed by services. | AC1, AC3 |
| `backend/app/api/v1/schemas/__init__.py` | deleted | Remove residual empty legacy schema package after contract migration. | AC1, AC3, AC8 |
| `backend/app/api/v1/routers/registry.py` | added | Single API v1 router registry. | AC4 |
| `backend/app/main.py` | modified | Consume router registry. | AC4, AC9 |
| `backend/app/api/errors/*` | modified | Remove legacy HTTP error surfaces. | AC5 |
| `backend/app/api/v1/routers/**/*.py` | modified | Import canonical contracts and use `raise_api_error`. | AC3, AC5, AC7 |
| `backend/app/services/**/*.py` | modified | Replace `app.api` imports. | AC2, AC3 |
| `backend/app/tests/**`, `backend/tests/integration/test_llm_release.py` | modified | Update imports and architecture/error guards. | AC8, AC10 |
| `_condamad/stories/api-adapter-boundary-convergence/**` | added/modified | Capsule, audit, final evidence. | AC1-AC10 |

## Files deleted

- `backend/app/api/v1/schemas/common.py`
- `backend/app/api/v1/schemas/routers/**`
- `backend/app/api/v1/schemas/__init__.py`

## Tests added or updated

- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- Existing tests updated for `app.services.api_contracts` imports.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; python .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` | repo root | PASS | 0 | Capsule generated. |
| `ruff format .` | `backend/` | PASS | 0 | Final run: 1232 files unchanged. |
| `ruff check . --fix` | `backend/` | PASS | 0 | Import ordering fixed. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py` | `backend/` | PASS | 0 | 62 tests passed. |
| `python -c "from app.main import app; schema = app.openapi(); assert schema['paths']"` | `backend/` | PASS | 0 | OpenAPI smoke passed. |
| `python -c "from app.main import app; import json; print(json.dumps(sorted(app.openapi()['paths'].keys()), indent=2))"` | `backend/` | PASS | 0 | 192 paths emitted. |
| `rg -n "from fastapi\|import fastapi\|APIRouter\|JSONResponse\|Depends\|Request\|Query\|Body" app/api/v1/schemas` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "from app\.api\.v1\.schemas\|import app\.api\.v1\.schemas" app tests` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "from app\.api\.dependencies\|from app\.api\.errors\|import app\.api" app/services app/domain app/infra app/core` | `backend/` | PASS | 1 | Zero hits. |
| `rg -n "raise_http_error\|legacy_detail\|content\[""detail""\]" app/api app/tests tests` | `backend/` | PASS | 0 | Only architecture guard expected hit. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; Git emitted line-ending warnings. |
| `ruff format app/services/api_contracts ...; ruff check app/services/api_contracts ...; pytest -q app/tests/unit/test_api_router_architecture.py app/tests/unit/test_api_error_contracts.py app/tests/integration/test_api_error_responses.py app/tests/integration/test_admin_stripe_actions_api.py app/tests/integration/test_daily_prediction_api.py app/tests/unit/test_daily_prediction_guardrails.py tests/integration/test_email_unsubscribe.py` | `backend/` | PASS | 0 | Post-review fixes validated: 103 tests passed. |
| `pytest -q` | `backend/` | PASS | user-run | User reported the full backend suite green after post-review fixes. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Pre-change OpenAPI snapshot | yes | Not captured before implementation began. | Cannot prove exact path diff from before state in evidence. | Post-change OpenAPI smoke and registry tests pass; `/api/email/unsubscribe` still present. |
| `pytest -q` initial implementation run | historical | Timed out after 10 minutes before post-review fixes. | Superseded by user-reported full-suite PASS after fixes. | Post-review targeted tests passed locally; user reported global suite green. |

## DRY / No Legacy evidence

- No active `app.api.v1.schemas` imports remain in backend app/tests.
- The residual `backend/app/api/v1/schemas` package is deleted and guarded by `test_api_v1_schemas_package_is_removed`.
- Non-API layers have no direct `app.api` imports by scan and AST guard.
- Legacy error helper symbols are removed from active API code.
- Router registration is centralized in `app.api.v1.routers.registry`.
- `/api/email/unsubscribe` is retained only as a classified external-active route.

## Diff review

- `git diff --stat` shows broad but scoped backend API/services/test changes plus CONDAMAD evidence.
- `git diff --check` passed with line-ending warnings only.
- No frontend files changed.

## Final worktree status

- Final `git status --short` shows expected backend modifications, deleted old schema files, new canonical modules, and the untracked CONDAMAD capsule.
- Git status also reports permission warnings for existing pytest temp directories.

## Remaining risks

- The pre-change OpenAPI snapshot was missed; reviewer should compare route list carefully if needed.
- Moving API contracts to `app.services.api_contracts` is broad and should be reviewed for package ownership naming in future architecture cleanup if needed.

## Suggested reviewer focus

- Confirm `app.services.api_contracts` is acceptable as the canonical owner for shared API/service DTOs.
- Review router registry completeness and future route-addition workflow.
- Review error payload change: top-level `detail` is removed from canonical API errors.
